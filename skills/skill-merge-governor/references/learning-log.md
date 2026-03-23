# Learning Log

This file records durable rules, approved workflow promotions, and avoided paths for `skill-merge-governor`.

## Durable rules

- Review contributor merges for semantic overlap, not just file-level conflicts.
- Prefer one clear owning skill per trigger/workflow instead of accepting near-duplicate skill folders.
- Treat overlap-audit scripts as triage aids; always read the flagged skills before deciding.
- Extract shared deterministic helpers instead of letting sibling skills carry drifting script copies.
- When the merge-governance skill is used, prefer emitting a ready-to-edit Markdown review report instead of leaving findings only in console output.

## Approved workflow promotions

- Promote contributor-merge review for overlapping skills and redundant scripts into a dedicated meta-skill instead of relying on ad hoc manual inspection.

## Avoided paths

- Avoid using portability audit alone as a substitute for redundancy and ownership review.
- Avoid merging adjacent but distinct skills just because they touch related tools.
- Avoid accepting vague new skill descriptions that overlap an existing owner's trigger boundary.
