from __future__ import annotations

import base64
import json
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from wb_config import REPO_CACHE_DIR, get_env
from wb_models import GitResult, GitOptions


class GitProviderError(RuntimeError):
    pass


def _run_git(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *cmd], cwd=cwd, capture_output=True, text=True)


def _request_json(url: str, headers: dict[str, str] | None = None) -> Any:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


class BaseProvider:
    name = "base"

    def list_repositories(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def authenticated_clone_url(self, repo: dict[str, Any]) -> str:
        raise NotImplementedError

    def token(self) -> str:
        raise NotImplementedError

    def normalize_repo(self, repo_name: str) -> dict[str, Any]:
        for repo in self.list_repositories():
            full_name = repo.get("full_name") or repo.get("name")
            if full_name == repo_name:
                return repo
        raise GitProviderError(f"Repository '{repo_name}' was not found for provider '{self.name}'.")


class GitHubProvider(BaseProvider):
    name = "github"

    def token(self) -> str:
        token = get_env("GITHUB_TOKEN")
        if not token:
            raise GitProviderError("Missing GITHUB_TOKEN.")
        return token

    def list_repositories(self) -> list[dict[str, Any]]:
        data = _request_json(
            "https://api.github.com/user/repos?per_page=100&sort=updated",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token()}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        return [
            {
                "full_name": item["full_name"],
                "default_branch": item.get("default_branch"),
                "clone_url": item.get("clone_url"),
                "html_url": item.get("html_url"),
            }
            for item in data
        ]

    def authenticated_clone_url(self, repo: dict[str, Any]) -> str:
        parsed = urllib.parse.urlparse(repo["clone_url"])
        return f"https://x-access-token:{self.token()}@{parsed.netloc}{parsed.path}"


class GitLabProvider(BaseProvider):
    name = "gitlab"

    def token(self) -> str:
        token = get_env("GITLAB_TOKEN")
        if not token:
            raise GitProviderError("Missing GITLAB_TOKEN.")
        return token

    def list_repositories(self) -> list[dict[str, Any]]:
        data = _request_json(
            "https://gitlab.com/api/v4/projects?membership=true&simple=true&per_page=100",
            headers={"PRIVATE-TOKEN": self.token()},
        )
        return [
            {
                "full_name": item["path_with_namespace"],
                "default_branch": item.get("default_branch"),
                "clone_url": item.get("http_url_to_repo"),
                "html_url": item.get("web_url"),
            }
            for item in data
        ]

    def authenticated_clone_url(self, repo: dict[str, Any]) -> str:
        parsed = urllib.parse.urlparse(repo["clone_url"])
        return f"https://oauth2:{self.token()}@{parsed.netloc}{parsed.path}"


class BitbucketProvider(BaseProvider):
    name = "bitbucket"

    def _auth_header(self) -> str:
        username = get_env("BITBUCKET_USERNAME")
        password = get_env("BITBUCKET_APP_PASSWORD") or get_env("BITBUCKET_TOKEN")
        if not username or not password:
            raise GitProviderError("Missing BITBUCKET_USERNAME or BITBUCKET_APP_PASSWORD.")
        token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
        return f"Basic {token}"

    def token(self) -> str:
        return self._auth_header()

    def list_repositories(self) -> list[dict[str, Any]]:
        workspace = get_env("BITBUCKET_WORKSPACE")
        if not workspace:
            raise GitProviderError("Missing BITBUCKET_WORKSPACE for repository listing.")
        data = _request_json(
            f"https://api.bitbucket.org/2.0/repositories/{workspace}?role=member&pagelen=100",
            headers={"Authorization": self._auth_header()},
        )
        repos = []
        for item in data.get("values", []):
            clone_links = [link for link in item.get("links", {}).get("clone", []) if link.get("name") == "https"]
            clone_url = clone_links[0]["href"] if clone_links else None
            repos.append(
                {
                    "full_name": item.get("full_name"),
                    "default_branch": item.get("mainbranch", {}).get("name"),
                    "clone_url": clone_url,
                    "html_url": item.get("links", {}).get("html", {}).get("href"),
                }
            )
        return repos

    def authenticated_clone_url(self, repo: dict[str, Any]) -> str:
        parsed = urllib.parse.urlparse(repo["clone_url"])
        username = urllib.parse.quote(get_env("BITBUCKET_USERNAME", ""), safe="")
        password = urllib.parse.quote(get_env("BITBUCKET_APP_PASSWORD") or get_env("BITBUCKET_TOKEN", ""), safe="")
        return f"https://{username}:{password}@{parsed.netloc}{parsed.path}"


def get_provider(name: str) -> BaseProvider:
    normalized = (name or "").lower()
    if normalized == "github":
        return GitHubProvider()
    if normalized == "gitlab":
        return GitLabProvider()
    if normalized == "bitbucket":
        return BitbucketProvider()
    raise GitProviderError(f"Unsupported git provider '{name}'.")


def list_repositories(provider_name: str) -> GitResult:
    provider = get_provider(provider_name)
    repos = provider.list_repositories()
    return GitResult(
        provider=provider.name,
        status="selection_required",
        message="Select one of the returned repositories and rerun with git_repo.",
        available_repos=repos,
    )


def prepare_repo_workspace(git: GitOptions, project_slug: str) -> tuple[Path, GitResult]:
    if not git.provider or not git.repo:
        raise GitProviderError("Both git provider and repo are required.")
    provider = get_provider(git.provider)
    repo = provider.normalize_repo(git.repo)
    branch = git.branch or repo.get("default_branch") or "main"
    checkout_dir = Path(tempfile.mkdtemp(prefix=f"{project_slug}-", dir=str(REPO_CACHE_DIR)))
    clone_result = _run_git(["clone", provider.authenticated_clone_url(repo), str(checkout_dir)])
    if clone_result.returncode != 0:
        raise GitProviderError(clone_result.stderr.strip() or "Failed to clone repository.")

    branch_check = _run_git(["checkout", branch], cwd=checkout_dir)
    if branch_check.returncode != 0:
        create_branch = _run_git(["checkout", "-b", branch], cwd=checkout_dir)
        if create_branch.returncode != 0:
            raise GitProviderError(create_branch.stderr.strip() or "Failed to check out git branch.")

    details = {"html_url": repo.get("html_url"), "clone_path": str(checkout_dir)}
    return checkout_dir, GitResult(
        provider=provider.name,
        status="ready",
        message="Repository cloned successfully.",
        repo=git.repo,
        branch=branch,
        details=details,
    )


def finalize_repo_changes(repo_path: Path, git: GitOptions, spec_summary: str) -> GitResult:
    branch = git.branch or "main"
    author_name = get_env("GIT_AUTHOR_NAME", "Shipstack Bot")
    author_email = get_env("GIT_AUTHOR_EMAIL", "shipstack@example.com")
    _run_git(["config", "user.name", author_name], cwd=repo_path)
    _run_git(["config", "user.email", author_email], cwd=repo_path)
    add_result = _run_git(["add", "."], cwd=repo_path)
    if add_result.returncode != 0:
        raise GitProviderError(add_result.stderr.strip() or "Failed to stage repository changes.")

    commit_message = git.commit_message or f"Shipstack: update project for {spec_summary[:48]}"
    commit_result = _run_git(["commit", "-m", commit_message], cwd=repo_path)
    commit_output = f"{commit_result.stdout}\n{commit_result.stderr}".lower()
    if commit_result.returncode != 0 and "nothing to commit" not in commit_output:
        raise GitProviderError(commit_result.stderr.strip() or "Failed to commit repository changes.")

    if git.push:
        push_result = _run_git(["push", "-u", "origin", branch], cwd=repo_path)
        if push_result.returncode != 0:
            raise GitProviderError(push_result.stderr.strip() or "Failed to push repository changes.")

    return GitResult(
        provider=git.provider or "unknown",
        status="pushed" if git.push else "committed",
        message="Repository updated successfully." if git.push else "Repository updated locally.",
        repo=git.repo,
        branch=branch,
        details={"path": str(repo_path)},
    )


def cleanup_repo_workspace(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
