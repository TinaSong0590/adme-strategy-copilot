from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from services.skill_loader import SkillLoader


class SkillLoaderTests(unittest.TestCase):
    def test_primary_directory_has_priority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = root / "primary"
            fallback = root / "fallback"
            primary.mkdir()
            fallback.mkdir()
            (primary / "demo.md").write_text("primary", encoding="utf-8")
            (fallback / "demo.md").write_text("fallback", encoding="utf-8")

            loader = SkillLoader(primary_dir=primary, fallback_dir=fallback)
            skill = loader.load("demo")

            self.assertEqual(skill.content, "primary")
            self.assertTrue(skill.source.startswith("openclaw:"))


if __name__ == "__main__":
    unittest.main()
