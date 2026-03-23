---
name: skill-merge-governor
description: Audit incoming contributor merges that add or modify skills, scripts, references, or workflow assets. Use when Codex needs to review a branch, PR, or local merge for near-duplicate skills, overlapping triggers, ambiguous ownership, redundant helper scripts, or reusable logic that should be unified before merging.
---

# Skill Merge Governor

Prevent contributor merges from silently creating overlapping skills, ambiguous triggers, duplicate scripts, or fragmented ownership.

## Goal

Given an incoming branch, PR, or local diff that touches `skills/`, `scripts/`, `references/`, or other workflow assets:

1. find likely overlaps with existing repo content
2. decide whether to merge into an existing skill, keep a distinct boundary, or extract shared helpers
3. leave behind a clear merge decision with minimal ambiguity

## Core rules

- Treat overlap detection as a **merge-governance** task, not a portability audit and not a generic Git conflict task.
- Prefer updating or extending an existing skill over accepting a near-duplicate skill with fuzzy boundaries.
- Keep legitimately distinct skills separate when their trigger, owner, or output contract is materially different.
- Prefer extracting shared logic into a script/reference helper when two skills need the same deterministic behavior.
- Do not merge two skills just because they use adjacent tools; merge only when the user-facing trigger and workflow contract substantially overlap.
- Do not accept a new skill with a vague description that could trigger where an existing skill already owns the request.

## Workflow

1. Identify the review scope.
   - Prefer a concrete diff such as `base...head`, a PR patch, or a list of changed paths.
   - Focus first on files under `skills/`, then repo-level `scripts/`, `docs/`, and schemas that support those skills.
2. Run `scripts/audit_merge_overlap.py` in this skill with either:
   - `--base-ref <base> --head-ref <head>` for Git diff review, or
   - `--changed-path <path>` for explicitly supplied paths.
   - add `--report-out <path>` when you want a ready-to-review Markdown merge report
3. Review the overlap report.
   - Treat the script as triage, not as the final decision-maker.
   - Read the SKILL.md files for the flagged pairs before deciding.
4. Resolve each finding using [references/review-checklist.md](references/review-checklist.md).
   - choose one of: **merge into existing**, **keep separate with sharper boundary**, **extract shared helper**, or **reject until clarified**
5. If accepting the contribution, patch the repo so the final state has one clear owner per trigger/workflow.
6. If declining or deferring the merge, report the exact ambiguity or redundancy that blocked acceptance.
7. Update this skill's learning log when the session reveals a reusable governance rule or avoided path.

## Decision standard

### Merge into an existing skill when

- the new skill's trigger language substantially overlaps an existing skill
- the main workflow is the same with only minor wording or asset differences
- the new script duplicates an existing helper with only superficial changes

### Keep a separate skill when

- the trigger boundary is clear and narrow
- the workflow or output contract is materially different
- combining them would make the owner skill too broad or vague

### Extract a shared helper when

- two skills need the same script or reference logic
- duplication is deterministic rather than purely instructional wording
- a shared helper reduces future drift without collapsing distinct skills

## Required checks

- Compare incoming skill descriptions against existing skill descriptions.
- Compare incoming script names and exact file hashes against existing scripts.
- Check whether new references merely restate an existing workflow with different wording.
- Verify that `workspace.manifest.yaml` and docs stay consistent if a skill is added, renamed, merged, or removed.
- Reject unresolved ambiguity instead of tolerating it.

## Validation checklist

Before finishing, verify:

- every added or modified skill has a clear owner and trigger boundary
- no accepted near-duplicate skill remains without explicit justification
- shared scripts are unified or intentionally duplicated with documented reason
- manifest/docs were updated if exported skills changed
- the final report names the chosen resolution for every flagged overlap

## References

- Use [references/review-checklist.md](references/review-checklist.md) for the merge review sequence and resolution matrix.
- Use [references/report-template.md](references/report-template.md) for the expected review-report shape.
- Use [references/learning-log.md](references/learning-log.md) to preserve durable governance rules and avoided paths.
