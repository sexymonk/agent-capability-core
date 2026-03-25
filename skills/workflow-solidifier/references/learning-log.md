# Learning Log

This file records durable rules, approved workflow promotions, and avoided paths for `workflow-solidifier`.

## Durable rules

- This skill should keep evolving whenever a workflow-solidification session teaches a reusable abstraction about prompts, state machines, escalation rules, stop rules, or reflection loops.
- This skill should also maintain a reusable coaching manual for teaching other people how to train and solidify their own workflows.
- Freeze only durable, reusable, multi-step behavior; keep one-off execution details out of the meta-skill.
- Split workflow knowledge into generic template rules, domain-specific defaults, and run-local state before writing anything.
- When a trained workflow introduces a reusable human-review loop, capture both the trigger condition and the post-review learning path.
- When a workflow is corrected, update not only the owning workflow skill but also this meta-skill if the correction improves the general solidification framework.
- When a workflow-solidification session reveals a better coaching pattern, update the training manual in the same turn instead of leaving that lesson implicit.
- Include reusable example dialogue templates in the training manual so future coaching does not have to improvise the questioning structure from scratch.
- Maintain bilingual coaching guidance when the handbook is meant to transfer workflows across mixed-language or future English-first contexts.
- Maintain scenario-based coaching templates when a single generic dialogue is no longer enough for investigation, review, reporting, automation, or human-review workflows.

## Approved workflow promotions

- Promote the pattern “user trains a workflow through repeated corrections, then asks to freeze it as a reusable template/skill” into a dedicated meta-skill instead of re-deriving the framework from scratch each time.
- Promote copyable template sections for triggers, state models, agent matrices, stop states, human-review loops, and reflection writeback into the reusable references scaffold.
- Promote a dedicated handbook for coaching others through workflow training, not just a template for the final frozen workflow.
- Promote reusable coach/trainee dialogue templates and fill-in-the-blank elicitation prompts into the handbook when they prove broadly reusable.
- Promote bilingual Chinese-English explanations and scenario-specific coaching sections into the handbook when they improve transferability.

## Avoided paths

- Avoid mixing domain physics/business/tool specifics into the meta-skill when they belong in a domain-owned skill or memory entry.
- Avoid treating a one-off preference as a permanent workflow abstraction.
- Avoid freezing a workflow without explicit stop states, escalation rules, and post-correction learning sinks.
- Avoid leaving the meta-skill static; it should absorb reusable lessons from future workflow-solidification sessions.
- Avoid assuming that people already know how to train a workflow well; the coaching method itself should be documented and iteratively improved.
- Avoid leaving coaching conversations fully ad hoc when reusable dialogue patterns have already emerged.
- Avoid keeping the handbook monolingual when the workflow abstractions are likely to be reused in both Chinese and English.
- Avoid assuming one scenario template fits investigation, review, reporting, automation, and human-review workflows equally well.
## 2026-03-24 additive note

### Approved workflow promotions

- Promote repo-owned workflow skills when a trained workflow is highly domain-specific but still durable, for example an isolated QuickLauncher UI E2E regression that bundles scratch-root isolation, overlay config, watchdog supervision, and detailed issue artifacts.

### Avoided paths

- Avoid freezing UI-regression workflows as pure prompt text when they actually need deterministic helper scripts, isolation plumbing, and a formal artifact schema.
