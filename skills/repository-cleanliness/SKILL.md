---
name: repository-cleanliness
description: Use whenever working inside any source repository or project workspace, especially if the task may create helper scripts, generated artifacts, scratch notes, exported reports, screenshots, debug logs, temporary data files, or any non-source output. Keeps the repository clean by routing auxiliary files outside the repo, using external workspace paths by default, and cleaning accidental repo clutter immediately.
---

# Repository Cleanliness

## Overview

This skill enforces a repository hygiene rule: source repositories should contain project files, not conversation-specific helper artifacts. Use it whenever a task might write anything beyond intentional project code, tests, or repo-owned documentation.

## Default Rule

- Do not create auxiliary files inside the repository unless the user explicitly asks for that file to live in the repo.
- Default to an external workspace for helper scripts, scratch files, generated reports, temporary exports, screenshots, and analysis artifacts.
- If an auxiliary file is accidentally created in the repository, move or delete it in the same turn whenever possible.

## External Workspace Policy

- Derive an external helper directory from the repository name when the user does not specify one.
- Preferred pattern on Windows: `D:\codex_aux\<repo-name>\`
- User-facing deliverables may go to a user-specified external location such as a meeting-report folder, but the generating scripts and scratch files should still stay outside the repo.
- Create external directories as needed before generating artifacts.

## What May Be Written Inside the Repo

- Requested source code changes.
- Requested tests.
- Documentation clearly intended to become part of the project.
- Configuration required for the requested feature or fix.

## What Must Stay Outside the Repo

- Temporary Python scripts or shell scripts written only to support the current task.
- Generated presentations, markdown notes, exported PDFs, review writeups, and analysis dumps unless the user explicitly wants them tracked in the repo.
- Screenshots, logs, one-off datasets, cached outputs, and intermediate files.
- Any file whose value ends with the current conversation rather than the project itself.

## Decision Standard

- If there is any doubt whether a file belongs in the repo, keep it outside the repo.
- If a user explicitly asks for a repo-owned document or script, follow the request.
- Prefer external paths first; do not use the repository root as a convenient scratch space.

## Typical Triggers

- Generating a report, slide deck, markdown summary, or PDF from repository code.
- Writing a one-off script to inspect, transform, or export project data.
- Producing screenshots, logs, benchmark outputs, or debug traces.
- Needing a temporary helper file to complete a coding task.

## Short Operating Checklist

1. Identify whether the requested output is project source or merely a helper artifact.
2. If it is a helper artifact, choose or create an external path first.
3. Generate the artifact outside the repo.
4. If anything was accidentally created inside the repo, clean it up before finishing.

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
