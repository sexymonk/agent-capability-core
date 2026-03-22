---
name: workflow-solidifier
description: Convert a user-trained multi-step workflow into a reusable Codex skill or a stable workflow template. Use when the user asks to 固化 workflow, 抽象模板流程, 沉淀流程与提示, 把当前流程做成技能, 将多轮修正变成可复用框架, or quickly freeze an orchestration pattern for future tasks.
---

# Workflow Solidifier

Use this skill when the user is not asking for one more execution of a workflow, but for the **workflow itself** to be stabilized, templated, and made reusable.

## Goal

Turn repeated user corrections, approvals, and workflow refinements into a reusable package with:

- trigger wording
- stable rules
- phase/state model
- agent participation rules
- escalation and stop conditions
- artifact/report schema
- human-review loop
- reflection and memory writeback rules

## Core rules

- Promote only **durable, reusable, multi-step** behavior.
- Split workflow knowledge into three layers:
  - **generic workflow template**
  - **domain-specific defaults**
  - **run-local state**
- Put:
  - orchestration rules in a skill
  - domain mechanics in the owning domain skill or solver memory
  - temporary execution state in run-state files, not in the skill
- Prefer updating an existing owning skill; create a new skill only when no current skill clearly owns the workflow.
- This skill should keep learning from future workflow-solidification sessions rather than remaining static.

## Self-update rules

After each meaningful workflow-training session, update this skill when there is reusable learning about:

- extracting durable workflow rules from conversation
- splitting generic workflow rules from domain-specific rules
- defining stop states, escalation gates, or human-review loops
- structuring artifact schemas or reflection writeback
- improving multilingual or scenario-based coaching scaffolds for teaching others
- identifying over-generalization that should be avoided

Promote that learning into:

- `SKILL.md` when the operating process changes
- [references/workflow-template.md](/C:/Users/13227/.codex/skills/workflow-solidifier/references/workflow-template.md) when the reusable scaffold improves
- [references/workflow-training-manual.md](/C:/Users/13227/.codex/skills/workflow-solidifier/references/workflow-training-manual.md) when the coaching handbook for training others improves
- [references/learning-log.md](/C:/Users/13227/.codex/skills/workflow-solidifier/references/learning-log.md) when the session yields durable rules, approved promotions, or avoided paths

Do not absorb one-off domain specifics from a single workflow into this meta-skill unless they clearly generalize across workflows.

## Fast path

When a workflow has already been trained in conversation, do this in order:

1. Extract the durable workflow deltas.
2. Classify each delta as:
   - generic template
   - domain-specific rule
   - run-local setting
3. Decide whether to:
   - update an existing skill
   - or create a narrow new skill
4. Encode the reusable framework into:
   - `SKILL.md` for the operating rules
   - `references/` for copyable templates and prompt scaffolds
   - optional scripts only if deterministic scaffolding is repeatedly needed
5. Add a learning log with:
   - durable rules
   - approved workflow promotions
   - avoided paths
6. Report what was frozen and where it now lives.

## What to extract from a trained workflow

Always try to capture these:

- **Trigger phrases**
  - what user wording should activate the workflow
- **Objective**
  - what outcome ends the workflow
- **Stop states**
  - when to stop because the task is confidently done
- **State machine**
  - phases, modes, escalation states, fallback states
- **Agent matrix**
  - which roles act in which phase
  - which roles must be skipped in some phases
- **Evidence schema**
  - what artifacts each round or phase must produce
- **Decision gates**
  - what upgrades or downgrades the workflow
- **Human review policy**
  - when to ask for human review
  - what happens after human feedback
- **Reflection loop**
  - what must be learned after confirmation/correction
- **Memory sinks**
  - which rules belong in skill memory vs domain memory

## Output pattern

For a reusable workflow skill, keep `SKILL.md` lean and put copyable scaffolds in [references/workflow-template.md](/C:/Users/13227/.codex/skills/workflow-solidifier/references/workflow-template.md).

Use [references/learning-log.md](/C:/Users/13227/.codex/skills/workflow-solidifier/references/learning-log.md) to record:

- durable rules
- approved workflow promotions
- avoided paths

Use [references/workflow-training-manual.md](/C:/Users/13227/.codex/skills/workflow-solidifier/references/workflow-training-manual.md) when the user wants a guide that can teach other people how to train and freeze their own workflows.
That handbook should evolve when bilingual guidance or scenario-based coaching templates materially improve reuse.

## Validation checklist

Before finishing, verify the new or updated workflow can answer:

- When does this workflow start?
- What are its stable phases?
- When does it escalate?
- When does it stop?
- What artifacts must exist after each phase?
- When does human review happen?
- What gets learned after human confirmation/correction?
- Which parts are generic vs domain-specific?

If any of those are unclear, the workflow is not solidified yet.

Also check whether the current solidification session taught this skill itself something reusable. If yes, update the skill in the same turn.

## Reuse template

When building or updating a workflow skill, follow the scaffold in [references/workflow-template.md](/C:/Users/13227/.codex/skills/workflow-solidifier/references/workflow-template.md) instead of inventing a fresh structure every time.
