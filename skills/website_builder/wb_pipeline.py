from __future__ import annotations

import uuid
from pathlib import Path

from wb_config import PROJECTS_DIR, ensure_projects_dirs, load_env
from wb_deploy import dispatch_deployment
from wb_git import GitProviderError, finalize_repo_changes, list_repositories, prepare_repo_workspace
from wb_models import GitResult
from wb_planner import build_project_spec
from wb_scaffold import scaffold_project


def _resolve_local_workspace(spec_slug: str) -> tuple[str, Path]:
    project_id = str(uuid.uuid4())[:8]
    project_folder = f"{spec_slug}-{project_id}"
    return project_id, PROJECTS_DIR / project_folder


def build_project(prompt: str, **kwargs) -> dict:
    try:
        load_env()
        ensure_projects_dirs()

        git_provider = kwargs.get("git_provider")
        git_repo = kwargs.get("git_repo")
        if git_provider and not git_repo:
            selection = list_repositories(git_provider)
            return {
                "status": "selection_required",
                "message": selection.message,
                "git": selection.to_dict(),
            }

        spec = build_project_spec(prompt, **kwargs)

        git_workspace = None
        git_ready: GitResult | None = None
        if spec.git.provider and spec.git.repo:
            git_workspace, git_ready = prepare_repo_workspace(spec.git, spec.slug)
            if git_ready.branch and not spec.git.branch:
                spec.git.branch = git_ready.branch
            project_id = str(uuid.uuid4())[:8]
            target_subdir = spec.git.repo_subdir or spec.slug
            project_path = git_workspace / target_subdir
            project_path.mkdir(parents=True, exist_ok=True)
        else:
            project_id, project_path = _resolve_local_workspace(spec.slug)
            project_path.mkdir(parents=True, exist_ok=True)

        scaffolded_files = scaffold_project(spec, project_path)
        deployment, integrations = dispatch_deployment(spec, project_path)

        git_result = git_ready
        if git_workspace and git_ready:
            git_result = finalize_repo_changes(git_workspace, spec.git, spec.summary)

        url = deployment.url
        return {
            "status": "success",
            "projectId": project_id,
            "path": str(project_path),
            "url": url,
            "site_name": spec.site_name,
            "projectType": spec.project_type,
            "deployTarget": spec.deploy_target,
            "spec": spec.to_dict(),
            "files": scaffolded_files,
            "deployment": deployment.to_dict(),
            "integrations": [item.to_dict() for item in integrations],
            "git": git_result.to_dict() if git_result else None,
        }
    except GitProviderError as exc:
        return {"status": "error", "error": str(exc), "category": "git"}
    except Exception as exc:  # pragma: no cover - safety net for runtime use
        return {"status": "error", "error": str(exc)}
