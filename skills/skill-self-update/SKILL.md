---
name: skill-self-update
description: Use when a user gives a clear, generalizable correction about how a local skill should trigger or behave, or when a novel multi-step workflow is completed and the user approves continuing with it. Update the owning skill or create a narrow new skill, and record durable rules plus avoided paths under ~/.codex/skills.
---

# Skill Self Update

## Purpose

Turn execution experience into durable local skill updates.

This skill has two modes:

1. **Correction-driven update**: a user points out a reusable mistake or missing rule.
2. **Approval-driven promotion**: a user accepts a novel long workflow and wants that workflow to become reusable going forward.

This skill is mainly for evolving existing skills. It may create a **new narrow skill** when no existing skill clearly owns an approved reusable workflow.

## Use when

- The user says a previous behavior, routing rule, output rule, or workflow rule was wrong and the fix should persist.
- The user asks to "remember this correction", "update the skill", "use this rule next time", or equivalent.
- A new multi-step workflow has just succeeded, the user accepts it or asks to continue without correction, and the workflow looks reusable.
- The learning clearly maps to one or more local skills in `~/.codex/skills`, or clearly warrants a new skill.

## Do not update for

- One-off preferences that should stay local to the current task only.
- Transient facts that belong in web verification, not a skill.
- Ambiguous feedback where the durable rule is not clear.
- Requests that would weaken higher-priority system or developer instructions.
- Trivial workflows that are too short or generic to deserve a dedicated skill.

## When to create a new skill

Prefer updating an existing skill first.

Create a new skill only when all of the following are true:

1. The workflow is **novel and reusable**.
2. The workflow is **long or specialized**, such as multiple non-trivial steps, specific tools, validation loops, or a distinctive output contract.
3. No current skill cleanly owns it.

If the workflow is too project-local to justify a new skill, capture the durable lessons in the best owning skill instead of spawning unnecessary skill folders.

## Narrowest-safe-edit rule

Prefer the smallest durable change that fixes the pattern:

1. Edit `SKILL.md` frontmatter `description` when the trigger conditions are wrong.
2. Edit the `SKILL.md` body when the workflow, routing, output shape, or validation rule is wrong.
3. Edit bundled `references/` when the correction is detailed reference material.
4. Edit `scripts/` only when a deterministic helper must change.
5. Update `agents/openai.yaml` only if the UI-facing description becomes stale.
6. Create or update `references/learning-log.md` when there is informative durable learning.

## Learning log policy

For both correction-driven and approval-driven updates, keep a concise `references/learning-log.md` in the owning skill.

Record three kinds of information when they are informative and generalizable:

- **Durable rules**: routing rules, output rules, validation rules, or scope boundaries.
- **Approved workflow promotions**: successful multi-step workflows worth reusing.
- **Avoided paths**: dead ends, brittle tool choices, misleading approaches, or failed validation patterns that should not be repeated.

Do **not** dump full transcripts or noisy retry history. Keep only lessons likely to prevent future rework.

## Workflow

1. Identify whether the learning is correction-driven or approval-driven.
2. Extract the durable rule, workflow, and any meaningful avoided paths.
3. Decide whether the learning is safe to generalize.
4. Pick the owning skill. If multiple skills are involved, update the smallest set that truly owns the rule.
5. If no skill owns an approved reusable long workflow, create a narrow new skill.
6. Patch the relevant skill files directly.
7. Create or update `references/learning-log.md`.
8. Keep wording concise and reusable; do not encode the whole conversation.
9. In the reply, state what changed and link the updated local files.

## Quality bar

- Prefer stable rules over literal examples.
- Avoid overfitting to a single prompt.
- Preserve existing skill scope unless the user clearly expands or narrows it.
- If the correction changes cross-skill routing, also update any local trigger-matrix document if one is actively maintained in the current workspace.
- Prefer updating an existing skill over creating a near-duplicate skill.
- For approval-driven creation, include enough workflow detail to reproduce success, but also preserve the key avoided paths that explain what not to repeat.

## Final response

Briefly report:

- which skill was updated
- whether the update was correction-driven or approval-driven
- what durable rule changed
- whether a new skill was created or an existing one was updated
- what avoided paths were recorded
- which files were modified

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
