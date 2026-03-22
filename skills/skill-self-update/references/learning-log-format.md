# Learning Log Format

Use `references/learning-log.md` inside the owning skill when durable experience should persist.

Keep entries concise and structured. Prefer short bullets over prose.

## Recommended structure

```md
# Learning Log

## Durable rules
- 2026-03-18: Rule summary.

## Approved workflow promotions
- 2026-03-18: Workflow summary, when to use it, and why it was promoted.

## Avoided paths
- 2026-03-18: Dead end or brittle path to avoid, and the safer replacement.
```

## What belongs here

- Routing corrections that will recur.
- Output and validation rules that should persist.
- Multi-step workflows that proved reusable after user approval.
- Informative dead ends that can prevent repeated failure.

## What does not belong here

- Full chat transcripts.
- Low-value retries with no general lesson.
- Transient external facts.
- One-off personal preferences that are not meant to become standing rules.
