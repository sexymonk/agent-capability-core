#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "scripts" / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))
from codex_workspace import load_manifest, machine_local_path, codex_home, normalize_path  # type: ignore


def main() -> int:
    manifest = load_manifest(ROOT)
    report = {
        "workspace_root": normalize_path(ROOT),
        "manifest_ok": True,
        "machine_local_path": normalize_path(machine_local_path(ROOT)),
        "machine_local_exists": machine_local_path(ROOT).exists(),
        "codex_home": normalize_path(codex_home(ROOT)) if machine_local_path(ROOT).exists() else "",
        "skills": [],
        "missing": [],
    }
    for item in manifest.get("runtime_mounts", {}).get("skills", []):
        skill_path = ROOT / item["source"]
        exists = skill_path.exists()
        report["skills"].append({"name": item["name"], "path": normalize_path(skill_path), "exists": exists})
        if not exists:
            report["missing"].append(normalize_path(skill_path))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["missing"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
