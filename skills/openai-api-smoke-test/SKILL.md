---
name: openai-api-smoke-test
description: Verify whether OpenAI API access is still usable. Use when Codex needs to test an OpenAI secret key or admin key, confirm chat, responses, image, or usage endpoints still answer, or distinguish quota, auth, scope, and model-permission failures from local client bugs.
---

# OpenAI API Smoke Test

Use the bundled script instead of ad-hoc snippets when the user asks whether an OpenAI API key still works.

## Quick Start

Run the smallest check that answers the question:

- Basic text-generation availability:
  `python scripts/check_openai_api.py`
- Secret key plus admin usage access:
  `python scripts/check_openai_api.py --checks chat,admin`
- Explicit Responses API probe:
  `python scripts/check_openai_api.py --checks chat,responses`
- Image generation access:
  `python scripts/check_openai_api.py --checks chat,images`

## Workflow

1. Start with `chat` for a cheap end-to-end inference probe that should return explicit text.
2. Add `responses` only when the user specifically depends on the Responses API.
3. Add `images` only when the user specifically wants to test image generation, because it is costlier than a text probe.
4. Add `admin` when the user asks about usage, billing, or organization-level permissions. This requires `OPENAI_ADMIN_API_KEY`.
5. Report both HTTP status and parsed error details. Treat these patterns as the first-pass diagnosis:
   - `200`: endpoint is usable
   - `401`: bad or missing key
   - `403`: missing scope, org role, or model access
   - `429`: quota or rate limit
   - `>=500`: provider-side failure or transient outage

## Output Interpretation

The script prints JSON so it can be copied into notes or parsed by other tooling. Each requested check includes:

- `ok`: whether the endpoint was usable
- `status`: HTTP status if a response was received
- `latency_ms`: request latency
- `error`: parsed error payload when the request failed
- endpoint-specific details such as reply preview, response id, or bucket counts

For admin checks, `200` with empty buckets still means the admin key and scope work.

## Parameters

- `--checks`: comma-separated subset of `chat,responses,images,admin`
- `--chat-model`: defaults to `gpt-4.1-mini`
- `--responses-model`: defaults to `gpt-5-mini`
- `--image-model`: defaults to `gpt-image-1`
- `--base-url`: defaults to `https://api.openai.com`
- `--secret-key-env`: defaults to `OPENAI_API_KEY`
- `--admin-key-env`: defaults to `OPENAI_ADMIN_API_KEY`
- `--admin-days`: rolling window for admin usage probe, defaults to `30`
- `--timeout`: request timeout in seconds

## Resource

- `scripts/check_openai_api.py`: deterministic probe for secret-key inference access, Responses API access, image generation access, and admin usage scope.

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
