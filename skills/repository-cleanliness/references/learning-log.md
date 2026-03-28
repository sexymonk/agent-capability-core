# Learning Log

This file records durable rules, approved workflow promotions, and avoided paths for `repository-cleanliness`.

## Durable rules
- When a test, validation, or automation run finishes or is manually stopped, run an explicit cleanup sweep for disposable artifacts in the repo and any helper directories touched by the run. Delete caches and transient outputs such as `__pycache__/`, `.pyc`, `.pytest_cache/`, temporary screenshots, review clips, throwaway logs, scratch exports, and runtime folders unless the user explicitly asked to keep them.
- Do not treat reusable issue logs, failure notes, or problem-memory updates as waste. Preserve them, or move them into the appropriate learning/problem-log location before cleaning the rest.

## Approved workflow promotions
- Promote stop-test cleanup into the normal finish path: after stopping a test, enumerate new artifacts, separate disposable waste from reusable learning records, remove the waste in the same turn, and then report what was kept.

## Avoided paths
- Do not leave gitignored caches or runtime debris behind just because version control already ignores them.
- Do not blanket-delete logs or evidence before deciding whether they are learnable issue records.
