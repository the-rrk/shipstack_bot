from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from wb_config import get_env
from wb_models import DeploymentResult, IntegrationResult, ProjectSpec


def _extract_https_url(output: str) -> str | None:
    match = re.search(r"https://[^\s]+", output)
    return match.group(0) if match else None


def _run_command(cmd: list[str], cwd: Path, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)


def deploy_to_vercel(project_path: Path) -> DeploymentResult:
    token = get_env("VERCEL_TOKEN")
    if not token:
        return DeploymentResult(
            target="vercel",
            status="prepared",
            message="VERCEL_TOKEN is missing. Project was prepared for Vercel but not deployed.",
        )
    vercel_cmd = "vercel.cmd" if os.name == "nt" else "vercel"
    if not shutil.which(vercel_cmd):
        return DeploymentResult(
            target="vercel",
            status="prepared",
            message="Vercel CLI is not installed. Project was prepared for Vercel.",
            details={"command": f"{vercel_cmd} --prod --yes --public --token <token>"},
        )
    cmd = [vercel_cmd, "--prod", "--yes", "--public", "--token", token]
    scope = get_env("VERCEL_SCOPE")
    if scope:
        cmd.extend(["--scope", scope])
    result = _run_command(cmd, cwd=project_path)
    if result.returncode != 0:
        return DeploymentResult(
            target="vercel",
            status="error",
            message="Vercel deployment failed.",
            details={"stderr": result.stderr.strip(), "stdout": result.stdout.strip()},
        )
    url = _extract_https_url(result.stdout.strip())
    return DeploymentResult(
        target="vercel",
        status="deployed",
        message="Project deployed to Vercel.",
        url=url,
        details={"stdout": result.stdout.strip()},
    )


def deploy_to_railway(project_path: Path) -> DeploymentResult:
    token = get_env("RAILWAY_TOKEN")
    railway_cmd = "railway.cmd" if os.name == "nt" else "railway"
    if not token:
        return DeploymentResult(
            target="railway",
            status="prepared",
            message="RAILWAY_TOKEN is missing. Project was prepared for Railway but not deployed.",
            details={"command": f"{railway_cmd} up --detach --ci"},
        )
    if not shutil.which(railway_cmd):
        return DeploymentResult(
            target="railway",
            status="prepared",
            message="Railway CLI is not installed. Project was prepared for Railway.",
            details={"command": f"{railway_cmd} up --detach --ci"},
        )
    result = _run_command([railway_cmd, "up", "--detach", "--ci"], cwd=project_path, extra_env={"RAILWAY_TOKEN": token})
    if result.returncode != 0:
        return DeploymentResult(
            target="railway",
            status="error",
            message="Railway deployment failed.",
            details={"stderr": result.stderr.strip(), "stdout": result.stdout.strip()},
        )
    url = _extract_https_url(result.stdout.strip() or result.stderr.strip())
    return DeploymentResult(
        target="railway",
        status="deployed" if url else "prepared",
        message="Project submitted to Railway." if url else "Project prepared for Railway.",
        url=url,
        details={"stdout": result.stdout.strip()},
    )


def prepare_supabase(spec: ProjectSpec, project_path: Path) -> IntegrationResult:
    required = {
        "SUPABASE_URL": bool(get_env("SUPABASE_URL")),
        "SUPABASE_ANON_KEY": bool(get_env("SUPABASE_ANON_KEY")),
        "SUPABASE_SERVICE_ROLE_KEY": bool(get_env("SUPABASE_SERVICE_ROLE_KEY")),
        "SUPABASE_PROJECT_REF": bool(get_env("SUPABASE_PROJECT_REF")),
    }
    configured = required["SUPABASE_URL"] and required["SUPABASE_ANON_KEY"]
    dashboard_url = None
    project_ref = get_env("SUPABASE_PROJECT_REF")
    if project_ref:
        dashboard_url = f"https://supabase.com/dashboard/project/{project_ref}"
    return IntegrationResult(
        kind="supabase",
        status="configured" if configured else "prepared",
        message=(
            "Supabase environment variables were detected and the generated app is wired for Supabase."
            if configured
            else "Supabase files were generated. Add Supabase credentials to finish wiring the app."
        ),
        details={
            "configured_env": required,
            "dashboard_url": dashboard_url,
            "migration_path": str(project_path / "supabase" / "migrations" / "20260315000000_initial.sql"),
        },
    )


def dispatch_deployment(spec: ProjectSpec, project_path: Path) -> tuple[DeploymentResult, list[IntegrationResult]]:
    integrations: list[IntegrationResult] = []
    if spec.use_supabase or spec.deploy_target == "supabase":
        integrations.append(prepare_supabase(spec, project_path))

    if spec.deploy_target == "railway":
        return deploy_to_railway(project_path), integrations
    if spec.deploy_target == "vercel":
        return deploy_to_vercel(project_path), integrations
    if spec.deploy_target == "supabase":
        return (
            DeploymentResult(
                target="supabase",
                status="configured" if integrations else "prepared",
                message="Supabase integration artifacts were generated.",
                url=integrations[0].details.get("dashboard_url") if integrations else None,
            ),
            integrations,
        )
    return (
        DeploymentResult(
            target="local",
            status="prepared",
            message="Project generated locally. No remote deployment was requested.",
        ),
        integrations,
    )
