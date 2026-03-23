# Merge Review Report Template

Use this shape for the final review artifact when auditing contributor merges for overlap and redundancy.

## Title

`# Merge Review Report: <scope>`

Examples:

- `# Merge Review Report: origin/main...HEAD`
- `# Merge Review Report: skills/new-skill/*`

## Summary

- review scope
- changed skills
- changed scripts
- count of flagged skill overlaps
- count of flagged script overlaps
- merge recommendation: `approve`, `approve with consolidation`, or `block until clarified`

## Scope

- base/head refs or explicit changed paths
- repo root
- threshold used by the audit script

## Flagged skill overlaps

For each finding include:

- incoming skill path
- matched existing skill path
- overlap scores
- reviewer decision
- rationale
- follow-up action

## Flagged script overlaps

For each finding include:

- incoming script path
- matched existing script path
- exact duplicate or near-duplicate status
- reviewer decision
- rationale
- follow-up action

## Decision log

Use one row per final decision:

| Area | Finding | Resolution | Owner | Follow-up |
| --- | --- | --- | --- | --- |

## Blocking issues

List unresolved ambiguity, ownership conflicts, or missing cleanup work. Write `None.` if there are no blockers.

## Final recommendation

State exactly one:

- `Approve`
- `Approve after listed consolidation changes`
- `Block until clarified`
