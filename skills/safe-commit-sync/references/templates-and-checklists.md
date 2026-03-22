# Templates and Checklists

Use this reference when the workflow already triggered and you need copyable patterns rather than re-deriving them.

## Commit message templates

Prefer concise subjects that reveal both scope and intent.

- `Update <area> for <purpose>`
  - Example: `Update SIISPH_ljy demos for Turbing test`
- `Fix <issue> in <area>`
  - Example: `Fix compilation issue in SemiAnalyticalDensitySolver`
- `Add <asset> for <feature>`
  - Example: `Add Turbing pipeline asset`
- `Sync <area> with <source>`
  - Example: `Sync Turbing demo with latest solver changes`

Rules:

- Reuse the original local commit subject when replaying that same change after rebase/cherry-pick unless the scope changed.
- If a superproject commit includes a submodule gitlink plus related code, mention both in the subject when feasible.
- Avoid one-word subjects like `update`, `fix`, or `adjust`.

## Explicit-scope commit pattern

```powershell
git diff --stat -- <paths>
git add -- <paths>
git diff --cached --name-status
git commit -m "<subject>"
```

Before committing:

- verify that every staged path is intentional
- verify that no untouched path outside scope appears in the staged diff

## Submodule-first pattern

When the intended scope includes files inside a submodule:

```powershell
# 1) inspect and update the submodule worktree
git -C <submodule> status --short --branch
git -C <submodule> diff --stat -- <submodule-paths>

# 2) commit inside the submodule
git -C <submodule> add -- <submodule-paths>
git -C <submodule> diff --cached --name-status
git -C <submodule> commit -m "<submodule-subject>"

# 3) push the submodule first
git -C <submodule> push <remote-or-direct-url> HEAD:<branch>

# 4) then commit the superproject gitlink plus related code
git add -- <superproject-paths> <submodule>
git diff --cached --name-status
git commit -m "<superproject-subject>"
```

## Merge-main checklist

Use this when integrating `main` into local work.

1. Read the actual `main` head immediately before merge.
2. Stash unrelated local work.
3. Merge `main` into the working branch.
4. For overlapping conflicts, prefer the `main` side.
5. Recheck the intended local changes afterward; restore only the desired local deltas.
6. Diff outside the intended scope and stop if untouched paths changed.
7. Run any targeted build/test checks needed for the touched area.

## Replay-onto-moved-remote checklist

Use this when the remote target branch advanced after local commits were created.

1. Read the actual remote head immediately before replay.
2. Stash unrelated local work.
3. Rebase or cherry-pick the local commits onto the moved remote head.
4. For overlapping conflicts, prefer the replayed local changes.
5. Preserve teammates' unrelated remote commits.
6. Verify the rebased commit file lists still match the intended local scope.
7. Push without force if the replay produced a fast-forward from the new remote head.

## Outside-scope blast-radius checks

Use at least one of these before push:

```powershell
git diff --name-status <base> HEAD -- . ':(exclude)<target-scope>'
git show --name-only --format=oneline HEAD
git diff --cached --name-status
```

Stop and inspect if:

- a path outside the intended scope changed
- a teammate-owned area changed unexpectedly
- a file the user did not recently edit appears in the proposed commit
