from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"
REPO_CACHE_DIR = PROJECTS_DIR / "_repo_cache"


def load_env() -> None:
    env_path = ROOT_DIR / ".env"
    if not env_path.exists():
        return
    with env_path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def ensure_projects_dirs() -> None:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    REPO_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


def resolve_openai_api_key() -> str | None:
    return get_env("OPENAI_API_KEY_1") or get_env("OPENAI_API_KEY")
