---
name: search-first-skill-script
description: Use when a user needs a new skill or script and the preferred workflow is to search the internet for existing skills, scripts, repositories, or examples first, then download or vendorize them locally, adapt them to the local environment, and only generate from scratch when no suitable reference exists.
---

# Search First Skill Script

## Overview

This meta-skill implements a **search first, localize second, generate last** workflow for new skills and scripts.

Use it when the user wants a new skill or script, but would rather start from proven public examples than from a blank page.

## Core policy

- Search the web first unless the user explicitly says not to.
- Prefer **primary sources**: official repositories, official docs, package registries, release pages, or maintained upstream examples.
- Prefer **local adaptation** over blind reuse.
- Generate from scratch only when no suitable reference exists, the license is incompatible, or the available code is too stale, unsafe, or misaligned.

## Workflow

1. Clarify the target:
   - Is the user asking for a **skill**, a **script**, or both?
   - What local environment, language, and output contract must it fit?
2. Search online for existing implementations.
   - Prefer official repos and maintained upstream sources.
   - For scripts, prefer focused utilities over giant frameworks when a narrow tool is enough.
   - For skills, consider existing Codex/OpenAI skill repos first when relevant.
3. Evaluate candidates using [references/source-selection.md](references/source-selection.md).
4. Download, vendorize, or install the best candidate locally.
5. Localize and adapt it:
   - rewrite prompts, paths, environment assumptions, output conventions, and helper commands
   - remove irrelevant pieces
   - make the result fit the user's current workspace and tooling
6. Validate the localized result locally.
7. If no acceptable candidate exists, generate a narrow custom implementation from scratch.
8. Record provenance, durable rules, and avoided paths in `references/learning-log.md`.

## Source priority order

Use this default source order unless the task strongly suggests a different path.

### When the target is a skill

1. Official skill repositories or vendor-maintained skill collections
   - for Codex/OpenAI-related skills, check official OpenAI/Codex skill sources first when relevant
2. Official product or framework docs that include example skills, templates, or starter repos
3. Well-maintained GitHub repositories with clear ownership and license
4. Narrow blog posts or gists only as a last-resort hint, never as the preferred source when a primary source exists

### When the target is a script

1. Official docs plus linked reference implementations
2. Official or vendor-maintained GitHub repositories
3. Package registries with strong examples or usable source packages
   - PyPI for Python
   - npm for Node.js
   - other language-native registries when clearly relevant
4. Well-maintained public repositories with clear license and recent activity
5. Low-trust snippets only as fallback inspiration

If the task is ambiguous between a reusable skill and a one-off script, search both tracks briefly, then choose the narrower artifact that satisfies the user need.

## Source selection rules

- Prefer actively maintained sources over abandoned snippets.
- Prefer code with a clear and usable license.
- Avoid copying from random blogs, repost sites, or unattributed gists when a primary source exists.
- If multiple candidates are viable, choose the one with the smallest adaptation surface and clearest maintenance story.
- If the best public code is too broad, vendor only the minimal relevant subset.

## Adaptation rules

When reusing an external skill or script, always localize it before treating it as done:

- align file paths with the local machine
- align shell commands with the local shell and OS
- align environment variable names with the local setup
- align output style with the user's expectations
- strip unused dependencies, examples, and assets when they add noise
- make validation repeatable in the local environment

## Fallback rule

Generate from scratch only when one of these is true:

- no suitable reference exists
- the license blocks the intended reuse
- the upstream implementation is too stale or unsafe
- adaptation cost is higher than a clean narrow implementation
- the user explicitly asks for a fresh implementation

When falling back, briefly note what was searched and why the fallback was necessary.

## Output expectations

When this skill is used, the result should usually include:

- the chosen upstream source or a short list of candidates
- what was downloaded or vendorized locally
- what was rewritten for local use
- how it was validated
- whether the result came from adaptation or from scratch

## References

Read [references/source-selection.md](references/source-selection.md) when deciding between candidate sources or determining whether to vendor, install, or rewrite.
Read [references/search-templates.md](references/search-templates.md) when forming web queries or deciding search order across GitHub, package registries, docs, and example repos.

## Learning maintenance

Maintain `references/learning-log.md` for this skill.

Update it when:
- a user gives a reusable correction about this skill's trigger, scope, workflow, output, validation, or routing
- a novel multi-step workflow using this skill is approved for reuse
- a failed or brittle path reveals an avoided path worth preserving

Keep entries concise and generalizable. Record:
- durable rules
- approved workflow promotions
- avoided paths

Do not store full transcripts, transient facts, or one-off preferences.
