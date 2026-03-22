# Workflow Solidification Template

Use this file as the copyable scaffold when freezing a trained workflow into a reusable skill.

## 1) Trigger block

Capture the user wording that should activate the workflow:

- user asks to 固化流程 / 抽象模板 / 做成技能 / 沉淀提示
- user has repeatedly corrected or approved a multi-step workflow
- workflow now has stable stop states, escalation rules, and evidence requirements

## 2) Layer split

Classify every rule into one of these buckets:

### Generic workflow template

- state machine
- stop conditions
- escalation rules
- human-review loop
- reflection policy
- artifact/report categories

### Domain-specific defaults

- scene/solver/tool-specific observation priorities
- domain-specific correctness rules
- domain-specific artifact fields

### Run-local state

- current round id
- temporary hypotheses
- unresolved count
- one-off ROI or path settings

## 3) Minimal skill skeleton

```markdown
---
name: <skill-name>
description: <what the skill does and when to use it>
---

# <Skill Title>

## Goal
- <main reusable objective>

## Workflow
1. <phase 1>
2. <phase 2>
3. <phase 3>

## State model
- <state A>
- <state B>
- <state C>

## Agent policy
- <role> during <state>: <enabled/disabled + reason>

## Escalation rules
- if <condition> => <next state>

## Stop rules
- stop when <confident clean/issue/etc.>

## Artifacts
- <artifact 1>
- <artifact 2>

## Reflection rules
- after <human correction/confirmation>, write back <what> to <where>
```

## 4) Prompt/template scaffold

Use these prompts internally when extracting the durable workflow:

### A. Workflow extraction prompt

- What part of this conversation is a **stable workflow rule** rather than a one-off preference?
- What states/phases now exist?
- What triggers escalation?
- What stops the process?
- What must be produced each round?
- What must be learned after success or correction?

### B. Ownership prompt

- Does an existing skill already own this workflow?
- If yes, what is the narrowest safe update?
- If no, what is the narrowest new skill that would own it cleanly?

### C. Separation prompt

- Which rules belong in the workflow skill?
- Which rules belong in domain memory?
- Which rules belong only in run state?

### D. Human-review prompt

- When should human review be requested?
- What changes after human review?
- What evidence must be matched back to prior materials?
- What reflection must be recorded afterward?

## 5) Agent matrix template

```json
{
  "phase_agents": {
    "standard_execution": {
      "reading_agent": true,
      "analysis_agent": true,
      "modification_agent": true,
      "control_agent": true
    },
    "fast_review_execution": {
      "reading_agent": false,
      "analysis_agent": false,
      "modification_agent": false,
      "control_agent": true
    },
    "post_human_feedback": {
      "reading_agent": false,
      "analysis_agent": true,
      "modification_agent": false,
      "control_agent": false
    }
  }
}
```

Adjust the booleans per workflow, but keep the phase split explicit.

## 6) Stop/escalation template

```json
{
  "resolution_status": [
    "insufficient",
    "confident_clean",
    "confident_issue"
  ],
  "continue_rule": "continue until not insufficient",
  "human_review_trigger": {
    "metric": "unresolved_round_count",
    "threshold": 10
  },
  "post_human_followup": {
    "mode": "fast_review",
    "capture_rule": "capture every N frames"
  }
}
```

## 7) Artifact schema template

At minimum, define:

- plan
- execution report
- analysis report
- modification report
- round summary
- human review report (if the workflow supports human escalation)

For each artifact, specify:

- when it is created
- who writes it
- which fields are required
- whether it is generic or domain-specific

## 8) Reflection template

After human confirmation/correction, capture:

- what the workflow judged
- what the human judged
- where they diverged
- why the workflow missed it
- what durable update should be promoted
- whether the update belongs in:
  - workflow skill
  - domain memory
  - both

## 9) Avoided-path checklist

Record paths that should not be retried, such as:

- overfitting one-off user phrasing into permanent rules
- mixing domain physics rules into a generic orchestration skill
- leaving stop conditions implicit
- forgetting human-review aftermath
- storing temporary execution state inside the skill

## 10) Finish criteria

The workflow is solidified only when a future agent can reuse it without rereading the whole training conversation.

## 11) Meta-skill self-update checkpoint

Before closing a workflow-solidification task, ask:

- Did this session reveal a better generic template section?
- Did this session reveal a reusable escalation/stop/human-review pattern?
- Did this session reveal a new avoided path for future workflow freezing?

If yes, update `workflow-solidifier` itself in the same turn.

If the session also taught a better way to coach humans to train their own workflows, update [workflow-training-manual.md](/C:/Users/13227/.codex/skills/workflow-solidifier/references/workflow-training-manual.md) too.
