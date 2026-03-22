# Memory family contract v1

`workspace.manifest.yaml` may declare `memory_families[*]` entries to opt a workspace into the generic memory framework.

## Required manifest fields

Each family should define:

- `name`
- `schema_version`
- `runtime_target`
- `source`
- `shared_subtrees`
- `local_only_subtrees`
- `transformer`
- `index_fields`
- `entity_kinds`

## Field meanings

- `name`: stable family identifier used by CLI routing
- `schema_version`: shared source schema version for the family
- `runtime_target`: directory name under `~/.codex/memories`
- `source`: shared source directory inside the workspace
- `shared_subtrees`: relative paths managed by render/promote
- `local_only_subtrees`: runtime-only paths that promote must preserve
- `transformer`: `path/to/module.py:callable` factory that returns the family contract
- `index_fields`: important fields expected to appear in indexed records
- `entity_kinds`: high-level record kinds that the family emits into the sidecar

## Transformer contract

The `transformer` callable must return a dict with at least:

- `managed_paths`
- `render(...)`
- `stage_source(...)`
- `build_index(...)`

Optional:

- `validate(...)`

### `render(...)`

Render shared source into the runtime working copy. The runtime working copy may include local conveniences such as absolute paths or expanded compatibility fields.

### `stage_source(...)`

Build a temporary staged shared tree from the runtime working copy. Promotion compares the staged tree against the tracked shared source and generates a managed-path diff before any apply step.

### `build_index(...)`

Return:

- `docs`: normalized sidecar records
- `relations`: optional relation edges for expansion/routing

The SQLite sidecar is a derived retrieval layer, not a durable source of truth.

### `validate(...)`

Return structured issues for family-specific invariants that generic validation cannot infer, such as cross-family references or domain-specific file ownership rules.

## Standard lifecycle commands

The generic CLI in [scripts/memory_cli.py](/D:/Codex/agent-capability-core/scripts/memory_cli.py) exposes:

- `render`
- `promote`
- `reindex`
- `query`
- `validate`
- `compact`

Expected semantics:

- `render`: refresh runtime copies, sidecar indexes, and digest files
- `promote`: validate, stage, and diff runtime changes back to shared source; default to dry-run preview
- `reindex`: rebuild sidecar indexes without re-rendering
- `query`: search sidecars, then apply relation expansion and lifecycle filtering
- `validate`: check shared source portability and family-specific invariants
- `compact`: refresh digest / hot-summary style runtime outputs

## Shared vs local boundary

- Shared source: durable, reviewable, repo-portable memory only
- Runtime working copy: mutable hot-path state used by skills and scripts
- Local-only subtrees: session notes, scratch analysis, review packets, or other host-specific working state that must survive render/promote without entering Git
