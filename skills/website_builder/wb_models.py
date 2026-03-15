from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Feature:
    title: str
    description: str


@dataclass
class DataEntity:
    name: str
    columns: list[str] = field(default_factory=list)


@dataclass
class ApiRoute:
    method: str
    path: str
    summary: str


@dataclass
class GitOptions:
    provider: str | None = None
    repo: str | None = None
    branch: str | None = None
    repo_subdir: str | None = None
    push: bool = True
    commit_message: str | None = None


@dataclass
class ProjectSpec:
    prompt: str
    site_name: str
    slug: str
    summary: str
    title: str
    subtitle: str
    cta_text: str
    project_type: str
    deploy_target: str
    auth_required: bool = False
    use_supabase: bool = False
    features: list[Feature] = field(default_factory=list)
    entities: list[DataEntity] = field(default_factory=list)
    api_routes: list[ApiRoute] = field(default_factory=list)
    primary_color: str = "#3498db"
    gradient_start: str = "#2c3e50"
    gradient_end: str = "#3498db"
    raw_blueprint: dict[str, Any] = field(default_factory=dict)
    git: GitOptions = field(default_factory=GitOptions)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class IntegrationResult:
    kind: str
    status: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DeploymentResult:
    target: str
    status: str
    message: str
    url: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GitResult:
    provider: str
    status: str
    message: str
    repo: str | None = None
    branch: str | None = None
    available_repos: list[dict[str, Any]] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
