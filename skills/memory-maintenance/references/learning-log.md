# Learning Log

This file records durable rules, approved workflow promotions, and avoided paths for `memory-maintenance`.

## Durable rules
- Keep shared memory as the only durable source of truth; runtime working copies and SQLite sidecars are derived layers.
- Prefer manifest-driven family contracts plus one generic CLI over per-family duplicated lifecycle scripts.
- Durable memory updates should use typed lifecycle fields, dedupe exact active duplicates, and supersede overlapping active items instead of silently overwriting them.
- Promotion must validate first and default to dry-run diff preview.

## Approved workflow promotions
- Promote the shared-file-memory + runtime-working-copy + SQLite-sidecar pattern into a reusable core workflow for multi-family workspaces.

## Avoided paths
- Avoid introducing an external database as the primary source of truth when file-backed shared memory already satisfies portability and code-review needs.
- Avoid destructive full-root rewrites during promote when managed-path diffs can apply the same change safely.
