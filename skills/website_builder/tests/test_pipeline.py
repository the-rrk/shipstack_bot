from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


TESTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = TESTS_DIR.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

import wb_config
import wb_deploy
import wb_pipeline
import wb_planner
from wb_models import GitResult


def build_blueprint(project_type: str, deploy_target: str, use_supabase: bool = False) -> dict:
    return {
        "site_name": "Demo Project",
        "summary": "Generated during tests.",
        "title": "Demo Project",
        "subtitle": "A test scaffold",
        "cta_text": "Launch",
        "project_type": project_type,
        "deploy_target": deploy_target,
        "auth_required": use_supabase or project_type == "fullstack_app",
        "use_supabase": use_supabase,
        "features": [
            {"title": "Feature one", "description": "Description one"},
            {"title": "Feature two", "description": "Description two"},
            {"title": "Feature three", "description": "Description three"},
        ],
        "entities": [{"name": "projects", "columns": ["id uuid primary key", "name text"]}],
        "api_routes": [
            {"method": "GET", "path": "/api/health", "summary": "Health check"},
            {"method": "GET", "path": "/api/items", "summary": "List items"},
        ],
        "primary_color": "#3498db",
        "gradient_start": "#1f2937",
        "gradient_end": "#2563eb",
    }


class WebsiteBuilderPipelineTests(unittest.TestCase):
    def test_infer_project_type_prefers_fullstack_keywords(self):
        project_type = wb_planner.infer_project_type("Build an admin dashboard with auth and a database")
        deploy_target = wb_planner.infer_deploy_target("Deploy this backend on Railway with Supabase auth")

        self.assertEqual(project_type, "fullstack_app")
        self.assertEqual(deploy_target, "railway")

    def test_build_project_generates_local_static_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            projects_dir = Path(tmp) / "projects"
            repo_cache_dir = projects_dir / "_repo_cache"
            with patch.object(wb_config, "PROJECTS_DIR", projects_dir), patch.object(
                wb_config, "REPO_CACHE_DIR", repo_cache_dir
            ), patch.object(wb_pipeline, "PROJECTS_DIR", projects_dir), patch(
                "wb_planner.generate_project_blueprint", return_value=build_blueprint("static_site", "vercel")
            ), patch.dict(
                os.environ,
                {"OPENAI_API_KEY": "", "OPENAI_API_KEY_1": "", "VERCEL_TOKEN": "", "RAILWAY_TOKEN": ""},
                clear=False,
            ):
                result = wb_pipeline.build_project("Build a portfolio website for a designer")
                project_path = Path(result["path"])
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["projectType"], "static_site")
                self.assertTrue((project_path / "index.html").exists())
                self.assertEqual(result["deployment"]["target"], "vercel")
                self.assertEqual(result["deployment"]["status"], "prepared")

    def test_build_project_generates_fullstack_railway_supabase_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            projects_dir = Path(tmp) / "projects"
            repo_cache_dir = projects_dir / "_repo_cache"
            with patch.object(wb_config, "PROJECTS_DIR", projects_dir), patch.object(
                wb_config, "REPO_CACHE_DIR", repo_cache_dir
            ), patch.object(wb_pipeline, "PROJECTS_DIR", projects_dir), patch(
                "wb_planner.generate_project_blueprint",
                return_value=build_blueprint("fullstack_app", "railway", use_supabase=True),
            ), patch.dict(
                os.environ,
                {"OPENAI_API_KEY": "", "OPENAI_API_KEY_1": "", "VERCEL_TOKEN": "", "RAILWAY_TOKEN": ""},
                clear=False,
            ):
                result = wb_pipeline.build_project(
                    "Build a customer portal with auth, data models, and deploy it on Railway with Supabase",
                    project_type="fullstack_app",
                    deploy_target="railway",
                    use_supabase=True,
                )
                project_path = Path(result["path"])
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["projectType"], "fullstack_app")
                self.assertTrue((project_path / "package.json").exists())
                self.assertTrue((project_path / "railway.json").exists())
                self.assertTrue((project_path / "supabase" / "migrations" / "20260315000000_initial.sql").exists())
                self.assertEqual(result["deployment"]["target"], "railway")

    def test_prepare_supabase_marks_configured_when_env_present(self):
        with patch("wb_planner.generate_project_blueprint", return_value=build_blueprint("fullstack_app", "supabase", True)):
            spec = wb_planner.build_project_spec(
                "Build a SaaS dashboard with auth and Supabase",
                project_type="fullstack_app",
                deploy_target="supabase",
                use_supabase=True,
            )
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "",
                "OPENAI_API_KEY_1": "",
                "SUPABASE_URL": "https://example.supabase.co",
                "SUPABASE_ANON_KEY": "anon",
                "SUPABASE_SERVICE_ROLE_KEY": "service",
                "SUPABASE_PROJECT_REF": "abcd1234",
            },
            clear=False,
        ):
            project_path = Path(tmp)
            project_path.mkdir(exist_ok=True)
            integration = wb_deploy.prepare_supabase(spec, project_path)

        self.assertEqual(integration.status, "configured")
        self.assertEqual(integration.details["dashboard_url"], "https://supabase.com/dashboard/project/abcd1234")

    def test_git_provider_without_repo_returns_selection(self):
        selection = GitResult(
            provider="github",
            status="selection_required",
            message="Select a repository.",
            available_repos=[{"full_name": "demo/repo", "default_branch": "main"}],
        )
        with patch.object(wb_pipeline, "list_repositories", return_value=selection):
            result = wb_pipeline.build_project("Update my app", git_provider="github")

        self.assertEqual(result["status"], "selection_required")
        self.assertEqual(result["git"]["available_repos"][0]["full_name"], "demo/repo")


if __name__ == "__main__":
    unittest.main()
