from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "scripts" / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from memory_framework import FamilyContext, create_sidecar_db, query_sidecar, validate_family  # type: ignore


class MemoryFrameworkTests(unittest.TestCase):
    def test_query_sidecar_filters_inactive_and_expands_relations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_root = root / "shared"
            runtime_root = root / "runtime"
            source_root.mkdir()
            runtime_root.mkdir()
            sidecar = root / "family.sqlite"

            connection = create_sidecar_db(sidecar)
            try:
                docs = [
                    {
                        "record_id": "solver-1",
                        "family": "demo-family",
                        "entity_kind": "solver",
                        "entity_id": "solver-1",
                        "source_layer": "runtime",
                        "file_path": "solvers/solver-1.yaml",
                        "title": "Solver One",
                        "summary": "solver query target",
                        "details": "active solver",
                        "evidence": "",
                        "status": "active",
                        "valid_from": "2026-03-20T00:00:00Z",
                        "valid_to": "",
                        "tags_json": "[]",
                        "related_refs_json": "[]",
                        "raw_json": json.dumps({"entity_id": "solver-1"}),
                    },
                    {
                        "record_id": "solution-1",
                        "family": "demo-family",
                        "entity_kind": "solution",
                        "entity_id": "solution-1",
                        "source_layer": "runtime",
                        "file_path": "solutions/solution-1.yaml",
                        "title": "Solution One",
                        "summary": "related fix",
                        "details": "linked from solver",
                        "evidence": "",
                        "status": "active",
                        "valid_from": "2026-03-20T00:00:00Z",
                        "valid_to": "",
                        "tags_json": "[]",
                        "related_refs_json": "[]",
                        "raw_json": json.dumps({"entity_id": "solution-1"}),
                    },
                    {
                        "record_id": "solver-old",
                        "family": "demo-family",
                        "entity_kind": "solver",
                        "entity_id": "solver-old",
                        "source_layer": "runtime",
                        "file_path": "solvers/solver-old.yaml",
                        "title": "Solver Old",
                        "summary": "solver query target",
                        "details": "old version",
                        "evidence": "",
                        "status": "superseded",
                        "valid_from": "2026-03-10T00:00:00Z",
                        "valid_to": "2026-03-12T00:00:00Z",
                        "tags_json": "[]",
                        "related_refs_json": "[]",
                        "raw_json": json.dumps({"entity_id": "solver-old"}),
                    },
                ]
                for doc in docs:
                    cursor = connection.execute(
                        """
                        INSERT INTO docs (
                            record_id, family, entity_kind, entity_id, source_layer, file_path,
                            title, summary, details, evidence, status, valid_from, valid_to,
                            tags_json, related_refs_json, raw_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            doc["record_id"],
                            doc["family"],
                            doc["entity_kind"],
                            doc["entity_id"],
                            doc["source_layer"],
                            doc["file_path"],
                            doc["title"],
                            doc["summary"],
                            doc["details"],
                            doc["evidence"],
                            doc["status"],
                            doc["valid_from"],
                            doc["valid_to"],
                            doc["tags_json"],
                            doc["related_refs_json"],
                            doc["raw_json"],
                        ),
                    )
                    connection.execute(
                        "INSERT INTO docs_fts(rowid, title, summary, details, evidence) VALUES (?, ?, ?, ?, ?)",
                        (cursor.lastrowid, doc["title"], doc["summary"], doc["details"], doc["evidence"]),
                    )
                connection.execute(
                    "INSERT INTO relations(family, src_kind, src_id, rel_type, dst_kind, dst_id, evidence_file) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("demo-family", "solver", "solver-1", "solves_with", "solution", "solution-1", "links/demo.yaml"),
                )
                connection.commit()
            finally:
                connection.close()

            context = FamilyContext(
                workspace_root=root,
                workspace_id="demo",
                manifest={},
                repo_ids=set(),
                family_definition={"name": "demo-family"},
                source_root=source_root,
                runtime_root=runtime_root,
                sidecar_path=sidecar,
                contract={},
            )

            payload = query_sidecar([context], text="solver", limit=5, include_inactive=False, include_related=True)
            entity_ids = [item["entity_id"] for item in payload["results"]]
            self.assertIn("solver-1", entity_ids)
            self.assertIn("solution-1", entity_ids)
            self.assertNotIn("solver-old", entity_ids)

            inactive_payload = query_sidecar([context], text="solver", limit=5, include_inactive=True, include_related=False)
            inactive_ids = [item["entity_id"] for item in inactive_payload["results"]]
            self.assertIn("solver-old", inactive_ids)

    def test_validate_family_flags_non_portable_shared_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_root = root / "family"
            runtime_root = root / "runtime"
            source_root.mkdir()
            runtime_root.mkdir()
            (source_root / "index.yaml").write_text(
                json.dumps(
                    {
                        "repo_id": "missing-repo",
                        "memory_file": "missing/entry.yaml",
                        "primary_files": ["C:/absolute/path.cpp"],
                        "evidence_path": "D:/absolute/evidence.txt",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            context = FamilyContext(
                workspace_root=root,
                workspace_id="demo",
                manifest={},
                repo_ids={"known-repo"},
                family_definition={"name": "demo-family"},
                source_root=source_root,
                runtime_root=runtime_root,
                sidecar_path=root / "unused.sqlite",
                contract={"managed_paths": ["index.yaml"], "validate": lambda **_: []},
            )

            payload = validate_family(context)
            codes = {item["code"] for item in payload["issues"]}
            self.assertIn("unknown-repo-id", codes)
            self.assertIn("missing-memory-ref", codes)
            self.assertIn("absolute-repo-path", codes)
            self.assertIn("absolute-path", codes)


if __name__ == "__main__":
    unittest.main()
