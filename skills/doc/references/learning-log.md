# Learning Log

This file records durable rules, approved workflow promotions, and avoided paths for `doc`.

## Durable rules
- 2026-04-01: For DOCX generation on Windows, verify non-ASCII content by reopening the saved file with `python-docx` or inspecting `word/document.xml` directly, instead of trusting terminal rendering.

## Approved workflow promotions
- None yet.

## Avoided paths
- 2026-04-01: Avoid piping inline Python with Chinese or other non-ASCII document text through PowerShell when generating `.docx`, because the shell path may replace characters with question marks before Python writes the file.
