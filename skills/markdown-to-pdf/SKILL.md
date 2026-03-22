---
name: markdown-to-pdf
description: Export Markdown documents (.md) to clean PDF files through HTML rendering with Chromium, Edge, Chrome, or Playwright. Use when Codex needs to convert notes, letters, resumes, reports, or other Markdown documents into print-friendly PDFs, especially when browser-added headers and footers must be removed.
---

# Markdown to PDF

Use `scripts/export_markdown_pdf.py` for deterministic Markdown-to-PDF conversion.

## Quick Start

Run:

```bash
python scripts/export_markdown_pdf.py --input /path/to/file.md
```

This writes:

- a PDF next to the Markdown file
- an intermediate HTML file next to the Markdown file

The script defaults to a clean print layout and suppresses browser-added header/footer content.

## Workflow

1. Choose the Markdown file.
2. Run `scripts/export_markdown_pdf.py`.
3. Open the generated PDF and verify pagination.
4. If the layout is too loose or too dense, rerun with a different `--margin-mm`, `--font-size-pt`, or `--line-height`.

## Important Behavior

- Prefer the script over a browser print dialog.
- Keep the generated HTML body limited to the rendered Markdown content. Do not prepend cover text, titles, dates, or footer blocks unless the Markdown source already contains them.
- The script removes browser-added print headers/footers by:
  - using Playwright with `display_header_footer=False`, or
  - using Chromium/Edge/Chrome with `--no-pdf-header-footer` and compatible fallbacks
- If you manually print the generated HTML from a browser UI instead of using the script, disable the browser's `Headers and footers` option or the browser may add URL, title, date, and page numbers.

## Command Examples

Use explicit output paths:

```bash
python scripts/export_markdown_pdf.py \
  --input D:/docs/letter.md \
  --out-html D:/docs/letter.print.html \
  --out-pdf D:/docs/letter.pdf
```

Use tighter page margins:

```bash
python scripts/export_markdown_pdf.py \
  --input D:/docs/report.md \
  --margin-mm 10 \
  --font-size-pt 11 \
  --line-height 1.45
```

Set an explicit title and language:

```bash
python scripts/export_markdown_pdf.py \
  --input D:/docs/bilingual-note.md \
  --title "Project Note" \
  --lang zh-CN
```

## Script Notes

- Relative image and link paths resolve from the Markdown file's directory through an HTML `<base>` tag.
- The script requires the Python `markdown` package.
- Playwright is optional. If unavailable, the script falls back to a locally installed Chromium-based browser.
- If no browser is available, stop and install Microsoft Edge or Google Chrome, or install Playwright with Chromium.

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
