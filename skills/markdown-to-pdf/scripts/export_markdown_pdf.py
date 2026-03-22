from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import markdown  # type: ignore
except Exception as exc:  # pragma: no cover - dependency check
    print(
        "Missing dependency: markdown. Install it with `python -m pip install markdown`.",
        file=sys.stderr,
    )
    raise SystemExit(4) from exc


def _extract_title(md_text: str, input_path: Path) -> str:
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return input_path.stem


def _infer_lang(md_text: str, input_path: Path) -> str:
    lowered = input_path.name.lower()
    if ".zh" in lowered or lowered.endswith(".zh-cn.md"):
        return "zh-CN"
    if ".en" in lowered or lowered.endswith(".en.md"):
        return "en"
    if re.search(r"[\u4e00-\u9fff]", md_text):
        return "zh-CN"
    return "en"


def _find_browser_exe() -> Path | None:
    candidates: list[str] = []

    for name in ["msedge", "msedge.exe", "chrome", "chrome.exe"]:
        found = shutil.which(name)
        if found:
            candidates.append(found)

    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")

    candidates += [
        str(Path(program_files) / "Microsoft" / "Edge" / "Application" / "msedge.exe"),
        str(Path(program_files_x86) / "Microsoft" / "Edge" / "Application" / "msedge.exe"),
        str(Path(program_files) / "Google" / "Chrome" / "Application" / "chrome.exe"),
        str(Path(program_files_x86) / "Google" / "Chrome" / "Application" / "chrome.exe"),
    ]

    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return path
    return None


def _md_to_html(
    md_text: str,
    title: str,
    lang: str,
    base_dir: Path,
    margin_mm: float,
    font_size_pt: float,
    line_height: float,
) -> str:
    body = markdown.markdown(
        md_text,
        extensions=["extra", "sane_lists"],
        output_format="html5",
    )
    base_href = base_dir.resolve().as_uri().rstrip("/") + "/"
    escaped_title = html.escape(title, quote=True)

    return f"""<!doctype html>
<html lang="{html.escape(lang, quote=True)}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escaped_title}</title>
  <base href="{html.escape(base_href, quote=True)}" />
  <style>
    @page {{ size: A4; margin: {margin_mm}mm; }}
    html, body {{ color: #111; background: #fff; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
        "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;
      font-size: {font_size_pt}pt;
      line-height: {line_height};
    }}
    h1 {{ font-size: 20pt; margin: 0 0 10pt; }}
    h2 {{ font-size: 14pt; margin: 14pt 0 8pt; border-bottom: 1px solid #ddd; padding-bottom: 4pt; }}
    h3 {{ font-size: 12.5pt; margin: 10pt 0 6pt; }}
    p {{ margin: 6pt 0; }}
    ul, ol {{ margin: 6pt 0 6pt 18pt; padding: 0; }}
    ul ul, ol ol, ul ol, ol ul {{ margin-left: 22pt; }}
    li {{ margin: 2pt 0; }}
    hr {{ border: 0; border-top: 1px solid #ddd; margin: 12pt 0; }}
    a {{ color: #0b57d0; text-decoration: none; }}
    img {{ max-width: 100%; height: auto; }}
    code, pre {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
        "Liberation Mono", "Courier New", monospace;
    }}
    pre {{ white-space: pre-wrap; background: #f6f8fa; padding: 8pt; border-radius: 6pt; }}
    blockquote {{ margin: 8pt 0; padding-left: 10pt; border-left: 3px solid #ddd; color: #444; }}
    table {{ border-collapse: collapse; width: 100%; margin: 8pt 0; }}
    th, td {{ border: 1px solid #ddd; padding: 6pt 8pt; vertical-align: top; }}
    th {{ background: #f6f8fa; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def _export_pdf_with_playwright(html_path: Path, out_pdf: Path, margin_mm: float) -> bool:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception:
        return False

    file_url = html_path.resolve().as_uri()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto(file_url, wait_until="networkidle")
            page.pdf(
                path=str(out_pdf.resolve()),
                format="A4",
                print_background=True,
                display_header_footer=False,
                margin={
                    "top": f"{margin_mm}mm",
                    "right": f"{margin_mm}mm",
                    "bottom": f"{margin_mm}mm",
                    "left": f"{margin_mm}mm",
                },
                prefer_css_page_size=True,
            )
            browser.close()
        return True
    except Exception:
        return False


def _export_pdf_with_browser(browser: Path, html_path: Path, out_pdf: Path) -> None:
    file_url = html_path.resolve().as_uri()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    commands = [
        [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--disable-features=PrintCompositorLPAC",
            f"--print-to-pdf={str(out_pdf.resolve())}",
            "--no-pdf-header-footer",
            file_url,
        ],
        [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--disable-features=PrintCompositorLPAC",
            f"--print-to-pdf={str(out_pdf.resolve())}",
            "--print-to-pdf-no-header",
            file_url,
        ],
        [
            str(browser),
            "--headless",
            "--disable-gpu",
            f"--print-to-pdf={str(out_pdf.resolve())}",
            "--no-pdf-header-footer",
            file_url,
        ],
        [
            str(browser),
            "--headless",
            "--disable-gpu",
            f"--print-to-pdf={str(out_pdf.resolve())}",
            "--print-to-pdf-no-header",
            file_url,
        ],
    ]

    last_error: Exception | None = None
    for command in commands:
        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception as exc:
            last_error = exc

    assert last_error is not None
    raise last_error


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export a Markdown document to PDF through HTML without browser-added headers or footers."
    )
    parser.add_argument("--input", required=True, help="Path to the input Markdown file.")
    parser.add_argument("--out-pdf", help="Output PDF path. Defaults to <input>.pdf.")
    parser.add_argument("--out-html", help="Intermediate HTML path. Defaults to <input>.html.")
    parser.add_argument("--title", help="Document title for the HTML wrapper.")
    parser.add_argument("--lang", help="Document language for the HTML wrapper.")
    parser.add_argument("--margin-mm", type=float, default=14.0, help="Page margin in millimeters. Default: 14.")
    parser.add_argument("--font-size-pt", type=float, default=12.0, help="Body font size in points. Default: 12.")
    parser.add_argument("--line-height", type=float, default=1.55, help="Body line height. Default: 1.55.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 2

    out_pdf = Path(args.out_pdf) if args.out_pdf else input_path.with_suffix(".pdf")
    out_html = Path(args.out_html) if args.out_html else input_path.with_suffix(".html")

    md_text = input_path.read_text(encoding="utf-8")
    title = args.title or _extract_title(md_text, input_path)
    lang = args.lang or _infer_lang(md_text, input_path)
    html_text = _md_to_html(
        md_text=md_text,
        title=title,
        lang=lang,
        base_dir=input_path.parent,
        margin_mm=args.margin_mm,
        font_size_pt=args.font_size_pt,
        line_height=args.line_height,
    )

    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html_text, encoding="utf-8")

    if _export_pdf_with_playwright(out_html, out_pdf, args.margin_mm):
        print(f"Wrote HTML: {out_html}")
        print(f"Wrote PDF: {out_pdf}")
        return 0

    browser = _find_browser_exe()
    if browser is None:
        print("Could not find Edge/Chrome and Playwright is unavailable.", file=sys.stderr)
        print(f"HTML has been generated at: {out_html}", file=sys.stderr)
        print(
            "Install one of the following:\n"
            "  - Microsoft Edge or Google Chrome\n"
            "  - Playwright with Chromium: python -m pip install playwright && python -m playwright install chromium",
            file=sys.stderr,
        )
        return 3

    _export_pdf_with_browser(browser, out_html, out_pdf)
    print(f"Wrote HTML: {out_html}")
    print(f"Wrote PDF: {out_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
