#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

MANIFEST_NAME = "workspace.manifest.yaml"
LOCK_NAME = "workspace.lock.yaml"

_PROVIDER_DEFAULTS: dict[str, dict[str, Any]] = {
    "codex_desktop": {
        "channel": "desktop",
        "default_home": "~/.codex",
        "default_local_home": "~/.codex-local",
        "default_command": "~/.codex/.sandbox-bin/codex.exe",
        "capabilities": ["workspace_mount", "memory_runtime", "chat_bridge", "session_resume", "linear"],
    },
    "codex_vscode": {
        "channel": "vscode",
        "default_home": "~/.codex",
        "default_local_home": "~/.codex-local",
        "default_command": "codex",
        "capabilities": ["workspace_mount", "memory_runtime"],
    },
    "codex_cli": {
        "channel": "cli",
        "default_home": "~/.codex",
        "default_local_home": "~/.codex-local",
        "default_command": "codex",
        "capabilities": ["workspace_mount", "memory_runtime", "chat_bridge", "session_resume", "linear"],
    },
    "claude_code": {
        "channel": "cli",
        "default_home": "~/.claude",
        "default_local_home": "~/.codex-local",
        "default_command": "claude",
        "capabilities": ["memory_runtime"],
    },
    "gemini_cli": {
        "channel": "cli",
        "default_home": "~/.gemini",
        "default_local_home": "~/.codex-local",
        "default_command": "gemini",
        "capabilities": ["memory_runtime"],
    },
    "external": {
        "channel": "external",
        "default_home": "~/.agent-runtime/external",
        "default_local_home": "~/.codex-local",
        "default_command": "",
        "capabilities": ["memory_runtime"],
    },
}

_NETWORK_PROFILE_DEFAULTS: dict[str, dict[str, Any]] = {
    "auto": {"allow_proxy_env": True, "allow_mirrors": True},
    "direct": {"allow_proxy_env": False, "allow_mirrors": False},
    "proxy": {"allow_proxy_env": True, "allow_mirrors": False},
    "mirror": {"allow_proxy_env": True, "allow_mirrors": True},
}


def normalize_path(value: str | Path | None) -> str:
    if value is None:
        return ""
    return str(value).replace("\\", "/")


def ensure_dir(path: str | Path) -> Path:
    value = Path(path).expanduser()
    value.mkdir(parents=True, exist_ok=True)
    return value.resolve()


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


def load_lock(workspace_root: str | Path) -> dict[str, Any]:
    root = find_workspace_root(workspace_root)
    payload = load_json_yaml(root / LOCK_NAME, default={})
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise RuntimeError(f"Lockfile is invalid: {root / LOCK_NAME}")
    return payload


def workspace_id(workspace_root: str | Path) -> str:
    root = find_workspace_root(workspace_root)
    manifest = load_manifest(root)
    return str(manifest.get("workspace_id") or root.name)


def workspace_api_version(workspace_root: str | Path) -> int:
    manifest = load_manifest(workspace_root)
    raw = manifest.get("workspace_api_version", manifest.get("schema_version", 1))
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"workspace_api_version is invalid: {raw!r}") from exc


def manifest_repositories(workspace_root: str | Path) -> dict[str, dict[str, Any]]:
    manifest = load_manifest(workspace_root)
    repo_specs: dict[str, dict[str, Any]] = {}
    for entry in list(manifest.get("repositories") or []):
        if not isinstance(entry, dict):
            continue
        repo_id = str(entry.get("repo_id") or entry.get("id") or "").strip()
        if repo_id:
            repo_specs[repo_id] = dict(entry)
    workspace_key = workspace_id(workspace_root)
    if workspace_key not in repo_specs:
        repo_specs[workspace_key] = {"repo_id": workspace_key, "default_relative_path": ".", "required": True}
    return repo_specs


def lock_repositories(workspace_root: str | Path) -> dict[str, dict[str, Any]]:
    payload = load_lock(workspace_root)
    raw = dict(payload.get("repositories") or {})
    result: dict[str, dict[str, Any]] = {}
    for repo_id, entry in raw.items():
        if isinstance(entry, dict):
            result[str(repo_id)] = dict(entry)
    return result


def _expand_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def _default_local_root() -> Path:
    raw = os.environ.get("AI_RUNTIME_LOCAL_HOME") or os.environ.get("CODEX_LOCAL_HOME") or str(Path.home() / ".codex-local")
    return _expand_path(raw)


def _provider_catalog(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    catalog = {key: dict(value) for key, value in _PROVIDER_DEFAULTS.items()}
    for provider, entry in dict(manifest.get("ai_providers") or {}).items():
        merged = dict(catalog.get(str(provider), {}))
        if isinstance(entry, dict):
            merged.update(entry)
        catalog[str(provider)] = merged
    return catalog


def default_runtime_provider() -> str:
    raw = str(os.environ.get("AI_RUNTIME_PROVIDER") or "").strip()
    return raw or "codex_cli"


def _default_runtime_home(provider: str, spec: dict[str, Any]) -> Path:
    if provider.startswith("codex"):
        raw = os.environ.get("AI_RUNTIME_HOME") or os.environ.get("CODEX_HOME") or str(spec.get("default_home") or _PROVIDER_DEFAULTS[provider]["default_home"])
        return _expand_path(raw)
    provider_env = str(spec.get("home_env") or "").strip()
    raw = os.environ.get("AI_RUNTIME_HOME") or (os.environ.get(provider_env) if provider_env else "") or str(spec.get("default_home") or _PROVIDER_DEFAULTS.get(provider, _PROVIDER_DEFAULTS["external"]).get("default_home"))
    return _expand_path(raw)


def _default_runtime_local_home(provider: str, spec: dict[str, Any]) -> Path:
    provider_env = str(spec.get("local_home_env") or "").strip()
    raw = os.environ.get("AI_RUNTIME_LOCAL_HOME") or (os.environ.get(provider_env) if provider_env else "") or os.environ.get("CODEX_LOCAL_HOME") or str(spec.get("default_local_home") or _default_local_root())
    return _expand_path(raw)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in values:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def machine_local_path(workspace_root: str | Path) -> Path:
    root = find_workspace_root(workspace_root)
    repo_local = root / "machine.local.yaml"
    if repo_local.exists():
        return repo_local
    return (_default_local_root() / workspace_id(root) / "machine.local.yaml").resolve()


def load_machine_local(workspace_root: str | Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    path = machine_local_path(workspace_root)
    payload = load_json_yaml(path, default=default or {})
    if not isinstance(payload, dict):
        raise RuntimeError(f"Machine-local config is invalid: {path}")
    return payload


def runtime_config(workspace_root: str | Path) -> dict[str, Any]:
    root = find_workspace_root(workspace_root)
    manifest = load_manifest(root)
    config = load_machine_local(root, default={})
    runtime_raw = dict(config.get("runtime") or {})
    legacy_toolchain = dict(config.get("toolchain") or {})
    provider = str(runtime_raw.get("provider") or config.get("runtime_provider") or "").strip()
    if not provider:
        provider = "codex_cli" if str(legacy_toolchain.get("codex_cli") or config.get("codex_home") or "").strip() else default_runtime_provider()
    catalog = _provider_catalog(manifest)
    spec = dict(catalog.get(provider) or catalog["external"])
    home = runtime_raw.get("home") or config.get("codex_home")
    local_home = runtime_raw.get("local_home") or config.get("codex_local_home")
    command = runtime_raw.get("command") or legacy_toolchain.get("codex_cli") or spec.get("default_command") or ""
    resolved_home = _expand_path(str(home)) if str(home or "").strip() else _default_runtime_home(provider, spec)
    resolved_local_home = _expand_path(str(local_home)) if str(local_home or "").strip() else _default_runtime_local_home(provider, spec)
    exports_root = runtime_raw.get("exports_root") or str((resolved_local_home / workspace_id(root) / "exports").resolve())
    capabilities = _unique([*(list(spec.get("capabilities") or [])), *(list(runtime_raw.get("capabilities") or []))])
    if command and provider.startswith("codex"):
        capabilities = _unique([*capabilities, "chat_bridge", "session_resume", "linear", "workspace_mount", "memory_runtime"])
    result = {
        "provider": provider,
        "channel": str(runtime_raw.get("channel") or spec.get("channel") or provider),
        "home": normalize_path(resolved_home),
        "local_home": normalize_path(resolved_local_home),
        "command": str(command).strip(),
        "args_template": list(runtime_raw.get("args_template") or []),
        "env": dict(runtime_raw.get("env") or {}),
        "capabilities": capabilities,
        "exports_root": normalize_path(exports_root),
        "image_arg": str(runtime_raw.get("image_arg") or "").strip(),
    }
    return result


def runtime_provider(workspace_root: str | Path) -> str:
    return str(runtime_config(workspace_root).get("provider") or "")


def runtime_home(workspace_root: str | Path) -> Path:
    return Path(str(runtime_config(workspace_root).get("home") or "")).expanduser().resolve()


def runtime_local_home(workspace_root: str | Path) -> Path:
    return Path(str(runtime_config(workspace_root).get("local_home") or "")).expanduser().resolve()


def runtime_exports_root(workspace_root: str | Path) -> Path:
    return Path(str(runtime_config(workspace_root).get("exports_root") or "")).expanduser().resolve()


def provider_export_root(workspace_root: str | Path, provider: str | None = None) -> Path:
    selected = provider or runtime_provider(workspace_root)
    return (runtime_exports_root(workspace_root) / selected).resolve()


def runtime_capability_enabled(workspace_root: str | Path, capability: str) -> bool:
    return str(capability).strip() in set(runtime_config(workspace_root).get("capabilities") or [])


def default_codex_home() -> Path:
    return _default_runtime_home("codex_cli", _PROVIDER_DEFAULTS["codex_cli"])


def default_codex_local_home() -> Path:
    return _default_local_root()


def codex_home(workspace_root: str | Path) -> Path:
    return runtime_home(workspace_root)


def codex_local_home(workspace_root: str | Path) -> Path:
    return runtime_local_home(workspace_root)


def repo_paths(workspace_root: str | Path) -> dict[str, str]:
    config = load_machine_local(workspace_root)
    return {str(key): str(value) for key, value in dict(config.get("repo_paths") or {}).items() if str(value).strip()}


def install_state_path(workspace_root: str | Path) -> Path:
    root = find_workspace_root(workspace_root)
    config = load_machine_local(root, default={})
    install = dict(config.get("install") or {})
    explicit = str(install.get("state_path") or "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    return (runtime_local_home(root) / workspace_id(root) / "install-state.json").resolve()


def load_install_state(workspace_root: str | Path) -> dict[str, Any]:
    payload = load_json_yaml(install_state_path(workspace_root), default={})
    if not isinstance(payload, dict):
        raise RuntimeError(f"Install state is invalid: {install_state_path(workspace_root)}")
    return payload


def network_config(workspace_root: str | Path) -> dict[str, Any]:
    root = find_workspace_root(workspace_root)
    manifest = load_manifest(root)
    config = load_machine_local(root, default={})
    raw = dict(config.get("network") or {})
    requested = str(raw.get("profile") or "auto").strip() or "auto"
    profiles = {key: dict(value) for key, value in _NETWORK_PROFILE_DEFAULTS.items()}
    for name, entry in dict(manifest.get("network_profiles") or {}).items():
        merged = dict(profiles.get(str(name), {}))
        if isinstance(entry, dict):
            merged.update(entry)
        profiles[str(name)] = merged
    proxy_raw = dict(raw.get("proxy") or {})
    mirrors_raw = dict(raw.get("mirrors") or {})
    resolved = requested
    if requested == "auto":
        if any(str(proxy_raw.get(key) or os.environ.get(env) or "").strip() for key, env in (("http", "HTTP_PROXY"), ("https", "HTTPS_PROXY"), ("no_proxy", "NO_PROXY"))):
            resolved = "proxy"
        elif any(str(value).strip() for value in mirrors_raw.values()):
            resolved = "mirror"
        else:
            resolved = "direct"
    profile = dict(profiles.get(resolved) or profiles["direct"])
    proxy = {
        "http": str(proxy_raw.get("http") or (os.environ.get("HTTP_PROXY") if profile.get("allow_proxy_env") else "") or "").strip(),
        "https": str(proxy_raw.get("https") or (os.environ.get("HTTPS_PROXY") if profile.get("allow_proxy_env") else "") or "").strip(),
        "no_proxy": str(proxy_raw.get("no_proxy") or (os.environ.get("NO_PROXY") if profile.get("allow_proxy_env") else "") or "").strip(),
    }
    mirrors = {
        "pip_index_url": str(mirrors_raw.get("pip_index_url") or "").strip(),
        "qt_base_url": str(mirrors_raw.get("qt_base_url") or "").strip(),
        "cuda_docs_url": str(mirrors_raw.get("cuda_docs_url") or "").strip(),
    }
    return {
        "requested_profile": requested,
        "selected_profile": resolved,
        "proxy": proxy,
        "mirrors": mirrors,
        "offline_cache_root": str(raw.get("offline_cache_root") or "").strip(),
    }
