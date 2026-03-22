---
name: safe-commit-sync
description: Safely scope, commit, rebase, and push Git changes when the user wants minimal collateral impact, explicit conflict policy, or mixed superproject/submodule updates. Use for requests like 提交commit, 重新提交, push到远端, 合并主分支后再提交, or 只提交这些文件. Prefer mainline changes when integrating main into local work, prefer local recent changes when replaying local commits onto a moved remote branch, and verify untouched files are not altered.
---

# Safe Commit Sync

## Goal

Commit and push the intended Git changes while minimizing collateral impact on unrelated files, teammates' recent work, and untouched paths.

## Use this skill when

- The user asks to commit, recommit, rebase, merge, or push selected files.
- The user gives explicit conflict rules, especially asymmetric rules for `main` versus a moved remote branch.
- The task mixes superproject changes with submodule content changes.
- The user wants to avoid touching files they did not recently modify.

## Workflow

1. **Lock the intended scope**
   - Build an explicit target path list from the user's request.
   - Stage and commit only those paths.
   - If the user names a directory, include only the currently modified files under that directory plus any explicitly named related files.

2. **Split intended work from unrelated work**
   - Commit the intended changes first when possible.
   - Stash unrelated local tracked and untracked work before rebase/push.
   - Do not assume a superproject stash will fully clear submodule worktrees; unrelated submodule dirtiness may remain visible even when the superproject is ready for replay.

3. **Handle submodules first**
   - If the intended scope includes files inside a submodule, commit and push the submodule change first on top of the submodule's latest remote head.
   - Then stage the superproject gitlink update together with the related superproject code changes.

4. **Prepare the local commit set**
   - Review `git diff --stat -- <paths>` before staging.
   - Review `git diff --cached --name-status` before each commit.
   - Refuse to include unrelated paths just because they are already dirty.

5. **Reconcile with upstream using semantic conflict rules**
   - Read the actual remote head directly before pushing.
   - If integrating `main` into local work, prefer the `main` side on conflicts.
   - If replaying recent local commits onto a moved remote target branch, prefer the replayed local changes on conflicts.
   - Reason semantically, not by memorizing `ours`/`theirs` labels. In merge, `ours` is the checked-out branch. In rebase/cherry-pick, the replayed local commit is the side that Git labels as `theirs`.
   - For the “remote moved, local wins” case during rebase/cherry-pick, `-X theirs` matches the intended policy.
   - Never overwrite unexpected new remote commits with a blind force-push unless the user explicitly asked to rewrite published history.

6. **Validate blast radius before push**
   - Verify the staged or rebased commit file list exactly matches the intended scope.
   - Diff outside the target scope and stop if untouched paths changed.
   - Check whether the proposed commit would modify files the user did not recently edit; if yes, inspect and justify them before continuing.
   - Keep teammates' unrelated recent changes intact whenever possible.

7. **Push and restore the workspace**
   - If the named remote goes through an auth-breaking proxy but the same GitHub repo is reachable directly, push to the equivalent direct GitHub URL and verify the branch head afterward.
   - If you bypass the named remote, update the corresponding local tracking ref after a verified push.
   - Restore unrelated stashed work after the push and keep or drop the stash only after confirming the workspace is back to the expected state.

## Templates and checklists

- Use [templates-and-checklists.md](/C:/Users/13227/.codex/skills/safe-commit-sync/references/templates-and-checklists.md) for:
  - standard commit message templates
  - submodule-first commit/push command patterns
  - merge-main validation checklist
  - rebase-onto-moved-remote validation checklist
- Preserve the original commit subject when replaying a local commit after rebase/cherry-pick unless the scope materially changed.
- Prefer short, scope-revealing commit subjects over generic messages such as `update` or `fix issues`.

## Validation checklist

Before finishing, verify all of the following:

- the intended path list is explicit
- the staged file list contains only intended paths
- submodule content is pushed before the superproject gitlink if applicable
- the remote target head was checked immediately before push
- commits outside the target scope are unchanged
- untouched local files were not accidentally pulled into the commit
- unrelated local changes were restored afterward

## Avoided paths

- Do not assume `git checkout <commit> -- <dir>` reproduces deletions; remove the tree first or use exact tree replacement.
- Do not treat `ours` and `theirs` as stable meanings across merge, rebase, and cherry-pick.
- Do not push through a proxy remote that cannot authenticate if the direct GitHub URL for the same repo and branch is available and verifiable.
- Do not overwrite unexpected remote movement; rebase or cherry-pick local commits onto the moved remote head first.
- Do not let an explicit path scope drift and capture teammates' unrelated files.
