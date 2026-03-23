# AGENTS.md

## Repository intent

`agent-capability-core` is a portable shared workspace for reusable agent skills, supporting references, and workspace metadata. Review changes against that goal first: portability, inspectability, reproducibility, and exclusion of user-private state matter more than local convenience.

## What reviews should prioritize

### 1. Portability over machine-specific convenience

Flag changes that:

- add user-specific, machine-local, or secret material to the repo
- hard-code private paths, local usernames, tokens, or personal runtime state
- couple a generic skill to a single provider or environment without a clear portability reason

Expected pattern:

- portable assets live in `skills/`, `scripts/`, `docs/`, `schemas/`, and workspace metadata
- machine-local state stays out of version control
- `machine.local.template.yaml` may document shape, but real machine-local files must not be committed

### 2. Skill completeness and self-containment

For any new or modified skill, check that:

- the skill has a clear `SKILL.md`
- referenced scripts, assets, and docs actually exist and use repo-relative structure cleanly
- instructions do not depend on hidden personal context
- behavior changes update bundled references or learning logs when needed

Block PRs that add a skill stub without the files needed to use it.

### 3. Workspace contract correctness

When a change adds, removes, renames, or materially changes an exported skill, verify the workspace contract stays consistent:

- update `workspace.manifest.yaml` when runtime exports change
- update related docs such as `README.md` or `docs/asset-inventory.md` when user-visible inventory changes
- keep `workspace.lock.yaml` and manifest semantics coherent

Treat missing manifest/doc follow-through as a real issue, not a nit.

### 4. Fail-fast code and scripts

This repo prefers straightforward, auditable logic.

Flag changes that introduce:

- silent fallbacks
- best-effort recovery for broken invariants
- hidden retries or compatibility shims without explicit need
- defensive branching that masks real contract violations

Prefer:

- explicit assumptions
- clear errors
- one obvious execution path

### 5. Repository cleanliness

Do not allow conversation-specific clutter into the repo.

Flag additions such as:

- scratch scripts created only for a one-off task
- screenshots, generated reports, debug dumps, temporary exports, caches, or logs
- analysis notes that are not intended project documentation

Only project-owned source, tests, docs, configuration, and reusable assets belong here.

### 6. Minimal, scoped changes

Prefer narrow diffs that solve the stated problem directly.

Flag PRs that:

- mix unrelated refactors with the actual change
- rename or reorganize broad parts of the workspace without a stated reason
- modify exported skills and repo-wide metadata opportunistically

### 7. Review for private-state leaks

Pay extra attention to:

- `.system/` content accidentally copied into core assets
- personal memory workflows
- local runtime home paths
- secrets, credentials, tokens, or copied clipboard/profile data

These should generally stay outside this repository.

## Validation expectations

When relevant, prefer review comments that ask the author to verify the real contract:

- run `python .\scripts\doctor.py` after workspace/manifest changes
- confirm `link_runtime_mounts.ps1` changes still match manifest expectations
- check that referenced files in `SKILL.md` exist at the stated repo-relative paths
- verify docs still match the exported inventory

Do not demand extra verification when the diff is docs-only and clearly cannot affect runtime behavior.

## Comment style

- Prefer high-signal findings on correctness, portability, safety, and contract drift.
- Do not nitpick style unless it harms portability, clarity, or maintenance.
- Be especially strict about repo-boundary violations and missing companion updates.
- If a change is acceptable, avoid inventing speculative issues.
