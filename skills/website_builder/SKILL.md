---
name: website_builder
description: "Generate static sites or full-stack apps from a prompt, prepare Railway or Supabase handlers, and optionally apply the output into a hosted Git repository. Use when users want a new project scaffold, deployment-ready app, or repo modifications driven by a prompt."
metadata:
  {
    "openclaw":
      {
        "emoji": "🌐",
        "requires": { "bins": ["python3"] },
      },
  }
---

# Website And App Builder

Generate deployable software projects from natural language prompts. The skill can produce a static website, scaffold a full-stack app, wire Supabase artifacts, prepare Railway deployment files, and optionally clone a GitHub, GitLab, or Bitbucket repository to apply the generated changes there.

## When to Use

✅ **USE this skill when:**

- "Build me a website for..."
- "Create a landing page for..."
- "Make a portfolio site for..."
- "Build me a customer portal with auth and a database"
- "Deploy this app to Railway"
- "Use Supabase for auth/data"
- "Update my GitHub repo with these changes"

## When NOT to Use

❌ **DON'T use this skill when:**

- The user only wants a code explanation or architecture review
- The user wants low-level manual Git operations unrelated to code generation
- The user has not chosen a repo yet and needs a human review before applying changes
- The user wants arbitrary destructive edits across an existing monorepo root

## Command

Run the builder handler with the user's prompt (using the project's virtual environment):

```bash
.venv/bin/python skills/website_builder/handler.py "<user's website description>"
```

Optional kwargs that the agent may pass:

- `project_type`: `static_site` or `fullstack_app`
- `deploy_target`: `vercel`, `railway`, `supabase`, or `local`
- `use_supabase`: `true` or `false`
- `git_provider`: `github`, `gitlab`, or `bitbucket`
- `git_repo`: repo full name such as `owner/repo`
- `git_branch`: target branch to update/create
- `repo_subdir`: optional subdirectory inside the selected repo

On Windows, direct execution also works:

```bash
.venv/bin/python skills\website_builder\handler.py "<user's website description>"
```

### Example

**User:** "Build a customer dashboard with login, deploy it on Railway, wire Supabase auth, and update my GitHub repo"

```bash
python skills/website_builder/handler.py "Build a customer dashboard with login, deploy it on Railway, wire Supabase auth"
```

### Output

The script returns:

- `✅ Project created successfully!`
- `📁 Local path: projects/<project-name>-<id>/`
- `🧩 Project type: static_site | fullstack_app`
- `🚀 Deploy target: vercel | railway | supabase | local`
- `🌍 Live URL: <when a deploy handler returns one>`
- `git.available_repos` when a Git provider is supplied without a repo

## What Gets Generated

For static projects, the handler creates:

1. **index.html** - Modern, responsive HTML with:
   - Hero section
   - Features/services cards
   - Contact section
   - Footer

2. **styles.css** - Professional CSS with:
   - Theme colors
   - Gradient hero background
   - Responsive layout

3. **script.js** - Interactive JavaScript:
   - Form handling

For full-stack projects, the handler creates:

1. **server.js** - Express-based API and static file host
2. **public/** - Frontend assets for the generated app
3. **package.json** - Runtime dependencies and start scripts
4. **railway.json** and **Dockerfile** - Railway-ready deployment files
5. **supabase/** - Config and SQL migration artifacts when Supabase is enabled
6. **shipstack.project.json** - Generated project metadata for later automation

## Response Format

After running the command, respond to the user with:

```
✅ I've created your project!

🧩 **Project type:** [static_site or fullstack_app]
🚀 **Deploy target:** [vercel, railway, supabase, or local]
🌍 **Live URL:** [if available]
📁 **Local files:** [paste the path]
🔧 **Git status:** [selection required, ready, committed, or pushed]

The project includes:
- [Brief summary]
- Generated app files
- Deployment-ready config
- Integration artifacts when requested
- Repo update details when a git provider was used

If `git.available_repos` is returned, ask the user which repo to use next.
```

## Requirements

- `python3` - Python 3.x interpreter
- Optional `vercel` CLI plus `VERCEL_TOKEN` for Vercel deployment
- Optional Railway CLI plus `RAILWAY_TOKEN` for Railway deployment
- Optional Git provider tokens:
  - `GITHUB_TOKEN`
  - `GITLAB_TOKEN`
  - `BITBUCKET_USERNAME`, `BITBUCKET_APP_PASSWORD`, `BITBUCKET_WORKSPACE`
- Optional Supabase env vars:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `SUPABASE_PROJECT_REF`
- Optional `OPENAI_API_KEY_1` or `OPENAI_API_KEY` for richer AI-generated blueprints

## Notes

- Without OpenAI credentials, the skill falls back to a deterministic project blueprint
- When targeting a hosted Git repo without `git_repo`, the skill returns a repo list instead of mutating anything
- Repo updates default to a generated subdirectory inside the cloned repo unless `repo_subdir` is specified
- Supabase is currently integrated by generating config and migration assets plus env validation
