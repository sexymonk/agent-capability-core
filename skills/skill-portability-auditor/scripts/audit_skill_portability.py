#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PATTERNS = {
    'codex_specific': re.compile(r'\bCodex\b|\bcodex\b'),
    'model_name': re.compile(r'\b(?:gpt-[\w.-]+|GPT(?:-[\w.-]+)?|Claude|claude|Gemini|gemini|Qwen|qwen|Copilot|copilot|Cursor|cursor|Windsurf|windsurf|Aider|aider|ChatGPT|chatgpt)\b'),
    'provider_name': re.compile(r'\b(?:OpenAI|openai|Anthropic|anthropic|Google|google)\b'),
    'absolute_windows_path': re.compile(r'[A-Za-z]:\\'),
    'agent_runtime_file': re.compile(r'\b(?:AGENTS\.md|GEMINI\.md|CLAUDE\.md|\.codex|\.claude|\.agent)\b'),
}

INTENTIONALLY_VENDOR_BOUND_HINTS = {
    'openai-docs',
    'openai-api-smoke-test',
    'chatgpt-apps',
    'sora',
    'speech',
    'transcribe',
}


def classify_skill(skill_name: str, findings: dict[str, list[dict]]) -> str:
    if not any(findings.values()):
        return 'portable-as-is'
    if skill_name in INTENTIONALLY_VENDOR_BOUND_HINTS:
        return 'likely-provider-bound-review'
    if findings['codex_specific'] or findings['model_name'] or findings['agent_runtime_file']:
        return 'likely-needs-generalization'
    return 'manual-review'


def audit_file(path: Path) -> dict:
    text = path.read_text(encoding='utf-8', errors='replace')
    findings: dict[str, list[dict]] = {key: [] for key in PATTERNS}
    for lineno, line in enumerate(text.splitlines(), start=1):
        for key, regex in PATTERNS.items():
            if regex.search(line):
                findings[key].append({'line': lineno, 'text': line.strip()})
    skill_name = path.parent.name
    return {
        'skill_name': skill_name,
        'path': str(path),
        'classification': classify_skill(skill_name, findings),
        'findings': findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Audit local skills for portability risks.')
    parser.add_argument('--skills-root', default=str(Path.home() / '.codex' / 'skills'))
    parser.add_argument('--json', action='store_true', help='Emit full JSON output')
    args = parser.parse_args()

    root = Path(args.skills_root).expanduser().resolve()
    skill_files = sorted(root.rglob('SKILL.md'))
    results = [audit_file(path) for path in skill_files]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    for item in results:
        counts = {k: len(v) for k, v in item['findings'].items() if v}
        if not counts:
            summary = 'no obvious portability flags'
        else:
            summary = ', '.join(f'{k}={v}' for k, v in counts.items())
        print(f"[{item['classification']}] {item['skill_name']}: {summary}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
