from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"


class SkillMetadataTests(unittest.TestCase):
    def test_repo_internal_skill_links_are_relative(self) -> None:
        offenders: list[str] = []
        for skill_file in sorted(SKILLS_ROOT.rglob("SKILL.md")):
            content = skill_file.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                if "references/" not in target and "scripts/" not in target:
                    continue
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                if target.startswith("/") or re.match(r"^[A-Za-z]:[/\\]", target):
                    offenders.append(f"{skill_file.relative_to(ROOT)} -> {target}")
                if ".codex/skills/" in target or ".codex\\skills\\" in target:
                    offenders.append(f"{skill_file.relative_to(ROOT)} -> {target}")
        self.assertFalse(
            offenders,
            "Repo-internal skill links must stay relative:\n" + "\n".join(offenders),
        )

    def test_skill_docs_do_not_embed_user_specific_absolute_paths(self) -> None:
        patterns = (
            re.compile(r"/[A-Za-z]:/Users/"),
            re.compile(r"[A-Za-z]:\\\\Users\\\\"),
            re.compile(r"/Users/[A-Za-z0-9._-]+/"),
        )
        offenders: list[str] = []
        for skill_file in sorted(SKILLS_ROOT.rglob("SKILL.md")):
            content = skill_file.read_text(encoding="utf-8")
            for pattern in patterns:
                if pattern.search(content):
                    offenders.append(str(skill_file.relative_to(ROOT)))
                    break
        self.assertFalse(
            offenders,
            "User-specific absolute paths should not appear in skill docs:\n"
            + "\n".join(offenders),
        )


if __name__ == "__main__":
    unittest.main()
