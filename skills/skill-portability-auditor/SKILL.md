---
name: skill-portability-auditor
description: Use when a user wants to audit local skills for portability across different models or agent environments, or wants non-portable skills rewritten so other people can reuse them outside the current model-specific setup.
---

# Skill Portability Auditor

## Overview

Audit local skills for cross-model portability, then rewrite the ones that are too tied to one model, one vendor, or one agent runtime.

The goal is **portable reuse**, not fake uniformity. If a skill is inherently tied to a specific product or API, keep that fact explicit, but isolate the provider-specific parts and avoid leaking that specificity into the generic workflow language.

## When to use

- The user asks whether local skills are reusable across different models or agent environments.
- The user wants local skills rewritten so they can work beyond the current model/runtime.
- The user wants an audit of model-specific wording, provider-specific assumptions, or runtime-specific coupling inside `SKILL.md` files.

## Do not over-generalize

Do **not** flatten genuinely provider-specific skills into fake generic skills.

Examples that may remain provider-bound by design:
- product-specific docs skills
- API smoke-test skills for a specific vendor
- media or speech skills tied to one vendor API
- app-builder skills for one product ecosystem

For those, prefer this pattern:
1. Keep the provider-specific purpose explicit.
2. Make the core workflow language neutral where possible.
3. Move provider-specific commands, credentials, and adapters into clearly marked sections.

## Workflow

1. Run `scripts/audit_skill_portability.py` against the local skills root.
2. Classify each skill into one of four buckets:
   - portable as-is
   - needs wording generalization
   - intentionally provider-bound but can be cleaned up
   - needs deeper restructuring
3. Use [references/portability-principles.md](references/portability-principles.md) to decide how to rewrite each skill.
4. For skills that should generalize, prefer these edits:
   - replace model names with capability language where possible
   - replace runtime-specific references like "Codex should" with neutral terms like "the agent"
   - separate generic workflow rules from provider-specific adapters
   - keep examples concrete, but avoid implying only one model can execute the workflow
5. For skills that are intentionally vendor-specific, preserve their purpose while isolating the specific commands, keys, and product names.
6. Validate that the rewritten skill still has clear trigger conditions and does not become vague.
7. Update the owning skill's `references/learning-log.md` with durable rules, promotions, or avoided paths.
8. Report what was audited, what was rewritten, and which skills were intentionally kept provider-specific.

## Rewrite rules

- Prefer **capability-based** wording over **model-name-based** wording.
  - Good: "requires file access and shell execution"
  - Worse: "works with Codex only"
- Prefer **simple, direct, structured instructions** over model-specific prompt tricks.
- Prefer **separating core workflow from adapters**.
- Avoid assuming one exact message hierarchy or one exact UI unless the skill truly depends on it.
- Keep triggers concrete; portability should not remove precision.
- Prefer relative or placeholder paths in general guidance, but keep local absolute paths when they are essential for the actual local setup.

## Audit helper

Run `scripts/audit_skill_portability.py` first. It flags likely portability risks such as:
- model or vendor names
- Codex-specific phrasing
- absolute local path coupling
- runtime-specific assumptions

Treat the script as a triage aid, not the final decision-maker.

## References

Read [references/portability-principles.md](references/portability-principles.md) when deciding whether a skill should be generalized or intentionally remain provider-bound.

## Learning maintenance

Maintain `references/learning-log.md` for this skill.

Update it when:
- a user gives a reusable correction about this skill's trigger, scope, workflow, output, validation, or routing
- a novel multi-step workflow using this skill is approved for reuse
- a failed or brittle path reveals an avoided path worth preserving

Keep entries concise and generalizable. Record:
- durable rules
- approved workflow promotions
- avoided paths

Do not store full transcripts, transient facts, or one-off preferences.
