# Running Shipstack

This guide shows how to run Shipstack locally for:

- direct project generation from the `website_builder` skill
- full-stack app scaffolding with Railway and Supabase preparation
- bot mode through the OpenClaw gateway

## Prerequisites

- `Node.js` 22 or newer
- `pnpm`
- `Python` 3.10 or newer
- optional: `vercel` CLI for Vercel deploys
- optional: `railway` CLI for Railway deploys

Install optional CLIs if you want real deployments:

```bash
npm install -g vercel
npm install -g @railway/cli
```

## 1. Install Dependencies

From the repo root:

```bash
pnpm install
python -m venv .venv
```

Activate the virtual environment:

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows `cmd.exe`:

```bat
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Then install the Python packages:

```bash
pip install -r requirements.txt
```

## 2. Create `.env`

There is currently no `.env.example` in this repo, so create a `.env` file in the repo root manually.

Minimum local setup:

```env
OPENAI_API_KEY=sk-your-openai-key
```

Optional deployment and integration variables:

```env
VERCEL_TOKEN=your-vercel-token
VERCEL_SCOPE=your-vercel-team

RAILWAY_TOKEN=your-railway-token

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_PROJECT_REF=your-project-ref

GITHUB_TOKEN=ghp_your-token
GITLAB_TOKEN=glpat-your-token
BITBUCKET_USERNAME=your-username
BITBUCKET_APP_PASSWORD=your-app-password
BITBUCKET_WORKSPACE=your-workspace

TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

Notes:

- If `OPENAI_API_KEY` is missing, the builder falls back to a deterministic project blueprint.
- If deploy tokens are missing, Shipstack still generates the project but marks deployment as `prepared` instead of fully deployed.
- If a Git provider token is missing, repo listing and push flows will fail for that provider.

## 3. Build the App

Build the TypeScript side of the repo:

```bash
pnpm build
```

This is mainly needed when you want to run the gateway or other OpenClaw-driven flows.

## 4. Run the Project Builder Directly

The fastest way to use Shipstack is to call the skill handler directly.

From the repo root:

```bash
python skills/website_builder/handler.py "Build a portfolio website for a photographer named Alex"
```

Example full-stack prompt:

```bash
python skills/website_builder/handler.py "Build a customer portal with login, database, and Railway deployment"
```

Expected output includes:

- local project path
- project type
- deploy target
- live URL when one is returned

Generated files are written under `projects/` unless you target a Git repository workflow.

## 5. Run Through the Gateway

If you want to use Shipstack through Telegram or the OpenClaw agent flow:

```bash
pnpm build
pnpm start gateway --allow-unconfigured --port 18789
```

Then send a prompt through your configured bot channel, for example:

```text
Build me a landing page for a SaaS company called CloudSync
```

## 6. Git Provider Usage

The builder supports GitHub, GitLab, and Bitbucket through the `website_builder` pipeline.

Current behavior:

- if you provide only a Git provider, the pipeline returns available repos for selection
- if you provide both provider and repo, the pipeline clones the repo, writes the generated project into a dedicated subdirectory, commits, and can push the branch

Relevant inputs supported by the skill:

- `project_type`
- `deploy_target`
- `use_supabase`
- `git_provider`
- `git_repo`
- `git_branch`
- `repo_subdir`

Important note:

- the direct CLI entrypoint in `skills/website_builder/handler.py` currently accepts only the prompt string from the shell
- provider/repo options are available through the Python `handle()` call and the broader skill invocation path, not as standalone CLI flags yet

## 7. Deployment Behavior

### Vercel

- target: `vercel`
- requires: `VERCEL_TOKEN`
- if `vercel` CLI is installed and token is present, the project is deployed
- otherwise the project is still scaffolded locally

### Railway

- target: `railway`
- requires: `RAILWAY_TOKEN`
- if `railway` CLI is installed and token is present, Shipstack runs a Railway deploy command
- otherwise it prepares Railway-ready files such as `railway.json` and `Dockerfile`

### Supabase

- target: `supabase` or `use_supabase=true`
- Shipstack generates:
  - `supabase/config.toml`
  - SQL migrations under `supabase/migrations/`
- if Supabase env vars are present, the integration result is marked as configured

## 8. Run Tests

Focused builder tests:

```bash
python -m unittest discover -s skills/website_builder/tests -p "test_*.py"
```

Repo-wide tests:

```bash
pnpm test
```

## 9. Troubleshooting

If `python` is not found:

- use the full launcher command on Windows:

```bat
py -3 -m venv .venv
py -3 -m pip install -r requirements.txt
py -3 skills\website_builder\handler.py "Build a landing page"
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.venv\Scripts\Activate.ps1
```

If deployment does not happen:

- check the required token exists in `.env`
- confirm the provider CLI is installed and on `PATH`
- inspect the JSON output from the handler for `deployment.status` and `integrations`

## 10. Most Common Local Flow

If you just want to get it running quickly:

```bash
pnpm install
python -m venv .venv
pip install -r requirements.txt
pnpm build
python skills/website_builder/handler.py "Build a startup landing page for an AI note-taking app"
```
