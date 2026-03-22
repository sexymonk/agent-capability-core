# Memory schema v2

All shared memory files in Git are stored as JSON-compatible YAML.

## v2 rules

- `repo_roots` -> `repo_ids`
- shared repo-bound file paths are stored relative to the logical repo root
- `memory_file` values are stored relative to the owning memory family root
- host-specific auxiliary artifact paths must not be committed
- runtime copies under `~/.codex/memories` may be rendered with absolute paths for backward-compatible tool execution

## Durable item envelope

Typed durable memory entries should normalize to this envelope wherever a family stores long-lived items:

- `id`
- `memory_type`
- `summary`
- `details`
- `evidence`
- `source`
- `confirmed_at`
- `confidence`
- `importance`
- `status` (`active`, `superseded`, `archived`)
- `valid_from`
- `valid_to`
- `tags`
- `related_refs`
- `supersedes`

Families may add domain fields on top of this envelope, but they should not drop these lifecycle/provenance fields once a family has opted into v2 durable items.

## Lifecycle rules

- Shared files in Git remain the only durable source of truth.
- Runtime copies under `~/.codex/memories/<family>` are mutable working copies.
- Sidecar indexes under `~/.codex/memories/.sidecar/<workspace>/<family>.sqlite` are derived caches only.
- New runtime writes should prefer hot-path local/session sinks first; promotion back to shared source is confirmation-gated.
- Overlapping active items in the same scope should supersede older items instead of silently overwriting or endlessly append-duplicating them.
- Promotion should validate first, preview a managed-path diff, and only write shared source when explicitly applied.

## Validation rules

- Shared source must not contain absolute machine paths.
- Shared `repo_id` / `repo_ids` values must resolve against the owning workspace manifest.
- Shared `memory_file` references must remain relative to the owning family root.
- Shared repo file references must remain repo-relative.
