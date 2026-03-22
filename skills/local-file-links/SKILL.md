---
name: local-file-links
description: Use when the user wants local files or folders in Codex output to appear as clickable blue links, or when a response includes local paths the user is likely to open. Formats local filesystem references as absolute Markdown links that open the target file or directory in the Codex app.
---

# Local File Links

## Overview

Use this skill when returning local files, folders, generated outputs, logs, reports, images, or code paths that the user may click in the Codex desktop app.

The goal is simple: never leave a useful local path as plain text when a clickable absolute link would let the user open it directly.

## Rules

- Format every local file or directory reference as a Markdown link, not plain text.
- Use an absolute filesystem path as the link target.
- In Codex desktop, the link target should be path-style, not URI-style.
- On Windows, use a leading slash before the drive letter: `/C:/path/to/file`.
- Do not use bare `C:/path/to/file` as the link target.
- Use one path per link. Do not combine multiple paths into one link.
- For files, link to the file itself.
- For directories, link to the directory itself.
- When handing off a newly created file, prefer giving both links when helpful:
  `Folder: [folder](/C:/absolute/folder)`
  `File: [name.ext](/C:/absolute/folder/name.ext)`
- Keep labels short and readable. Do not use the full long path as the visible label unless that clarity is needed.
- Do not wrap the visible link label in backticks.

## Output Pattern

Use patterns like these:

```md
Result file: [report.md](/C:/Users/13227/Documents/report.md)
```

```md
Folder: [exports](/D:/codex_aux/exports)
File: [summary.pdf](/D:/codex_aux/exports/summary.pdf)
```

```md
Code: [main.cpp](/D:/Project/src/main.cpp)
```

## Avoid

- Plain paths like `C:\tmp\out.txt` with no link.
- Relative paths when an absolute path is available.
- Bare Markdown targets like `(C:/tmp/out.txt)` that may be treated as a URI instead of a local file path.
- Bundling a file and its folder into one unreadable sentence when separate links would scan better.

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
