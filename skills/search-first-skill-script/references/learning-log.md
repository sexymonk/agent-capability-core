# Learning Log

This file records durable rules, approved workflow promotions, and avoided paths for `search-first-skill-script`.

## Durable rules
- 2026-03-22: For new skills or scripts, prefer a search-first workflow: search online, adapt locally, and generate from scratch only when references are unsuitable.
- 2026-03-22: Prefer primary sources and locally adapted reuse over blind copying or blank-page generation.
- 2026-03-22: Use an explicit source priority order: official skills/docs first, then package ecosystems and maintained repos, and only then lower-trust snippets.
- 2026-03-22: Use reusable query templates for GitHub, official docs, and package registries to keep search focused and repeatable.

## Approved workflow promotions
- 2026-03-22: Promote the workflow `clarify -> search -> evaluate -> vendorize/install -> localize -> validate -> fallback generate` as the default pattern for this meta-skill.
- 2026-03-22: Promote a default search wave of `primary sources -> registries -> GitHub -> low-trust fallback` before selecting a candidate.

## Avoided paths
- 2026-03-22: Do not start from scratch before attempting a real search for existing references.
- 2026-03-22: Do not blindly download and use external code without local adaptation, licensing review, and validation.
- 2026-03-22: Do not prefer reposted snippets or random blogs when primary sources are available.
- 2026-03-22: Do not let package registries or generic GitHub search outrank official docs or official upstream repos by default.
