#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

MANIFEST_NAME = "workspace.manifest.yaml"


def normalize_path(value: str | Path | None) -> str:
    if value is None:
        return ""
    return str(value).replace("\\", "/")


def ensure_dir(path: str | Path) -> Path:
    value = Path(path)
    value.mkdir(parents=True, exist_ok=True)
    return value


def load_json_yaml(path: str | Path, default: Any | None = None) -> Any:
    value = Path(path)
    if not value.exists():
        return default
    raw = value.read_text(encoding="utf-8-sig").strip()
    if not raw:
        return default
    return json.loads(raw)


def save_json_yaml(path: str | Path, payload: Any) -> Path:
    value = Path(path)
    ensure_dir(value.parent)
    value.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return value


def find_workspace_root(start: str | Path) -> Path:
    current = Path(start).resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / MANIFEST_NAME).exists():
            return candidate
    raise RuntimeError(f"Unable to locate {MANIFEST_NAME} from {start}")


def load_manifest(workspace_root: str | Path) -> dict[str, Any]:
    root = find_workspace_root(workspace_root)
    payload = load_json_yaml(root / MANIFEST_NAME, default={})
    if not isinstance(payload, dict):
        raise RuntimeError(f"Manifest is invalid: {root / MANIFEST_NAME}")
    return payload


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex")).resolve()


def default_codex_local_home() -> Path:
    return Path(os.environ.get("CODEX_LOCAL_HOME") or (Path.home() / ".codex-local")).resolve()


def machine_local_path(workspace_root: str | Path) -> Path:
    root = find_workspace_root(workspace_root)
    manifest = load_manifest(root)
    workspace_id = str(manifest.get("workspace_id") or root.name)
    repo_local = root / "machine.local.yaml"
    if repo_local.exists():
        return repo_local
    return default_codex_local_home() / workspace_id / "machine.local.yaml"


def load_machine_local(workspace_root: str | Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    path = machine_local_path(workspace_root)
    payload = load_json_yaml(path, default=default or {})
    if not isinstance(payload, dict):
        raise RuntimeError(f"Machine-local config is invalid: {path}")
    return payload


def codex_home(workspace_root: str | Path) -> Path:
    config = load_machine_local(workspace_root)
    return Path(str(config.get("codex_home") or default_codex_home())).expanduser().resolve()


def codex_local_home(workspace_root: str | Path) -> Path:
    config = load_machine_local(workspace_root)
    return Path(str(config.get("codex_local_home") or default_codex_local_home())).expanduser().resolve()


def repo_paths(workspace_root: str | Path) -> dict[str, str]:
    config = load_machine_local(workspace_root)
    return {str(key): str(value) for key, value in dict(config.get("repo_paths") or {}).items() if str(value).strip()}
