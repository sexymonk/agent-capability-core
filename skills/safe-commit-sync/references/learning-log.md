# Learning Log

This file records durable rules, approved workflow promotions, and avoided paths for `safe-commit-sync`.

## Durable rules

- When integrating `main` into local work, resolve overlapping conflicts in favor of the `main` side.
- When replaying recent local commits onto a remote branch that moved, resolve overlapping conflicts in favor of the replayed local changes.
- Decide conflict policy semantically for the operation at hand instead of memorizing `ours`/`theirs` labels without context.
- Before every commit, verify that the staged file list is exactly the intended scope and that untouched paths stay unchanged.
- Prefer explicit path staging and explicit outside-scope diff checks to avoid pulling in teammates' unrelated work.
- If the intended scope includes a submodule path, publish the submodule commit first and only then commit the superproject gitlink.
- If a proxy remote cannot authenticate but the same GitHub repository is reachable directly, use the direct GitHub URL and verify the branch head after push.
- Keep reusable commit message templates in the skill so narrow commits do not drift into vague or scope-mismatched subjects.
- Maintain separate reusable checklists for “merge main into local work” and “replay local commits onto a moved remote branch”.
- Keep a copyable submodule-first command pattern in the skill because that sequence is easy to get wrong under pressure.

## Approved workflow promotions

- Promote the reusable workflow "scope local changes -> commit intended paths -> stash unrelated work -> rebase/cherry-pick onto moved remote with asymmetric conflict rules -> push -> restore stash" into a dedicated Git skill.
- Promote the reusable rule set "main integration prefers main; replay onto remote prefers local" into a first-class commit/push workflow instead of resolving it ad hoc.
- Promote submodule-aware commit/push handling into the workflow so asset changes under nested repos can be published safely with the matching superproject gitlink.

## Avoided paths

- Avoid assuming `git checkout <commit> -- <dir>` reproduces deletions; it does not reliably drop files absent from the source tree.
- Avoid using `ours`/`theirs` as if they always point to the same semantic side; they flip meaning across merge versus rebase/cherry-pick.
- Avoid blind force-push when the remote head moved unexpectedly; rebase or cherry-pick local commits onto the new remote head first.
- Avoid staging all dirty files in a repository when the user asked for a narrow commit scope.
- Avoid relying on a superproject stash to fully clean submodule worktrees; submodule dirtiness can remain visible and must be interpreted carefully.
- Avoid vague commit subjects that hide the actual scope of a narrow replayed change.
