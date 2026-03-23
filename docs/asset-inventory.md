# Asset inventory

## Included generic skills

- agent-browser
- doc
- fail-fast-coding
- imagegen
- local-file-links
- markdown-to-pdf
- memory-maintenance
- openai-api-smoke-test
- pdf
- playwright-interactive
- pptx
- repository-cleanliness
- safe-commit-sync
- screenshot
- screenshot-sequence-video
- slides
- sora
- speech
- theme-factory
- transcribe
- workflow-solidifier
- search-first-skill-script
- skill-merge-governor
- skill-portability-auditor
- skill-self-update

## Deliberately excluded from core v1

- `.system/*` because they are upstream/system-managed rather than team-owned.
- `clipboard-profile-memory` because it contains personal profile recovery workflow.
- `group-meeting-report` because it is user-specific reporting automation.
- `chatgpt-apps` because it currently depends on excluded `.system/openai-docs` and needs a separate portability pass.
