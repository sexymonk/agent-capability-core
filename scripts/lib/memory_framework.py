#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import sqlite3
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from codex_workspace import codex_home, load_json_yaml, load_manifest, normalize_path


ABS_PATH_RE = re.compile(r"^(?:[A-Za-z]:[\\/]|/(?!/))")
MEMORY_REF_KEY_RE = re.compile(r"^memory_file(s)?$", re.IGNORECASE)
RELATIVE_REPO_PATH_KEY_RE = re.compile(
    r"(?:^|_)(?:path|paths|primary_files|entry_files|boundary_asset_paths|member_paths|solver_primary_files|solver_step_core)$",
    re.IGNORECASE,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_relpath(value: str | Path) -> str:
    return normalize_path(value).lstrip("/")


def ensure_dir(path: str | Path) -> Path:
    value = Path(path)
    value.mkdir(parents=True, exist_ok=True)
    return value


def save_json_yaml(path: str | Path, payload: Any) -> Path:
    value = Path(path)
    ensure_dir(value.parent)
    value.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return value


def tokenize_search(text: str) -> list[str]:
    return [token for token in re.findall(r"[A-Za-z0-9_./-]+", text.lower()) if token.strip()]


def build_fts_query(text: str) -> str:
    tokens = [token.replace('"', "") for token in tokenize_search(text)]
    if not tokens:
        raise RuntimeError("Query text must contain at least one searchable token.")
    return " OR ".join(f'"{token}"*' for token in tokens)


def is_absolute_path_string(value: str) -> bool:
    if not value or value.startswith(("http://", "https://")):
        return False
    return bool(ABS_PATH_RE.match(value))


def flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(part for part in (flatten_text(item) for item in value) if part)
    if isinstance(value, dict):
        return " ".join(part for part in (flatten_text(item) for item in value.values()) if part)
    return str(value)


def iter_key_values(value: Any, path: str = ""):
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield child_path, key, item
            yield from iter_key_values(item, child_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, str(index), item
            yield from iter_key_values(item, child_path)


def relative_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return []


def collect_files(root: Path, managed_paths: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for rel in managed_paths:
        rel_value = normalize_relpath(rel)
        target = root / rel_value
        if not target.exists():
            continue
        if target.is_file():
            result[rel_value] = target
            continue
        for file in sorted(item for item in target.rglob("*") if item.is_file()):
            result[normalize_relpath(file.relative_to(root))] = file
    return result


def file_bytes(path: Path) -> bytes:
    return path.read_bytes()


def diff_managed_trees(source_root: Path, staged_root: Path, managed_paths: list[str]) -> dict[str, Any]:
    source_files = collect_files(source_root, managed_paths)
    staged_files = collect_files(staged_root, managed_paths)
    added: list[str] = []
    changed: list[str] = []
    deleted: list[str] = []
    unchanged = 0
    for rel_path, staged_path in staged_files.items():
        source_path = source_files.get(rel_path)
        if source_path is None:
            added.append(rel_path)
        elif file_bytes(source_path) != file_bytes(staged_path):
            changed.append(rel_path)
        else:
            unchanged += 1
    for rel_path in source_files:
        if rel_path not in staged_files:
            deleted.append(rel_path)
    return {
        "added": sorted(added),
        "changed": sorted(changed),
        "deleted": sorted(deleted),
        "unchanged_count": unchanged,
    }


def apply_managed_tree(source_root: Path, staged_root: Path, managed_paths: list[str], diff_payload: dict[str, Any]) -> dict[str, Any]:
    for rel_path in diff_payload["deleted"]:
        target = source_root / rel_path
        if target.exists():
            target.unlink()
    for rel_path in [*diff_payload["added"], *diff_payload["changed"]]:
        staged_file = staged_root / rel_path
        target = source_root / rel_path
        ensure_dir(target.parent)
        shutil.copy2(staged_file, target)
    for rel in managed_paths:
        rel_value = normalize_relpath(rel)
        target = source_root / rel_value
        if target.is_dir() and not any(target.iterdir()):
            target.rmdir()
    return {
        "applied": True,
        "added": list(diff_payload["added"]),
        "changed": list(diff_payload["changed"]),
        "deleted": list(diff_payload["deleted"]),
    }


@dataclass
class FamilyContext:
    workspace_root: Path
    workspace_id: str
    manifest: dict[str, Any]
    repo_ids: set[str]
    family_definition: dict[str, Any]
    source_root: Path
    runtime_root: Path
    sidecar_path: Path
    contract: dict[str, Any]


def runtime_root_for_family(workspace_root: Path, family_definition: dict[str, Any]) -> Path:
    runtime_target = str(family_definition.get("runtime_target") or family_definition["name"])
    return (codex_home(workspace_root) / "memories" / runtime_target).resolve()


def sidecar_path_for_family(workspace_root: Path, manifest: dict[str, Any], family_definition: dict[str, Any]) -> Path:
    runtime_target = str(family_definition.get("runtime_target") or family_definition["name"])
    workspace_id = str(manifest.get("workspace_id") or workspace_root.name)
    return (codex_home(workspace_root) / "memories" / ".sidecar" / workspace_id / f"{runtime_target}.sqlite").resolve()


def selected_families(manifest: dict[str, Any], requested: list[str]) -> list[dict[str, Any]]:
    known = {str(item.get("name")): dict(item) for item in manifest.get("memory_families", [])}
    if not known:
        raise RuntimeError("This workspace does not define any memory_families.")
    if not requested:
        return list(known.values())
    result: list[dict[str, Any]] = []
    for item in requested:
        if item == "all":
            return list(known.values())
        if item not in known:
            raise RuntimeError(f"Unknown memory family: {item}")
        result.append(known[item])
    return result


def load_contract(workspace_root: Path, family_definition: dict[str, Any]) -> dict[str, Any]:
    transformer = str(family_definition.get("transformer") or "").strip()
    if not transformer:
        raise RuntimeError(f"memory_families[{family_definition.get('name')}] is missing transformer.")
    if ":" not in transformer:
        raise RuntimeError(f"Invalid transformer spec: {transformer}")
    module_rel, callable_name = transformer.split(":", 1)
    module_path = (workspace_root / module_rel).resolve()
    if not module_path.exists():
        raise RuntimeError(f"Transformer module does not exist: {module_path}")
    module_name = f"_memory_contract_{workspace_root.name}_{family_definition['name']}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load transformer module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    factory = getattr(module, callable_name, None)
    if factory is None or not callable(factory):
        raise RuntimeError(f"Transformer callable not found: {transformer}")
    contract = factory(workspace_root=workspace_root, family_definition=family_definition)
    if not isinstance(contract, dict):
        raise RuntimeError(f"Transformer callable must return dict contract: {transformer}")
    for required in ("managed_paths", "render", "stage_source", "build_index"):
        if required not in contract:
            raise RuntimeError(f"Contract for {family_definition['name']} missing required key: {required}")
    return contract


def family_contexts(workspace_root: str | Path, requested: list[str]) -> list[FamilyContext]:
    root = Path(workspace_root).resolve()
    manifest = load_manifest(root)
    workspace_id = str(manifest.get("workspace_id") or root.name)
    repo_ids = {str(item.get("id")) for item in manifest.get("repo_ids", []) if str(item.get("id") or "").strip()}
    results: list[FamilyContext] = []
    for family_definition in selected_families(manifest, requested):
        source_root = (root / str(family_definition["source"])).resolve()
        if not source_root.exists():
            raise RuntimeError(f"Memory family source root does not exist: {source_root}")
        contract = load_contract(root, family_definition)
        results.append(
            FamilyContext(
                workspace_root=root,
                workspace_id=workspace_id,
                manifest=manifest,
                repo_ids=repo_ids,
                family_definition=family_definition,
                source_root=source_root,
                runtime_root=runtime_root_for_family(root, family_definition),
                sidecar_path=sidecar_path_for_family(root, manifest, family_definition),
                contract=contract,
            )
        )
    return results

def create_sidecar_db(path: Path) -> sqlite3.Connection:
    ensure_dir(path.parent)
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    connection.execute(
        """
        CREATE TABLE docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id TEXT NOT NULL UNIQUE,
            family TEXT NOT NULL,
            entity_kind TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            source_layer TEXT NOT NULL,
            file_path TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            details TEXT NOT NULL,
            evidence TEXT NOT NULL,
            status TEXT NOT NULL,
            valid_from TEXT NOT NULL,
            valid_to TEXT NOT NULL,
            tags_json TEXT NOT NULL,
            related_refs_json TEXT NOT NULL,
            raw_json TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE VIRTUAL TABLE docs_fts USING fts5(
            title,
            summary,
            details,
            evidence,
            content='docs',
            content_rowid='id'
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE relations (
            family TEXT NOT NULL,
            src_kind TEXT NOT NULL,
            src_id TEXT NOT NULL,
            rel_type TEXT NOT NULL,
            dst_kind TEXT NOT NULL,
            dst_id TEXT NOT NULL,
            evidence_file TEXT NOT NULL
        )
        """
    )
    connection.execute("CREATE INDEX relations_src_idx ON relations(family, src_kind, src_id)")
    connection.execute("CREATE INDEX relations_dst_idx ON relations(family, dst_kind, dst_id)")
    return connection


def normalized_record(record: dict[str, Any], family_name: str) -> dict[str, Any]:
    normalized = dict(record)
    normalized["record_id"] = str(normalized.get("record_id") or f"{family_name}:{normalized.get('entity_kind', 'record')}:{normalized.get('entity_id', 'unknown')}:{normalized.get('file_path', '')}")
    normalized["family"] = family_name
    normalized["entity_kind"] = str(normalized.get("entity_kind") or "record")
    normalized["entity_id"] = str(normalized.get("entity_id") or normalized["record_id"])
    normalized["source_layer"] = str(normalized.get("source_layer") or "runtime")
    normalized["file_path"] = normalize_path(normalized.get("file_path") or "")
    normalized["title"] = str(normalized.get("title") or normalized["entity_id"])
    normalized["summary"] = str(normalized.get("summary") or "")
    normalized["details"] = str(normalized.get("details") or "")
    normalized["evidence"] = flatten_text(normalized.get("evidence") or "")
    normalized["status"] = str(normalized.get("status") or "active")
    normalized["valid_from"] = str(normalized.get("valid_from") or "")
    normalized["valid_to"] = str(normalized.get("valid_to") or "")
    normalized["tags"] = [str(item) for item in list(normalized.get("tags") or []) if str(item).strip()]
    normalized["related_refs"] = [str(item) for item in list(normalized.get("related_refs") or []) if str(item).strip()]
    return normalized


def normalized_relation(relation: dict[str, Any], family_name: str) -> dict[str, Any]:
    return {
        "family": family_name,
        "src_kind": str(relation.get("src_kind") or "record"),
        "src_id": str(relation.get("src_id") or ""),
        "rel_type": str(relation.get("rel_type") or "related_to"),
        "dst_kind": str(relation.get("dst_kind") or "record"),
        "dst_id": str(relation.get("dst_id") or ""),
        "evidence_file": normalize_path(relation.get("evidence_file") or ""),
    }


def reindex_family(context: FamilyContext) -> dict[str, Any]:
    if not context.runtime_root.exists():
        raise RuntimeError(f"Runtime memory root does not exist for {context.family_definition['name']}: {context.runtime_root}")
    payload = context.contract["build_index"](
        workspace_root=context.workspace_root,
        family_definition=context.family_definition,
        source_root=context.source_root,
        runtime_root=context.runtime_root,
        sidecar_path=context.sidecar_path,
    )
    docs = [normalized_record(item, context.family_definition["name"]) for item in list(payload.get("docs") or [])]
    relations = [normalized_relation(item, context.family_definition["name"]) for item in list(payload.get("relations") or [])]
    connection = create_sidecar_db(context.sidecar_path)
    try:
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
                    json.dumps(doc["tags"], ensure_ascii=False),
                    json.dumps(doc["related_refs"], ensure_ascii=False),
                    json.dumps(doc, ensure_ascii=False),
                ),
            )
            connection.execute(
                "INSERT INTO docs_fts(rowid, title, summary, details, evidence) VALUES (?, ?, ?, ?, ?)",
                (cursor.lastrowid, doc["title"], doc["summary"], doc["details"], doc["evidence"]),
            )
        for relation in relations:
            connection.execute(
                "INSERT INTO relations(family, src_kind, src_id, rel_type, dst_kind, dst_id, evidence_file) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    relation["family"],
                    relation["src_kind"],
                    relation["src_id"],
                    relation["rel_type"],
                    relation["dst_kind"],
                    relation["dst_id"],
                    relation["evidence_file"],
                ),
            )
        connection.commit()
    finally:
        connection.close()
    return {
        "family": context.family_definition["name"],
        "sidecar_path": normalize_path(context.sidecar_path),
        "doc_count": len(docs),
        "relation_count": len(relations),
    }


def parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    cleaned = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None

def query_sidecar(contexts: list[FamilyContext], text: str, limit: int, include_inactive: bool, include_related: bool) -> dict[str, Any]:
    fts_query = build_fts_query(text)
    now = datetime.now(timezone.utc)
    results: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    primary_ids: list[tuple[FamilyContext, str, str]] = []
    for context in contexts:
        if not context.sidecar_path.exists():
            raise RuntimeError(f"Sidecar index does not exist for {context.family_definition['name']}: {context.sidecar_path}. Run reindex first.")
        connection = sqlite3.connect(context.sidecar_path)
        connection.row_factory = sqlite3.Row
        try:
            rows = connection.execute(
                """
                SELECT
                    docs.record_id,
                    docs.family,
                    docs.entity_kind,
                    docs.entity_id,
                    docs.source_layer,
                    docs.file_path,
                    docs.title,
                    docs.summary,
                    docs.details,
                    docs.evidence,
                    docs.status,
                    docs.valid_from,
                    docs.valid_to,
                    docs.tags_json,
                    docs.related_refs_json,
                    docs.raw_json,
                    bm25(docs_fts) AS raw_score
                FROM docs_fts
                JOIN docs ON docs.id = docs_fts.rowid
                WHERE docs_fts MATCH ?
                LIMIT ?
                """,
                (fts_query, max(limit * 4, 20)),
            ).fetchall()
            for row in rows:
                status = str(row["status"] or "active")
                if not include_inactive and status in {"superseded", "archived"}:
                    continue
                valid_to = parse_iso(str(row["valid_to"] or ""))
                if not include_inactive and valid_to is not None and valid_to < now:
                    continue
                tokens = tokenize_search(text)
                boost = 0.0
                for token in tokens:
                    if token == str(row["entity_id"] or "").lower():
                        boost += 50.0
                    elif token in str(row["title"] or "").lower():
                        boost += 20.0
                    elif token in str(row["file_path"] or "").lower():
                        boost += 8.0
                raw_score = abs(float(row["raw_score"] or 0.0))
                score = (1000.0 / (1.0 + raw_score)) + boost
                item = {
                    "record_id": row["record_id"],
                    "family": row["family"],
                    "entity_kind": row["entity_kind"],
                    "entity_id": row["entity_id"],
                    "source_layer": row["source_layer"],
                    "file_path": row["file_path"],
                    "title": row["title"],
                    "summary": row["summary"],
                    "details": row["details"],
                    "evidence": row["evidence"],
                    "status": status,
                    "valid_from": row["valid_from"],
                    "valid_to": row["valid_to"],
                    "tags": json.loads(row["tags_json"] or "[]"),
                    "related_refs": json.loads(row["related_refs_json"] or "[]"),
                    "score": score,
                    "raw_json": json.loads(row["raw_json"]),
                }
                if item["record_id"] in seen_ids:
                    continue
                seen_ids.add(item["record_id"])
                results.append(item)
                primary_ids.append((context, item["entity_kind"], item["entity_id"]))
        finally:
            connection.close()
    if include_related and primary_ids:
        for context, entity_kind, entity_id in primary_ids[: max(limit, 3)]:
            connection = sqlite3.connect(context.sidecar_path)
            connection.row_factory = sqlite3.Row
            try:
                relation_rows = connection.execute(
                    "SELECT dst_kind, dst_id FROM relations WHERE family = ? AND src_kind = ? AND src_id = ?",
                    (context.family_definition["name"], entity_kind, entity_id),
                ).fetchall()
                for relation in relation_rows:
                    row = connection.execute(
                        """
                        SELECT
                            record_id, family, entity_kind, entity_id, source_layer, file_path,
                            title, summary, details, evidence, status, valid_from, valid_to,
                            tags_json, related_refs_json, raw_json
                        FROM docs
                        WHERE family = ? AND entity_kind = ? AND entity_id = ?
                        LIMIT 1
                        """,
                        (context.family_definition["name"], relation["dst_kind"], relation["dst_id"]),
                    ).fetchone()
                    if row is None or row["record_id"] in seen_ids:
                        continue
                    status = str(row["status"] or "active")
                    if not include_inactive and status in {"superseded", "archived"}:
                        continue
                    results.append(
                        {
                            "record_id": row["record_id"],
                            "family": row["family"],
                            "entity_kind": row["entity_kind"],
                            "entity_id": row["entity_id"],
                            "source_layer": row["source_layer"],
                            "file_path": row["file_path"],
                            "title": row["title"],
                            "summary": row["summary"],
                            "details": row["details"],
                            "evidence": row["evidence"],
                            "status": status,
                            "valid_from": row["valid_from"],
                            "valid_to": row["valid_to"],
                            "tags": json.loads(row["tags_json"] or "[]"),
                            "related_refs": json.loads(row["related_refs_json"] or "[]"),
                            "score": 40.0,
                            "raw_json": json.loads(row["raw_json"]),
                            "via_relation": {"src_kind": entity_kind, "src_id": entity_id},
                        }
                    )
                    seen_ids.add(str(row["record_id"]))
            finally:
                connection.close()
    results.sort(key=lambda item: (-float(item["score"]), item["family"], item["entity_kind"], item["entity_id"]))
    return {"query": text, "results": results[:limit]}


def validate_family(context: FamilyContext) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    for managed_rel, file in collect_files(context.source_root, list(context.contract["managed_paths"])).items():
        payload = load_json_yaml(file, default={})
        if payload is None:
            continue
        for value_path, key, value in iter_key_values(payload):
            if isinstance(value, str) and is_absolute_path_string(value):
                issues.append(
                    {
                        "severity": "error",
                        "family": context.family_definition["name"],
                        "code": "absolute-path",
                        "path": normalize_path(file),
                        "field": value_path,
                        "message": f"Shared memory contains absolute path: {value}",
                    }
                )
            if key == "repo_id" and str(value).strip() and str(value) not in context.repo_ids:
                issues.append(
                    {
                        "severity": "error",
                        "family": context.family_definition["name"],
                        "code": "unknown-repo-id",
                        "path": normalize_path(file),
                        "field": value_path,
                        "message": f"Unknown repo_id: {value}",
                    }
                )
            if key == "repo_ids":
                for repo_id in relative_string_list(value):
                    if repo_id not in context.repo_ids:
                        issues.append(
                            {
                                "severity": "error",
                                "family": context.family_definition["name"],
                                "code": "unknown-repo-id",
                                "path": normalize_path(file),
                                "field": value_path,
                                "message": f"Unknown repo_id: {repo_id}",
                            }
                        )
            if MEMORY_REF_KEY_RE.search(key):
                for rel_path in relative_string_list(value):
                    if is_absolute_path_string(rel_path):
                        issues.append(
                            {
                                "severity": "error",
                                "family": context.family_definition["name"],
                                "code": "absolute-memory-ref",
                                "path": normalize_path(file),
                                "field": value_path,
                                "message": f"Memory reference must stay relative inside shared source: {rel_path}",
                            }
                        )
                    elif rel_path and not (context.source_root / rel_path).exists():
                        issues.append(
                            {
                                "severity": "error",
                                "family": context.family_definition["name"],
                                "code": "missing-memory-ref",
                                "path": normalize_path(file),
                                "field": value_path,
                                "message": f"Referenced memory file does not exist inside family: {rel_path}",
                            }
                        )
            if RELATIVE_REPO_PATH_KEY_RE.search(key):
                for rel_path in relative_string_list(value):
                    if is_absolute_path_string(rel_path):
                        issues.append(
                            {
                                "severity": "error",
                                "family": context.family_definition["name"],
                                "code": "absolute-repo-path",
                                "path": normalize_path(file),
                                "field": value_path,
                                "message": f"Shared source must store repo-relative paths, not absolute: {rel_path}",
                            }
                        )
    custom_validate = context.contract.get("validate")
    if callable(custom_validate):
        issues.extend(
            list(
                custom_validate(
                    workspace_root=context.workspace_root,
                    family_definition=context.family_definition,
                    source_root=context.source_root,
                    runtime_root=context.runtime_root,
                )
                or []
            )
        )
    return {"family": context.family_definition["name"], "issue_count": len(issues), "issues": issues}

def compact_family(context: FamilyContext) -> dict[str, Any]:
    payload = context.contract["build_index"](
        workspace_root=context.workspace_root,
        family_definition=context.family_definition,
        source_root=context.source_root,
        runtime_root=context.runtime_root,
        sidecar_path=context.sidecar_path,
    )
    docs = [normalized_record(item, context.family_definition["name"]) for item in list(payload.get("docs") or [])]
    relations = [normalized_relation(item, context.family_definition["name"]) for item in list(payload.get("relations") or [])]
    by_kind: dict[str, int] = {}
    by_status: dict[str, int] = {}
    entities: dict[tuple[str, str], int] = {}
    for doc in docs:
        by_kind[doc["entity_kind"]] = by_kind.get(doc["entity_kind"], 0) + 1
        by_status[doc["status"]] = by_status.get(doc["status"], 0) + 1
        entity_key = (doc["entity_kind"], doc["entity_id"])
        entities[entity_key] = entities.get(entity_key, 0) + 1
    digest = {
        "family": context.family_definition["name"],
        "generated_at": utc_now(),
        "doc_count": len(docs),
        "relation_count": len(relations),
        "entity_kind_counts": by_kind,
        "status_counts": by_status,
        "top_entities": [
            {"entity_kind": entity_kind, "entity_id": entity_id, "record_count": count}
            for (entity_kind, entity_id), count in sorted(entities.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))[:15]
        ],
    }
    digest_path = context.runtime_root / "__memory_digest__.json"
    save_json_yaml(digest_path, digest)
    return {"family": context.family_definition["name"], "digest_path": normalize_path(digest_path), "doc_count": len(docs)}


def render_family(context: FamilyContext, run_reindex: bool = True, run_compact: bool = True) -> dict[str, Any]:
    ensure_dir(context.runtime_root.parent)
    result = context.contract["render"](
        workspace_root=context.workspace_root,
        family_definition=context.family_definition,
        source_root=context.source_root,
        runtime_root=context.runtime_root,
    )
    payload = {"family": context.family_definition["name"], **dict(result or {})}
    if run_reindex:
        payload["reindex"] = reindex_family(context)
    if run_compact:
        payload["compact"] = compact_family(context)
    return payload


def promote_family(context: FamilyContext, dry_run: bool) -> dict[str, Any]:
    validation = validate_family(context)
    if validation["issue_count"] > 0:
        raise RuntimeError(f"Validation failed for {context.family_definition['name']}; fix issues before promote.")
    with tempfile.TemporaryDirectory(prefix=f"{context.family_definition['name']}-promote-") as temp_dir:
        staged_root = Path(temp_dir).resolve()
        stage_payload = context.contract["stage_source"](
            workspace_root=context.workspace_root,
            family_definition=context.family_definition,
            source_root=context.source_root,
            runtime_root=context.runtime_root,
            staged_root=staged_root,
        )
        managed_paths = [normalize_relpath(item) for item in list(stage_payload.get("managed_paths") or context.contract["managed_paths"])]
        diff_payload = diff_managed_trees(context.source_root, staged_root, managed_paths)
        payload = {
            "family": context.family_definition["name"],
            "dry_run": dry_run,
            "managed_paths": managed_paths,
            "diff": diff_payload,
        }
        if not dry_run:
            payload["apply"] = apply_managed_tree(context.source_root, staged_root, managed_paths, diff_payload)
        return payload


def run_command(workspace_root: str | Path, command: str, families: list[str], *, text: str = "", limit: int = 10, include_inactive: bool = False, include_related: bool = True, dry_run: bool = True) -> dict[str, Any]:
    contexts = family_contexts(workspace_root, families)
    if command == "render":
        return {"workspace_root": normalize_path(Path(workspace_root).resolve()), "results": [render_family(context) for context in contexts]}
    if command == "promote":
        return {"workspace_root": normalize_path(Path(workspace_root).resolve()), "results": [promote_family(context, dry_run=dry_run) for context in contexts]}
    if command == "validate":
        return {"workspace_root": normalize_path(Path(workspace_root).resolve()), "results": [validate_family(context) for context in contexts]}
    if command == "reindex":
        return {"workspace_root": normalize_path(Path(workspace_root).resolve()), "results": [reindex_family(context) for context in contexts]}
    if command == "compact":
        return {"workspace_root": normalize_path(Path(workspace_root).resolve()), "results": [compact_family(context) for context in contexts]}
    if command == "query":
        return {"workspace_root": normalize_path(Path(workspace_root).resolve()), **query_sidecar(contexts, text=text, limit=limit, include_inactive=include_inactive, include_related=include_related)}
    raise RuntimeError(f"Unsupported command: {command}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generic memory framework CLI for shared/runtime family workflows.")
    parser.add_argument("--workspace-root", default=".", help="Workspace root containing workspace.manifest.yaml.")
    parser.add_argument("--family", action="append", default=[], help="Memory family name. Repeat or use 'all'.")
    parser.add_argument("--json", action="store_true", help="Print structured JSON output.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("render", help="Render shared source memories into runtime copies and refresh sidecars.")

    promote = subparsers.add_parser("promote", help="Preview or apply promotion from runtime copies back into shared source.")
    promote.add_argument("--apply", action="store_true", help="Apply the promotion. Default is dry-run preview.")

    subparsers.add_parser("validate", help="Validate shared source memory families.")
    subparsers.add_parser("reindex", help="Rebuild runtime sidecar indexes.")
    subparsers.add_parser("compact", help="Refresh runtime digest files.")

    query = subparsers.add_parser("query", help="Query runtime sidecar indexes.")
    query.add_argument("--text", required=True, help="Search text.")
    query.add_argument("--limit", type=int, default=10, help="Maximum number of results to return.")
    query.add_argument("--include-inactive", action="store_true", help="Include superseded, archived, or expired records.")
    query.add_argument("--no-related", action="store_true", help="Disable relation expansion.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "query":
        payload = run_command(
            args.workspace_root,
            "query",
            args.family,
            text=args.text,
            limit=int(args.limit),
            include_inactive=bool(args.include_inactive),
            include_related=not bool(args.no_related),
        )
    elif args.command == "promote":
        payload = run_command(args.workspace_root, "promote", args.family, dry_run=not bool(args.apply))
    else:
        payload = run_command(args.workspace_root, args.command, args.family)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
