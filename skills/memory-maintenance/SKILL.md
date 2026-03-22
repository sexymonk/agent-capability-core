---
name: memory-maintenance
description: Maintain manifest-driven shared/runtime memory frameworks that use file-backed shared source plus runtime working copies and SQLite sidecar indexes. Use when Codex needs to add or refactor memory families, validate/render/promote/query/compact memory stores, enforce shared-vs-local boundaries, or tune lifecycle rules such as dedupe, supersede, provenance, and temporal validity.
---

# Memory Maintenance

Use this skill when the task is about the memory framework itself rather than one domain memory entry.

## What this skill owns

- Memory-family contract design in `workspace.manifest.yaml`
- Shared source vs runtime working-copy boundaries
- Generic lifecycle commands:
  - `render`
  - `promote`
  - `reindex`
  - `query`
  - `validate`
  - `compact`
- Durable item lifecycle rules:
  - dedupe
  - supersede
  - temporal validity
  - provenance / evidence retention
- Sidecar retrieval design using local SQLite indexes

## Core model

- Shared file memory in Git is the only durable source of truth.
- Runtime memory under `~/.codex/memories` is a mutable working copy.
- SQLite sidecars under `~/.codex/memories/.sidecar` are derived retrieval indexes, never the primary store.
- Hot-path writes should land in runtime/local/session sinks first.
- Promotion back to shared source must stay confirmation-gated and diff-driven.

## When to use

- A workspace is introducing or refactoring `memory_families`.
- Shared/runtime render or promote logic is duplicated across scripts and should move into the generic core.
- Retrieval quality needs sidecar search, relation expansion, temporal filtering, or better validation.
- A family needs durable lifecycle fields such as `status`, `valid_from`, `valid_to`, `supersedes`, `related_refs`, or `confidence`.
- A workspace needs dry-run promotion, digests, or non-destructive compaction/defrag behavior.

## Workflow

1. Read the owning workspace manifest and identify the target `memory_families`.
2. Check the family contract against:
   - [memory-family-v1 schema](/D:/Codex/agent-capability-core/schemas/memory-family-v1.md)
   - [memory-v2 schema](/D:/Codex/agent-capability-core/schemas/memory-v2.md)
3. Implement or update the family transformer so the generic core can:
   - render shared source to runtime
   - stage shared source for promote
   - build sidecar docs/relations
   - validate domain-specific invariants
4. Prefer the generic CLI in [memory_cli.py](/D:/Codex/agent-capability-core/scripts/memory_cli.py) over ad-hoc family scripts.
5. Keep old family entry points as thin wrappers when compatibility matters.
6. Rebuild indexes and digests after render-related changes.
7. Run validation before any promote logic.
8. Keep promote non-destructive:
   - preview managed-path diffs first
   - apply only after explicit approval
   - never replace whole roots when a scoped diff can be applied

## Durable lifecycle rules

- Normalize durable memory items to the shared envelope described in `schemas/memory-v2.md`.
- Reject exact active duplicates instead of endlessly appending them.
- When a new active item overlaps an old active item in the same scope, mark the old item as `superseded` and carry the provenance forward.
- Preserve evidence/source fields instead of silently collapsing history.
- Use `valid_to` and `status` to filter historical records out of default retrieval.

## Retrieval rules

- Query sidecars first.
- Apply rule-based boosts second.
- Expand relations third when the task benefits from neighboring context.
- Filter inactive or expired records by default unless the task explicitly needs history.
- Treat digests as operator summaries, not as the authoritative source.

## Output / validation checklist

Before finishing, verify:

- manifest contract fields are complete and consistent
- shared source contains no absolute host paths
- local-only subtrees are preserved across render/promote
- sidecar rebuild succeeds
- promote defaults to dry-run preview
- compatibility wrappers still work if they existed before

## Learning maintenance

Maintain [references/learning-log.md](/D:/Codex/agent-capability-core/skills/memory-maintenance/references/learning-log.md) for this skill.

Record:

- durable rules about memory lifecycle and retrieval
- approved workflow promotions for reusable memory maintenance flows
- avoided paths such as destructive rewrite patterns or non-portable storage choices
