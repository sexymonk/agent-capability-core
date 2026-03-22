# Search Templates

Use these templates to search faster and more consistently when building a new skill or script.

## Search strategy

Search in short waves:

1. **Official / primary sources first**
2. **Package ecosystem sources second**
3. **General GitHub search third**
4. **Low-trust examples only if needed**

Do not spend too long on broad search before narrowing the target.

## Skill-oriented query templates

Use these when the user wants a reusable skill, workflow package, or Codex-style capability.

### Official and curated first

- `site:github.com/openai/skills <task> skill`
- `site:github.com <product-or-vendor> skill <task>`
- `<product> official examples <task>`
- `<framework> starter template <task>`

### GitHub follow-up

- `site:github.com <task> skill`
- `site:github.com <task> codex skill`
- `site:github.com <task> workflow automation`

## Script-oriented query templates

Use these when the user wants a script, CLI helper, utility, converter, extractor, or automation script.

### Official docs first

- `<tool> official docs <task>`
- `<tool> example <task>`
- `<library> reference implementation <task>`

### Package registry second

- `site:pypi.org <task> python`
- `site:npmjs.com <task> node`
- `site:crates.io <task> rust`
- `site:packagist.org <task> php`

### GitHub follow-up

- `site:github.com <task> script`
- `site:github.com <task> cli`
- `site:github.com <task> python`
- `site:github.com <task> node`

## Narrowing hints

- Add the target OS when environment matters: `Windows`, `PowerShell`, `Linux`, `macOS`
- Add the target runtime when needed: `Python`, `Node`, `Bash`, `PowerShell`
- Add `official`, `maintained`, or `example` when results are too noisy
- Add `license` or a specific license name if reuse rights are important

## Candidate collection rule

Before choosing, try to gather:

- 1 to 2 primary-source candidates
- 1 to 2 ecosystem candidates
- 1 fallback public-repo candidate

That is usually enough. Avoid endless search.

## What to record after search

Capture briefly:

- which queries were used
- which candidates were considered
- which source was chosen
- why other candidates were rejected
