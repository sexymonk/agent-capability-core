# Learning Log

This file records durable rules, approved workflow promotions, and avoided paths for `skill-self-update`.

## Durable rules
- 2026-03-18: `skill-self-update` must support both correction-driven updates and approval-driven promotion of reusable long workflows.
- 2026-03-18: Correction-driven updates should capture not only the corrected rule but also informative failed paths that should not be retried.

## Approved workflow promotions
- 2026-03-18: When a novel multi-step workflow is completed and the user accepts it or asks to continue without correction, treat that as permission to update an owning skill or create a narrow new skill if no owner exists.
- 2026-03-25: When a user approves a weekly ecosystem-watch workflow that scans hot projects, writes structured learning records, creates one implementation plan, and performs one safe local execution step, prefer creating a narrow owning skill instead of overloading generic workflow or research skills.

## Avoided paths
- 2026-03-18: Do not limit skill learning to explicit user error reports only; this misses reusable workflows that were implicitly approved by continuation.
- 2026-03-18: Do not preserve only the happy path; record concise avoided paths when they explain what future runs should skip.
