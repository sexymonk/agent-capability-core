from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path, extra_modules: dict[str, types.ModuleType] | None = None):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    if extra_modules:
        with patch.dict(sys.modules, extra_modules, clear=False):
            spec.loader.exec_module(module)
    else:
        spec.loader.exec_module(module)
    return module


class SkillScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.openai_module = load_module(
            "check_openai_api_test",
            ROOT / "skills" / "openai-api-smoke-test" / "scripts" / "check_openai_api.py",
        )
        pil_module = types.ModuleType("PIL")
        pil_image_module = types.ModuleType("PIL.Image")
        pil_module.Image = pil_image_module
        cls.sequence_module = load_module(
            "sequence_to_video_test",
            ROOT / "skills" / "screenshot-sequence-video" / "scripts" / "sequence_to_video.py",
            extra_modules={"PIL": pil_module, "PIL.Image": pil_image_module},
        )

    def test_check_chat_handles_request_exception(self) -> None:
        args = types.SimpleNamespace(
            secret_key_env="OPENAI_API_KEY",
            chat_model="gpt-4.1-mini",
            base_url="https://api.openai.com",
            timeout=3.0,
        )
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            with patch.object(
                self.openai_module.requests,
                "request",
                side_effect=self.openai_module.requests.ConnectionError("network down"),
            ):
                result = self.openai_module.check_chat(args)
        self.assertFalse(result["ok"])
        self.assertIsNone(result["status"])
        self.assertEqual("ConnectionError", result["error"]["type"])
        self.assertIn("network down", result["error"]["message"])
        self.assertIn("latency_ms", result)

    def test_resolve_ffmpeg_prefers_ffmpeg_bin_env(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ffmpeg_path = Path(temp_dir) / "ffmpeg-custom"
            ffmpeg_path.write_text("", encoding="utf-8")
            with patch.dict(os.environ, {"FFMPEG_BIN": str(ffmpeg_path)}, clear=False):
                with patch.object(self.sequence_module.shutil, "which", return_value="/usr/bin/ffmpeg"):
                    resolved = self.sequence_module.resolve_ffmpeg(None)
        self.assertEqual(ffmpeg_path.resolve(), resolved.resolve())

    def test_resolve_ffmpeg_uses_ffmpeg_path_env(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ffmpeg_path = Path(temp_dir) / "ffmpeg-secondary"
            ffmpeg_path.write_text("", encoding="utf-8")
            with patch.dict(
                os.environ,
                {"FFMPEG_BIN": "", "FFMPEG_PATH": str(ffmpeg_path)},
                clear=False,
            ):
                with patch.object(self.sequence_module.shutil, "which", return_value=None):
                    resolved = self.sequence_module.resolve_ffmpeg(None)
        self.assertEqual(ffmpeg_path.resolve(), resolved.resolve())


if __name__ == "__main__":
    unittest.main()
