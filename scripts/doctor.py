#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "scripts" / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))
from codex_workspace import (  # type: ignore
    install_state_path,
    load_install_state,
    load_lock,
    load_manifest,
    machine_local_path,
    manifest_repositories,
    network_config,
    normalize_path,
    runtime_config,
    runtime_exports_root,
    runtime_home,
    runtime_local_home,
    workspace_api_version,
)


def main() -> int:
    manifest = load_manifest(ROOT)
    lock = load_lock(ROOT)
    state_path = install_state_path(ROOT)
    install_state = load_install_state(ROOT) if state_path.exists() else {}
    machine_path = machine_local_path(ROOT)
    runtime = runtime_config(ROOT) if machine_path.exists() else {}
    report = {
        "workspace_root": normalize_path(ROOT),
        "manifest_ok": True,
        "workspace_api_version": workspace_api_version(ROOT),
        "lockfile_path": normalize_path(ROOT / "workspace.lock.yaml"),
        "lockfile_exists": bool(lock),
        "machine_local_path": normalize_path(machine_path),
        "machine_local_exists": machine_path.exists(),
        "runtime": {
            "provider": str(runtime.get("provider") or ""),
            "channel": str(runtime.get("channel") or ""),
            "home": normalize_path(runtime_home(ROOT)) if machine_path.exists() else "",
            "local_home": normalize_path(runtime_local_home(ROOT)) if machine_path.exists() else "",
            "exports_root": normalize_path(runtime_exports_root(ROOT)) if machine_path.exists() else "",
            "command": str(runtime.get("command") or ""),
            "capabilities": list(runtime.get("capabilities") or []),
        },
        "network": network_config(ROOT) if machine_path.exists() else {},
        "install_state_path": normalize_path(state_path),
        "install_state_exists": state_path.exists(),
        "install_state": install_state if install_state else {},
        "repositories": manifest_repositories(ROOT),
        "bootstrap_tools": {
            "git": shutil.which("git") is not None,
            "gh": shutil.which("gh") is not None,
            "python": shutil.which("python") is not None,
            "cmake": shutil.which("cmake") is not None,
            "winget": shutil.which("winget") is not None,
        },
        "skills": [],
        "missing": [],
    }
    for item in manifest.get("runtime_mounts", {}).get("skills", []):
        skill_path = ROOT / item["source"]
        exists = skill_path.exists()
        report["skills"].append({"name": item["name"], "path": normalize_path(skill_path), "exists": exists})
        if not exists:
            report["missing"].append(normalize_path(skill_path))
    if machine_path.exists() and not str(runtime.get("provider") or "").strip():
        report["missing"].append("runtime.provider is not configured")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["missing"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
