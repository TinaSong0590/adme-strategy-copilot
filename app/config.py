from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path("/home/knan/adme_strategy_copilot")
OPENCLAW_ROOT = Path("/home/knan/.openclaw")
OPENCLAW_SKILLS_DIR = OPENCLAW_ROOT / "workspace" / "skills"
PROJECT_SKILLS_DIR = PROJECT_ROOT / "skills"
REPORTS_DIR = PROJECT_ROOT / "reports"
PROJECT_ENV_FILE = PROJECT_ROOT / ".env"
OPENCLAW_ENV_FILE = OPENCLAW_ROOT / ".env"


def load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE pairs without requiring third-party packages."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def bootstrap_environment() -> None:
    load_env_file(OPENCLAW_ENV_FILE)
    load_env_file(PROJECT_ENV_FILE)


def get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(slots=True)
class AppConfig:
    project_root: Path = PROJECT_ROOT
    reports_dir: Path = REPORTS_DIR
    openclaw_skills_dir: Path = OPENCLAW_SKILLS_DIR
    project_skills_dir: Path = PROJECT_SKILLS_DIR
    openclaw_env_file: Path = OPENCLAW_ENV_FILE
    project_env_file: Path = PROJECT_ENV_FILE
    openai_api_key: str = ""
    openai_base_url: str = ""
    model: str = ""
    http_proxy: str = ""
    https_proxy: str = ""
    enable_real_literature_search: bool = True
    literature_provider: str = "europe_pmc"
    europe_pmc_base_url: str = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    pubmed_esearch_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    pubmed_esummary_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    pubmed_efetch_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    enable_secondary_literature_provider: bool = True
    secondary_literature_provider: str = "pubmed"
    literature_timeout: int = 20
    literature_max_results: int = 5

    @property
    def llm_extensions_enabled(self) -> bool:
        return bool(self.openai_api_key and self.model)

    @property
    def environment_summary(self) -> dict[str, str]:
        return {
            "openclaw_skills_dir": str(self.openclaw_skills_dir),
            "project_skills_dir": str(self.project_skills_dir),
            "project_env_loaded": str(self.project_env_file.exists()),
            "openclaw_env_loaded": str(self.openclaw_env_file.exists()),
            "http_proxy_configured": str(bool(self.http_proxy)),
            "https_proxy_configured": str(bool(self.https_proxy)),
            "llm_extensions_enabled": str(self.llm_extensions_enabled),
            "enable_real_literature_search": str(self.enable_real_literature_search),
            "literature_provider": self.literature_provider,
            "enable_secondary_literature_provider": str(self.enable_secondary_literature_provider),
            "secondary_literature_provider": self.secondary_literature_provider,
            "literature_timeout": str(self.literature_timeout),
            "literature_max_results": str(self.literature_max_results),
        }


def get_config() -> AppConfig:
    bootstrap_environment()
    return AppConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_base_url=os.getenv("OPENAI_BASE_URL", ""),
        model=os.getenv("MODEL", ""),
        http_proxy=os.getenv("HTTP_PROXY", os.getenv("http_proxy", "")),
        https_proxy=os.getenv("HTTPS_PROXY", os.getenv("https_proxy", "")),
        enable_real_literature_search=get_bool_env("ENABLE_REAL_LITERATURE_SEARCH", True),
        literature_provider=os.getenv("LITERATURE_PROVIDER", "europe_pmc"),
        europe_pmc_base_url=os.getenv(
            "EUROPE_PMC_BASE_URL",
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        ),
        pubmed_esearch_url=os.getenv(
            "PUBMED_ESEARCH_URL",
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        ),
        pubmed_esummary_url=os.getenv(
            "PUBMED_ESUMMARY_URL",
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        ),
        pubmed_efetch_url=os.getenv(
            "PUBMED_EFETCH_URL",
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        ),
        enable_secondary_literature_provider=get_bool_env("ENABLE_SECONDARY_LITERATURE_PROVIDER", True),
        secondary_literature_provider=os.getenv("SECONDARY_LITERATURE_PROVIDER", "pubmed"),
        literature_timeout=get_int_env("LITERATURE_TIMEOUT", 20),
        literature_max_results=get_int_env("LITERATURE_MAX_RESULTS", 5),
    )
