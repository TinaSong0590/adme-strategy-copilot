from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from utils.models import SkillDocument


@dataclass(slots=True)
class SkillLoader:
    primary_dir: Path
    fallback_dir: Path

    def load_many(self, names: list[str]) -> dict[str, SkillDocument]:
        loaded: dict[str, SkillDocument] = {}
        for name in names:
            loaded[name] = self.load(name)
        return loaded

    def load(self, skill_name: str) -> SkillDocument:
        resolved = self.resolve(skill_name)
        text = resolved.read_text(encoding="utf-8")
        return SkillDocument(name=skill_name, path=resolved, content=text, source=self._source_label(resolved))

    def resolve(self, skill_name: str) -> Path:
        normalized = skill_name[:-3] if skill_name.endswith(".md") else skill_name
        candidates = [
            self.primary_dir / f"{normalized}.md",
            self.primary_dir / normalized / "SKILL.md",
            self.fallback_dir / f"{normalized}.md",
            self.fallback_dir / normalized / "SKILL.md",
        ]
        for path in candidates:
            if path.exists():
                return path
        searched = "\n".join(f"- {path}" for path in candidates)
        raise FileNotFoundError(f"Skill '{skill_name}' not found. Checked:\n{searched}")

    def _source_label(self, path: Path) -> str:
        if self.primary_dir in path.parents or path == self.primary_dir:
            return f"openclaw:{path}"
        return f"project:{path}"
