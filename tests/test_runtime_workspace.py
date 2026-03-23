from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "scripts" / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from codex_workspace import runtime_config, runtime_exports_root  # type: ignore


class RuntimeWorkspaceTests(unittest.TestCase):
    def test_runtime_config_prefers_runtime_section_and_exports_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "workspace.manifest.yaml").write_text(
                json.dumps({"workspace_id": "demo", "workspace_api_version": 3, "ai_providers": {"external": {"default_home": "~/.agent-runtime/external"}}}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (root / "machine.local.yaml").write_text(
                json.dumps(
                    {
                        "runtime": {
                            "provider": "external",
                            "home": str(root / "runtime-home"),
                            "local_home": str(root / "runtime-local"),
                            "command": "runner.exe",
                            "capabilities": ["chat_bridge"],
                        }
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            config = runtime_config(root)
            self.assertEqual("external", config["provider"])
            self.assertIn("chat_bridge", config["capabilities"])
            self.assertEqual(str((root / "runtime-local" / "demo" / "exports").resolve()).replace("\\", "/"), config["exports_root"])
            self.assertEqual(Path(config["exports_root"]), runtime_exports_root(root))


if __name__ == "__main__":
    unittest.main()
