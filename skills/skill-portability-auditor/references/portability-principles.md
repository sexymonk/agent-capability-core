# Portability Principles

These principles help keep skills reusable across different model and agent environments.

## Why these rules

Two useful reference points informed this skill:

- OpenAI prompt guidance emphasizes **clear, specific, structured instructions** and warns against unnecessary model-specific prompt tricks.
- Universal skill loaders such as OpenSkills show that the same `SKILL.md` format can be reused across multiple agents when the skill stays neutral about the runtime and isolates adapters.

## Core principles

1. **Describe capabilities, not brands, unless brands are essential.**
   - Prefer "the agent needs shell access" over "Codex should run shell commands".
2. **Keep prompts simple and direct.**
   - Do not rely on one model family's special prompting quirks unless the skill truly targets that family.
3. **Separate core workflow from provider adapters.**
   - Put product-specific keys, commands, and integration steps into clearly marked sections.
4. **Keep intentionally vendor-specific skills explicit.**
   - Portability does not mean pretending a vendor API is generic.
5. **Avoid accidental runtime lock-in.**
   - Do not imply that one UI, one tool, or one prompt hierarchy is the only valid execution path unless it actually is.
6. **Keep trigger descriptions precise.**
   - Generality should not make the skill harder to trigger correctly.

## Rewrite patterns

### Prefer this
- "the agent"
- "the runtime"
- "requires file access / shell / browser automation"
- "if using OpenAI..."
- "if using Claude-compatible skills..."

### Instead of this
- "Codex always..."
- "Claude is required" when only the skill format is reused
- hard-coding one model name when the actual requirement is a capability
- burying provider-specific keys and commands inside the generic workflow

## Acceptable exceptions

A skill may stay provider-specific when its actual purpose is provider-specific, for example:
- OpenAI API smoke testing
- ChatGPT app implementation details
- Sora generation workflows
- vendor-specific docs lookup

In these cases, improve portability around the edges rather than pretending the underlying product is universal.
