# Source Selection

Use this checklist when deciding whether an online skill or script should be reused locally.

## Search order by source type

Apply this order by default.

### Skills

1. Official skill repositories
2. Official docs with starter templates
3. Maintained GitHub repos with clear ownership
4. Lower-trust examples only if better sources fail

### Scripts

1. Official docs and linked examples
2. Official or vendor repos
3. Package registries and linked source repos
4. Maintained public repos
5. Lower-trust snippets only as last-resort inspiration

## Prefer these sources first

1. Official repository or vendor-maintained example
2. Official documentation with a linked reference implementation
3. Trusted package registry example or release asset
4. Well-maintained public repository with clear license and recent activity

## Candidate scoring questions

- Is the source primary and attributable?
- Is the license clear and acceptable for local reuse?
- Is the implementation narrow enough to adapt without dragging in unrelated complexity?
- Does it match the local OS, shell, language, and dependency stack?
- Is it maintained recently enough to trust?
- Can it be validated locally after adaptation?

## Quick triage table

| Criterion | Prefer | Avoid |
|---|---|---|
| Ownership | official vendor, official org, known maintainer | reposts, mirrors, unattributed copies |
| License | explicit and compatible | missing, ambiguous, or restrictive for the intended use |
| Scope | narrow and directly relevant | broad frameworks when a small utility is enough |
| Freshness | recently maintained or clearly still valid | stale, archived, or obviously broken |
| Adaptation cost | light local edits | heavy surgery that exceeds scratch implementation cost |
| Validation | easy to test locally | hard to validate in the local environment |

## Prefer adaptation over wholesale copying

- Vendor the smallest useful subset.
- Rewrite hard-coded paths, commands, and prompts.
- Remove stale examples, demos, and extra dependencies that do not serve the current user need.

## Red flags

Avoid or downgrade candidates when:

- the license is missing or unclear
- the source is a copy of a copy rather than an original repo
- the code is obviously stale or broken
- the implementation is much broader than the user's request
- local adaptation would be more fragile than a clean reimplementation
- the package or repo is abandoned and has known broken installation or runtime paths

## Fallback trigger

Generate from scratch only after a real search has been attempted and the best candidates are still unsuitable.
