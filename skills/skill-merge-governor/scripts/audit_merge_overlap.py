#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "for", "from", "if",
    "in", "into", "is", "it", "needs", "of", "on", "or", "other", "that", "the",
    "their", "this", "to", "use", "when", "with", "your", "you", "any", "local",
    "skill", "skills", "script", "scripts", "workflow", "workflows", "task", "tasks",
    "user", "users", "agent", "agents", "codex",
}


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a = set(left)
    b = set(right)
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def ratio(left: str, right: str) -> float:
    return difflib.SequenceMatcher(a=left, b=right).ratio()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_changed_paths(repo_root: Path, base_ref: str, head_ref: str) -> list[Path]:
    cmd = ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"]
    result = subprocess.run(
        cmd,
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=True,
    )
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped:
            paths.append((repo_root / stripped).resolve())
    return paths


def parse_frontmatter(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")
    if not text.startswith("---"):
        raise ValueError(f"Missing YAML frontmatter in {path}")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse YAML frontmatter in {path}")
    frontmatter = match.group(1)
    name_match = re.search(r"^name:\s*(.+?)\s*$", frontmatter, flags=re.MULTILINE)
    desc_match = re.search(r"^description:\s*(.+?)\s*$", frontmatter, flags=re.MULTILINE)
    if not name_match or not desc_match:
        raise ValueError(f"Frontmatter must contain name and description in {path}")
    name = name_match.group(1).strip().strip("\"'")
    description = desc_match.group(1).strip().strip("\"'")
    return name, description


@dataclass(frozen=True)
class SkillInfo:
    slug: str
    name: str
    description: str
    path: Path
    script_paths: tuple[Path, ...]
    reference_paths: tuple[Path, ...]

    @property
    def description_tokens(self) -> set[str]:
        return tokenize(self.description)

    @property
    def name_tokens(self) -> set[str]:
        return tokenize(self.slug.replace("-", " "))


@dataclass(frozen=True)
class ScriptInfo:
    path: Path
    owner: str
    stem: str
    digest: str

    @property
    def tokens(self) -> set[str]:
        return tokenize(self.stem.replace("-", " ").replace("_", " "))


def discover_skills(repo_root: Path) -> list[SkillInfo]:
    skills_root = repo_root / "skills"
    if not skills_root.exists():
        raise FileNotFoundError(f"Skills root not found: {skills_root}")
    results: list[SkillInfo] = []
    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        name, description = parse_frontmatter(skill_file)
        script_paths = tuple(sorted((skill_dir / "scripts").rglob("*"))) if (skill_dir / "scripts").exists() else ()
        script_paths = tuple(path for path in script_paths if path.is_file())
        reference_paths = tuple(sorted((skill_dir / "references").rglob("*"))) if (skill_dir / "references").exists() else ()
        reference_paths = tuple(path for path in reference_paths if path.is_file())
        results.append(
            SkillInfo(
                slug=skill_dir.name,
                name=name,
                description=description,
                path=skill_file,
                script_paths=script_paths,
                reference_paths=reference_paths,
            )
        )
    return results


def discover_scripts(repo_root: Path, skills: list[SkillInfo]) -> list[ScriptInfo]:
    script_infos: list[ScriptInfo] = []
    seen: set[Path] = set()
    for skill in skills:
        for path in skill.script_paths:
            if "__pycache__" in path.parts:
                continue
            seen.add(path.resolve())
            script_infos.append(
                ScriptInfo(path=path, owner=skill.slug, stem=path.stem.lower(), digest=sha256(path))
            )
    repo_scripts_root = repo_root / "scripts"
    if repo_scripts_root.exists():
        for path in sorted(repo_scripts_root.rglob("*")):
            if "__pycache__" in path.parts:
                continue
            if path.is_file() and path.resolve() not in seen:
                script_infos.append(
                    ScriptInfo(path=path, owner="repo-root", stem=path.stem.lower(), digest=sha256(path))
                )
    return script_infos


def changed_skill_slugs(repo_root: Path, changed_paths: list[Path]) -> set[str]:
    slugs: set[str] = set()
    for path in changed_paths:
        try:
            rel = path.resolve().relative_to(repo_root.resolve())
        except ValueError:
            continue
        parts = rel.parts
        if len(parts) >= 2 and parts[0] == "skills":
            slugs.add(parts[1])
    return slugs


def changed_script_paths(repo_root: Path, changed_paths: list[Path]) -> set[Path]:
    results: set[Path] = set()
    for path in changed_paths:
        resolved = path.resolve()
        try:
            rel = resolved.relative_to(repo_root.resolve())
        except ValueError:
            continue
        if resolved.is_file() and "scripts" in rel.parts:
            results.add(resolved)
    return results


def skill_overlap_score(left: SkillInfo, right: SkillInfo) -> dict[str, float]:
    name_similarity = ratio(left.slug, right.slug)
    name_token_overlap = jaccard(left.name_tokens, right.name_tokens)
    description_overlap = jaccard(left.description_tokens, right.description_tokens)
    weighted = (0.4 * description_overlap) + (0.35 * name_similarity) + (0.25 * name_token_overlap)
    return {
        "score": round(weighted, 3),
        "name_similarity": round(name_similarity, 3),
        "name_token_overlap": round(name_token_overlap, 3),
        "description_overlap": round(description_overlap, 3),
    }


def script_overlap_score(left: ScriptInfo, right: ScriptInfo) -> dict[str, float]:
    exact_duplicate = 1.0 if left.digest == right.digest else 0.0
    stem_similarity = ratio(left.stem, right.stem)
    token_overlap = jaccard(left.tokens, right.tokens)
    weighted = max(exact_duplicate, (0.45 * stem_similarity) + (0.55 * token_overlap))
    return {
        "score": round(weighted, 3),
        "exact_duplicate": round(exact_duplicate, 3),
        "stem_similarity": round(stem_similarity, 3),
        "token_overlap": round(token_overlap, 3),
    }


def build_report(
    repo_root: Path,
    skills: list[SkillInfo],
    scripts: list[ScriptInfo],
    changed_paths: list[Path],
    threshold: float,
    top_n: int,
) -> dict:
    changed_slugs = changed_skill_slugs(repo_root, changed_paths)
    changed_script_set = changed_script_paths(repo_root, changed_paths)

    candidate_skills = [skill for skill in skills if not changed_slugs or skill.slug in changed_slugs]
    if changed_script_set:
        candidate_scripts = [script for script in scripts if script.path.resolve() in changed_script_set]
    elif changed_slugs:
        candidate_scripts = [script for script in scripts if script.owner in changed_slugs]
    else:
        candidate_scripts = list(scripts)

    skill_findings: list[dict] = []
    for candidate in candidate_skills:
        comparisons: list[dict] = []
        for other in skills:
            if other.slug == candidate.slug:
                continue
            metrics = skill_overlap_score(candidate, other)
            if metrics["score"] >= threshold:
                comparisons.append(
                    {
                        "other_skill": other.slug,
                        "other_path": str(other.path),
                        **metrics,
                    }
                )
        comparisons.sort(key=lambda item: item["score"], reverse=True)
        if comparisons:
            skill_findings.append(
                {
                    "skill": candidate.slug,
                    "path": str(candidate.path),
                    "matches": comparisons[:top_n],
                }
            )

    script_findings: list[dict] = []
    for candidate in candidate_scripts:
        comparisons = []
        for other in scripts:
            if other.path.resolve() == candidate.path.resolve():
                continue
            metrics = script_overlap_score(candidate, other)
            if metrics["score"] >= threshold:
                comparisons.append(
                    {
                        "other_owner": other.owner,
                        "other_path": str(other.path),
                        **metrics,
                    }
                )
        comparisons.sort(key=lambda item: (item["exact_duplicate"], item["score"]), reverse=True)
        if comparisons:
            script_findings.append(
                {
                    "script": str(candidate.path),
                    "owner": candidate.owner,
                    "matches": comparisons[:top_n],
                }
            )

    return {
        "repo_root": str(repo_root),
        "changed_paths": [str(path) for path in changed_paths],
        "changed_skills": sorted(changed_slugs),
        "changed_script_paths": sorted(str(path) for path in changed_script_set),
        "skill_findings": skill_findings,
        "script_findings": script_findings,
    }


def default_scope_label(report: dict, base_ref: str | None, head_ref: str | None) -> str:
    if base_ref and head_ref:
        return f"{base_ref}...{head_ref}"
    if report["changed_paths"]:
        return ", ".join(Path(path).name for path in report["changed_paths"])
    return "full repository scan"


def markdown_escape(text: str) -> str:
    return text.replace("|", "\\|")


def render_markdown_report(report: dict, scope_label: str, threshold: float) -> str:
    skill_overlap_count = sum(len(item["matches"]) for item in report["skill_findings"])
    script_overlap_count = sum(len(item["matches"]) for item in report["script_findings"])
    recommendation = "Approve"
    if skill_overlap_count or script_overlap_count:
        recommendation = "Approve after listed consolidation changes"

    lines: list[str] = [
        f"# Merge Review Report: {scope_label}",
        "",
        "## Summary",
        "",
        f"- Review scope: {scope_label}",
        f"- Changed skills: {', '.join(report['changed_skills']) if report['changed_skills'] else 'None'}",
        f"- Changed scripts: {', '.join(report['changed_script_paths']) if report['changed_script_paths'] else 'None'}",
        f"- Flagged skill overlaps: {skill_overlap_count}",
        f"- Flagged script overlaps: {script_overlap_count}",
        f"- Merge recommendation: {recommendation}",
        "",
        "## Scope",
        "",
        f"- Repo root: `{report['repo_root']}`",
        f"- Threshold: `{threshold}`",
    ]

    if report["changed_paths"]:
        lines.append("- Changed paths:")
        for path in report["changed_paths"]:
            lines.append(f"  - `{path}`")
    else:
        lines.append("- Changed paths: full repository scan")

    lines.extend(["", "## Flagged skill overlaps", ""])
    if report["skill_findings"]:
        for item in report["skill_findings"]:
            lines.append(f"### Incoming skill: `{item['path']}`")
            lines.append("")
            for match in item["matches"]:
                lines.extend(
                    [
                        f"- Matched existing skill: `{match['other_path']}`",
                        f"- Overlap score: `{match['score']}` "
                        f"(description `{match['description_overlap']}`, "
                        f"name `{match['name_similarity']}`, tokens `{match['name_token_overlap']}`)",
                        "- Reviewer decision: `<fill: merge into existing | keep separate with sharper boundary | extract shared helper | reject until clarified>`",
                        "- Rationale: `<fill>`",
                        "- Follow-up action: `<fill>`",
                        "",
                    ]
                )
    else:
        lines.append("None.")
        lines.append("")

    lines.extend(["## Flagged script overlaps", ""])
    if report["script_findings"]:
        for item in report["script_findings"]:
            lines.append(f"### Incoming script: `{item['script']}`")
            lines.append("")
            for match in item["matches"]:
                duplicate_label = "exact duplicate" if match["exact_duplicate"] == 1.0 else "near duplicate"
                lines.extend(
                    [
                        f"- Matched existing script: `{match['other_path']}`",
                        f"- Duplicate status: {duplicate_label}",
                        f"- Overlap score: `{match['score']}` "
                        f"(exact `{match['exact_duplicate']}`, "
                        f"stem `{match['stem_similarity']}`, tokens `{match['token_overlap']}`)",
                        "- Reviewer decision: `<fill: merge into existing | keep separate with sharper boundary | extract shared helper | reject until clarified>`",
                        "- Rationale: `<fill>`",
                        "- Follow-up action: `<fill>`",
                        "",
                    ]
                )
    else:
        lines.append("None.")
        lines.append("")

    lines.extend(
        [
            "## Decision log",
            "",
            "| Area | Finding | Resolution | Owner | Follow-up |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    if report["skill_findings"] or report["script_findings"]:
        for item in report["skill_findings"]:
            for match in item["matches"]:
                lines.append(
                    "| skill | "
                    f"{markdown_escape(item['skill'])} vs {markdown_escape(match['other_skill'])} | "
                    "<fill> | <fill> | <fill> |"
                )
        for item in report["script_findings"]:
            for match in item["matches"]:
                lines.append(
                    "| script | "
                    f"{markdown_escape(Path(item['script']).name)} vs {markdown_escape(Path(match['other_path']).name)} | "
                    "<fill> | <fill> | <fill> |"
                )
    else:
        lines.append("| none | none | none | none | none |")

    lines.extend(
        [
            "",
            "## Blocking issues",
            "",
            "None.",
            "",
            "## Final recommendation",
            "",
            recommendation,
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit merges for overlapping skills and redundant scripts.")
    parser.add_argument("--repo-root", default=".", help="Repository root that contains the skills/ directory.")
    parser.add_argument("--base-ref", help="Git base ref for diff review.")
    parser.add_argument("--head-ref", help="Git head ref for diff review.")
    parser.add_argument(
        "--changed-path",
        action="append",
        default=[],
        help="Explicit changed path. Repeat for multiple paths.",
    )
    parser.add_argument("--threshold", type=float, default=0.45, help="Minimum overlap score to report.")
    parser.add_argument("--top", type=int, default=5, help="Maximum matches to keep per finding.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--report-out", help="Write a Markdown merge review report to this path.")
    parser.add_argument("--report-title", help="Override the report scope/title.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        raise FileNotFoundError(f"Repo root does not exist: {repo_root}")
    if args.base_ref and not args.head_ref:
        raise ValueError("--head-ref is required when --base-ref is provided.")
    if args.head_ref and not args.base_ref:
        raise ValueError("--base-ref is required when --head-ref is provided.")

    changed_paths: list[Path] = []
    if args.base_ref and args.head_ref:
        changed_paths.extend(git_changed_paths(repo_root, args.base_ref, args.head_ref))
    for value in args.changed_path:
        changed_paths.append((repo_root / value).resolve())

    skills = discover_skills(repo_root)
    scripts = discover_scripts(repo_root, skills)
    report = build_report(repo_root, skills, scripts, changed_paths, args.threshold, args.top)
    scope_label = args.report_title or default_scope_label(report, args.base_ref, args.head_ref)

    if args.report_out:
        report_path = Path(args.report_out).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            render_markdown_report(report, scope_label=scope_label, threshold=args.threshold),
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print(f"Repo root: {report['repo_root']}")
    if report["changed_paths"]:
        print("Changed paths:")
        for path in report["changed_paths"]:
            print(f"  - {path}")
    else:
        print("Changed paths: <all skills/scripts scanned>")

    if report["skill_findings"]:
        print("\nPotential skill overlaps:")
        for item in report["skill_findings"]:
            print(f"- {item['skill']} ({item['path']})")
            for match in item["matches"]:
                print(
                    "    -> "
                    f"{match['other_skill']} score={match['score']:.3f} "
                    f"(desc={match['description_overlap']:.3f}, "
                    f"name={match['name_similarity']:.3f}, "
                    f"tokens={match['name_token_overlap']:.3f})"
                )
    else:
        print("\nPotential skill overlaps: none above threshold")

    if report["script_findings"]:
        print("\nPotential script overlaps:")
        for item in report["script_findings"]:
            print(f"- {item['script']} [{item['owner']}]")
            for match in item["matches"]:
                print(
                    "    -> "
                    f"{match['other_path']} owner={match['other_owner']} score={match['score']:.3f} "
                    f"(exact={match['exact_duplicate']:.3f}, "
                    f"stem={match['stem_similarity']:.3f}, "
                    f"tokens={match['token_overlap']:.3f})"
                )
    else:
        print("\nPotential script overlaps: none above threshold")

    if args.report_out:
        print(f"\nMarkdown report written to: {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
