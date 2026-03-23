# Review Checklist

Use this checklist when reviewing contributor merges that touch skills or shared helpers.

## 1. Lock the incoming scope

- Identify `base...head` or the explicit changed path list.
- List touched skill folders under `skills/`.
- List touched helper scripts under any `scripts/` directory.

## 2. Run the overlap audit

Examples:

```powershell
python .\skills\skill-merge-governor\scripts\audit_merge_overlap.py --repo-root . --base-ref origin/main --head-ref HEAD
python .\skills\skill-merge-governor\scripts\audit_merge_overlap.py --repo-root . --changed-path skills\new-skill\SKILL.md --changed-path skills\new-skill\scripts\helper.py
python .\skills\skill-merge-governor\scripts\audit_merge_overlap.py --repo-root . --base-ref origin/main --head-ref HEAD --report-out D:\codex_aux\agent-capability-core\merge-review.md
```

## 3. Classify each finding

### Resolution: merge into existing skill

Choose this when:

- trigger wording overlaps heavily
- the workflow contract is effectively the same
- the incoming skill mainly rephrases an existing one

Typical action:

- fold the new instructions into the existing owner skill
- delete or decline the duplicate skill folder
- preserve any genuinely better scripts or references by moving them into the owner skill

### Resolution: keep separate with sharper boundary

Choose this when:

- the trigger is distinct
- the output contract is distinct
- combining them would make one skill too broad

Typical action:

- tighten `description:` frontmatter
- add explicit “do not use for” wording in the body if needed
- rename scripts or references to reduce confusion

### Resolution: extract shared helper

Choose this when:

- both sides need the same deterministic code or structured reference
- drift will reappear if both copies stay in place

Typical action:

- create one shared script/reference
- update both skills to call or reference the shared asset
- remove the duplicate copies

### Resolution: reject until clarified

Choose this when:

- ownership is fuzzy
- trigger wording is too broad
- the contribution creates unresolved ambiguity

Typical action:

- block merge
- report the exact conflict pair and what must be clarified

## 4. Final review questions

- What user request triggers the new or changed skill?
- Which existing skill already covers that request?
- If both remain, what exact wording differentiates them?
- Is any new helper script functionally redundant with an existing one?
- Would future contributors know which owner skill to edit?

If any answer is unclear, the merge is not governed yet.

## 5. Emit the review artifact

- Prefer generating a Markdown report with `--report-out`.
- Fill in reviewer decisions and follow-up actions in the generated report.
- Keep the report structure aligned with [report-template.md](report-template.md).
