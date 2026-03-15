from __future__ import annotations

import re

from wb_llm import generate_project_blueprint
from wb_models import ApiRoute, DataEntity, Feature, GitOptions, ProjectSpec


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")
    return slug or "shipstack-project"


def infer_project_type(prompt: str, requested: str | None = None) -> str:
    if requested in {"static_site", "fullstack_app"}:
        return requested
    lowered = prompt.lower()
    fullstack_markers = (
        "dashboard",
        "portal",
        "admin",
        "auth",
        "login",
        "database",
        "supabase",
        "railway",
        "api",
        "crud",
        "app",
    )
    return "fullstack_app" if any(marker in lowered for marker in fullstack_markers) else "static_site"


def infer_deploy_target(prompt: str, requested: str | None = None) -> str:
    if requested in {"vercel", "railway", "supabase", "local"}:
        return requested
    lowered = prompt.lower()
    if "railway" in lowered:
        return "railway"
    if "supabase" in lowered:
        return "supabase"
    if "vercel" in lowered:
        return "vercel"
    return "vercel" if infer_project_type(prompt) == "static_site" else "railway"


def _normalize_features(raw: list[dict]) -> list[Feature]:
    features: list[Feature] = []
    for item in raw[:4]:
        title = str(item.get("title", "")).strip()
        description = str(item.get("description", "")).strip()
        if title and description:
            features.append(Feature(title=title, description=description))
    if features:
        return features
    return [
        Feature(title="Generated experience", description="A polished UI scaffolded from your prompt."),
        Feature(title="Deployable runtime", description="Project files are prepared for cloud deployment."),
        Feature(title="Editable codebase", description="Users can keep iterating on the generated app."),
    ]


def _normalize_entities(raw: list[dict]) -> list[DataEntity]:
    entities: list[DataEntity] = []
    for item in raw[:4]:
        name = str(item.get("name", "")).strip().lower()
        columns = [str(column).strip() for column in item.get("columns", []) if str(column).strip()]
        if name:
            entities.append(DataEntity(name=name, columns=columns))
    return entities


def _normalize_api_routes(raw: list[dict]) -> list[ApiRoute]:
    routes: list[ApiRoute] = []
    for item in raw[:5]:
        method = str(item.get("method", "GET")).upper().strip()
        path = str(item.get("path", "")).strip() or "/api/items"
        summary = str(item.get("summary", "")).strip() or "Generated API route"
        routes.append(ApiRoute(method=method, path=path, summary=summary))
    return routes or [ApiRoute(method="GET", path="/api/health", summary="Health check")]


def build_project_spec(prompt: str, **kwargs) -> ProjectSpec:
    requested_project_type = kwargs.get("project_type")
    requested_deploy_target = kwargs.get("deploy_target")
    project_type = infer_project_type(prompt, requested_project_type)
    deploy_target = infer_deploy_target(prompt, requested_deploy_target)
    blueprint = generate_project_blueprint(prompt, project_type, deploy_target)

    resolved_project_type = infer_project_type(prompt, blueprint.get("project_type", project_type))
    resolved_deploy_target = infer_deploy_target(prompt, blueprint.get("deploy_target", deploy_target))
    site_name = str(blueprint.get("site_name") or "Shipstack Project").strip()
    slug = slugify(site_name)

    use_supabase = bool(kwargs.get("use_supabase"))
    if not kwargs.get("use_supabase"):
        use_supabase = bool(blueprint.get("use_supabase")) or resolved_deploy_target == "supabase"

    git = GitOptions(
        provider=kwargs.get("git_provider"),
        repo=kwargs.get("git_repo"),
        branch=kwargs.get("git_branch"),
        repo_subdir=kwargs.get("repo_subdir"),
        push=kwargs.get("git_push", True),
        commit_message=kwargs.get("git_commit_message"),
    )

    return ProjectSpec(
        prompt=prompt,
        site_name=site_name,
        slug=slug,
        summary=str(blueprint.get("summary") or prompt).strip(),
        title=str(blueprint.get("title") or site_name).strip(),
        subtitle=str(blueprint.get("subtitle") or prompt).strip(),
        cta_text=str(blueprint.get("cta_text") or "Get started").strip(),
        project_type=resolved_project_type,
        deploy_target=resolved_deploy_target,
        auth_required=bool(blueprint.get("auth_required")),
        use_supabase=use_supabase,
        features=_normalize_features(blueprint.get("features", [])),
        entities=_normalize_entities(blueprint.get("entities", [])),
        api_routes=_normalize_api_routes(blueprint.get("api_routes", [])),
        primary_color=str(blueprint.get("primary_color") or "#3498db").strip(),
        gradient_start=str(blueprint.get("gradient_start") or "#1f2937").strip(),
        gradient_end=str(blueprint.get("gradient_end") or "#2563eb").strip(),
        raw_blueprint=blueprint,
        git=git,
    )
