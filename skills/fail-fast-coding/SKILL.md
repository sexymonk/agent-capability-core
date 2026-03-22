---
name: fail-fast-coding
description: "Use whenever modifying code in any repository or project workspace unless the user explicitly asks for defensive programming, graceful degradation, compatibility fallbacks, or tolerant handling of invalid upstream state. Enforces a fail-fast style: prefer strict contracts, explicit preconditions, clear errors, and immediate failure over fallback branches, silent clamping, optional-path auto-detection, retries, or guard-heavy recovery code."
---

# Fail Fast Coding

## Overview

This skill enforces a strict fail-fast coding style for code changes. Treat invalid state as a bug to surface quickly, not something to patch over with defensive branches or fallback behavior.

## Default Policy

- Do not add fallback implementations, graceful-degradation branches, compatibility shims, retry loops, or silent recovery logic unless the user explicitly asks for them.
- Do not add defensive checks whose only purpose is to tolerate broken upstream state.
- Prefer a single clear execution path with explicit assumptions.
- Prefer immediate failure with a clear error over hidden correction or best-effort continuation.

## What To Prefer

- Explicit preconditions and narrow contracts.
- Assertions, hard errors, or direct failures when invariants are violated.
- Straight-line logic instead of multi-branch fallback flows.
- Fixing the real upstream assumption when feasible instead of compensating downstream.
- Boundary validation that rejects bad input clearly rather than coercing it into a tolerated shape.

## What To Avoid

- Null-tolerant branches added "just in case".
- Size, bounds, or existence guards added only to keep execution limping forward.
- Silent defaulting, silent clamping, and silent type coercion.
- Catch-all exception swallowing.
- Fallback code paths for environments, features, or data shapes unless explicitly required.
- "Best effort" behavior that hides contract violations.

## Decision Standard

- If the code should not run when an assumption is false, let it fail clearly.
- If robustness is required for a public boundary, validate at the boundary and reject invalid input explicitly.
- If an existing code path already contains defensive fallback logic, do not expand that pattern by default.
- If the user explicitly asks for resilience, backward compatibility, or graceful degradation, follow the user request instead of this skill.

## Typical Triggers

- Any feature implementation in a repository where the default preference is strict behavior.
- Bug fixes where the tempting option would be to add guards instead of addressing the actual invariant.
- Refactors involving optional branches, compatibility paths, retries, or fallback implementations.
- Reviews or rewrites where the user wants simpler, more auditable code paths.

## Short Checklist

1. Identify the real invariant or contract.
2. Implement the direct path that assumes the contract is true.
3. Reject or fail clearly when the contract is broken.
4. Do not add fallback behavior unless the user explicitly asks for it.

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
