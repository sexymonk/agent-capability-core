---
name: repository-cleanliness
description: Use whenever working inside any source repository or project workspace, especially if the task may create helper scripts, generated artifacts, scratch notes, exported reports, screenshots, debug logs, temporary data files, or test/validation run waste. Keeps the repository clean by routing auxiliary files outside the repo, using external workspace paths by default, cleaning accidental repo clutter immediately, and sweeping disposable test artifacts when runs stop.
---

# Repository Cleanliness

## Overview

This skill enforces a repository hygiene rule: source repositories should contain project files, not conversation-specific helper artifacts. Use it whenever a task might write anything beyond intentional project code, tests, or repo-owned documentation. This includes the cleanup pass when a test, validation, or automation run finishes or is intentionally stopped.

## Default Rule

- Do not create auxiliary files inside the repository unless the user explicitly asks for that file to live in the repo.
- Default to an external workspace for helper scripts, scratch files, generated reports, temporary exports, screenshots, and analysis artifacts.
- If an auxiliary file is accidentally created in the repository, move or delete it in the same turn whenever possible.
- When a test, validation, or automation run finishes or is manually stopped, inspect for newly created transient artifacts and clean them in the same turn.
- Preserve durable learning artifacts such as reusable issue logs, failure notes, problem records, and memory updates that are still useful for future troubleshooting.

## External Workspace Policy

- Derive an external helper directory from the repository name when the user does not specify one.
- Preferred pattern on Windows: `<external-workspace>\<repo-name>\`
- User-facing deliverables may go to a user-specified external location such as a meeting-report folder, but the generating scripts and scratch files should still stay outside the repo.
- Create external directories as needed before generating artifacts.
- Apply the same cleanup rule to external helper directories when they were used only for the current test or validation run.

## What May Be Written Inside the Repo

- Requested source code changes.
- Requested tests.
- Documentation clearly intended to become part of the project.
- Configuration required for the requested feature or fix.

## What Must Stay Outside the Repo

- Temporary Python scripts or shell scripts written only to support the current task.
- Generated presentations, markdown notes, exported PDFs, review writeups, and analysis dumps unless the user explicitly wants them tracked in the repo.
- Screenshots, logs, one-off datasets, cached outputs, and intermediate files.
- Disposable test artifacts such as `__pycache__/`, `.pyc`, `.pytest_cache/`, temporary runtime folders, throwaway screenshots, and review clips unless the user explicitly asked to keep them.
- Any file whose value ends with the current conversation rather than the project itself.

## Decision Standard

- If there is any doubt whether a file belongs in the repo, keep it outside the repo.
- If a user explicitly asks for a repo-owned document or script, follow the request.
- Prefer external paths first; do not use the repository root as a convenient scratch space.
- If an artifact is useful only for the completed or stopped test run, delete it; if it teaches future debugging, preserve it or relocate it to the established learning/problem-memory location.

## Test-stop cleanup rule

When a test, validation, or automation run ends or is intentionally stopped:

1. Enumerate the new artifacts created by the run in the repo and in any helper directories touched by the run.
2. Separate disposable waste from durable learning artifacts.
3. Delete disposable waste immediately. Typical examples include `__pycache__/`, `.pyc`, `.pytest_cache/`, temporary screenshots, review videos, scratch exports, throwaway logs, runtime folders, and ignored cache directories.
4. Keep requested deliverables and learnable issue logs. If a learnable issue log is sitting in a disposable location, move it to the appropriate problem, memory, or notes location instead of deleting it.
5. Finish the cleanup before the final reply whenever it is safe to do so.

## Typical Triggers

- Generating a report, slide deck, markdown summary, or PDF from repository code.
- Writing a one-off script to inspect, transform, or export project data.
- Producing screenshots, logs, benchmark outputs, or debug traces.
- Running, validating, or stopping a test, automation, or local investigation flow that creates transient artifacts.
- Needing a temporary helper file to complete a coding task.

## Short Operating Checklist

1. Identify whether the requested output is project source or merely a helper artifact.
2. If it is a helper artifact, choose or create an external path first.
3. Generate the artifact outside the repo.
4. When a test, validation, or automation run ends or is stopped, enumerate the new transient artifacts in the repo and any helper directories used for the run.
5. Delete or move disposable artifacts immediately, while preserving requested deliverables and learnable issue logs.
6. If anything was accidentally created inside the repo, clean it up before finishing.

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
