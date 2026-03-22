# Learning Log

This file records durable rules, approved workflow promotions, and avoided paths for `skill-portability-auditor`.

## Durable rules
- 2026-03-22: Audit skills for portability by checking wording, provider assumptions, runtime coupling, and path coupling.
- 2026-03-22: Prefer capability-based wording over model-name-based wording when the capability is what really matters.
- 2026-03-22: Keep intentionally vendor-specific skills explicit; do not force fake generality onto product-specific skills.

## Approved workflow promotions
- 2026-03-22: Promote the workflow `audit -> classify -> rewrite or preserve -> validate triggers -> update learning log` as the default pattern for this skill.

## Avoided paths
- 2026-03-22: Do not blanket-replace every provider or model name without checking whether the skill is provider-specific by design.
- 2026-03-22: Do not make skills so generic that their trigger conditions become vague.
- 2026-03-22: Do not treat the audit script as the final authority; use it as triage and apply human judgment.
