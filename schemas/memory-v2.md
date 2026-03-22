# Memory schema v2

All shared memory files in Git are stored as JSON-compatible YAML.

## v2 rules

- `repo_roots` -> `repo_ids`
- shared repo-bound file paths are stored relative to the logical repo root
- `memory_file` values are stored relative to the owning memory family root
- host-specific auxiliary artifact paths must not be committed
- runtime copies under `~/.codex/memories` may be rendered with absolute paths for backward-compatible tool execution
