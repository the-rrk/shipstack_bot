# Shipstack

**Build software with AI. Deploy it anywhere.**

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.npmjs.com/package/shipstack"><img src="https://img.shields.io/npm/v/shipstack?style=for-the-badge" alt="npm version"></a>
</p>

## What is Shipstack?

**Shipstack** is an AI-assisted software shipping tool built on top of [OpenClaw](https://github.com/openclaw/openclaw). It turns natural-language prompts into fully deployed projects.

Describe what you want to build in plain English — Shipstack generates the code, scaffolds the project, and deploys it to the platform of your choice: **Vercel**, **Supabase**, **Railway**, or your own hardware.

OpenClaw provides the AI agent foundation (gateway, agent orchestration, skill system), and Shipstack extends it with deployment automation and project generation workflows.

## Features

- **AI-Powered Generation** — Describe your project in a prompt; Shipstack builds it using OpenAI via OpenClaw's agent system
- **Multi-Platform Deployment** — Deploy to Vercel (supported now), with Supabase, Railway, and self-hosted targets planned
- **Bot Interface** — Interact via Telegram to trigger builds and receive live URLs
- **Smart Scaffolding** — Generates complete HTML, CSS, and JavaScript with AI-tailored content, colors, and copy
- **Project Management** — Each build gets a unique project folder under `projects/`
- **Docker and Railway Ready** — One-click cloud deployment for the Shipstack bot itself

## Installation

### Option 1: npm (recommended)

```bash
npm install -g shipstack
shipstack init
```

### Option 2: From source

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/shipstack.git
cd shipstack

# Install Node.js dependencies
pnpm install

# Set up Python virtual environment
python3 -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys (see Environment Variables below)
```

### Prerequisites

- **Node.js** >= 22
- **Python** >= 3.10
- **pnpm** (recommended) or npm
- **Vercel CLI** — `npm install -g vercel`
- An **OpenAI API key**
- A **Vercel API token**

## Environment Variables

Create a `.env` file in the project root (or copy `.env.example`):

```env
# Required — OpenAI API key for AI content generation
# Get one at: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-api-key

# Required — Vercel token for deployment
# Get one at: https://vercel.com/account/tokens
VERCEL_TOKEN=your-vercel-token

# Optional — Vercel team scope (if deploying under a team)
VERCEL_SCOPE=your-vercel-team

# Optional — Telegram bot token (for bot interface)
# Create a bot via @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

Future deployment targets will use additional variables (e.g. `SUPABASE_ACCESS_TOKEN`, `RAILWAY_TOKEN`).

## Usage

### CLI

Generate and deploy a website directly from the command line:

```bash
# Using the skill handler directly (current)
python skills/website_builder/handler.py "Build a portfolio site for a photographer named Alex"
```

Example output:

```
✅ Website created successfully!
📁 Local path: projects/alex-photography-a1b2c3d4/
🌍 Live URL: https://alex-photography-a1b2c3d4.vercel.app
```

### Bot Interface

Start the gateway to interact via Telegram:

```bash
# Build the project
pnpm build

# Start the gateway
pnpm start gateway --allow-unconfigured --port 18789
```

Then send a message to your Telegram bot:

> "Build me a landing page for a SaaS product called CloudSync that helps teams collaborate in real-time"

The bot generates the site and replies with the live URL.

## Deployment Targets

| Platform            | Status    | Description                               |
| ------------------- | --------- | ----------------------------------------- |
| **Vercel**          | Supported | Static sites deployed via Vercel CLI      |
| **Supabase**        | Planned   | Full-stack apps with database and auth    |
| **Railway**         | Planned   | Backend services and APIs                 |
| **Custom Hardware** | Planned   | Deploy to your own servers via SSH/Docker |

## Deploy Shipstack Itself to Railway

You can self-host the Shipstack bot on Railway:

1. Push this repo to GitHub
2. Connect it to [Railway](https://railway.app)
3. Set your environment variables in Railway's dashboard (`OPENAI_API_KEY`, `VERCEL_TOKEN`, `TELEGRAM_BOT_TOKEN`)
4. Railway uses `railway.json` and `Dockerfile` to build and deploy automatically

The boot script (`scripts/railway-setup.sh`) configures the gateway, sets up the Python environment, and starts the Telegram bot.

## Architecture Overview

```
shipstack/
├── src/                         # Core TypeScript gateway and agent system (OpenClaw)
│   ├── gateway/                 # HTTP gateway server
│   ├── agents/                  # AI agent orchestration
│   ├── cli/                     # CLI commands
│   └── config/                  # Configuration management
│
├── skills/                      # Pluggable AI skills
│   └── website_builder/         # Website generation + Vercel deployment
│       ├── handler.py           # Main skill logic (OpenAI → HTML → Vercel)
│       ├── SKILL.md             # Skill documentation and triggers
│       ├── skill.yaml           # Skill metadata
│       └── templates/           # HTML/CSS/JS base templates
│
├── scripts/                     # Deployment and setup scripts
│   └── railway-setup.sh         # Railway boot script
│
├── projects/                    # Generated project output (gitignored)
├── Dockerfile                   # Container build
├── docker-compose.yml           # Local Docker development
└── railway.json                 # Railway deployment config
```

### How It Works

```mermaid
flowchart LR
  Prompt[User Prompt] --> OpenClaw[OpenClaw Agent]
  OpenClaw --> AIGen[AI Generation]
  AIGen --> Scaffold[Project Scaffolder]
  Scaffold --> Projects["projects/ folder"]
  Projects --> DeployTarget{Deploy Target}
  DeployTarget --> Vercel[Vercel]
  DeployTarget --> Supabase["Supabase (planned)"]
  DeployTarget --> Railway["Railway (planned)"]
  DeployTarget --> Custom["Custom Hardware (planned)"]
```

1. **User sends a prompt** — via CLI or Telegram bot
2. **OpenClaw agent** receives the prompt and routes it to the appropriate skill
3. **AI generates content** — site name, copy, colors, features — as structured JSON via OpenAI
4. **Scaffolder creates files** — `index.html`, `styles.css`, `script.js` in a new project folder
5. **Deployment** — the project is deployed to the chosen platform (currently Vercel) and the live URL is returned

## Built on OpenClaw

Shipstack is built on top of [OpenClaw](https://github.com/openclaw/openclaw), an open-source personal AI assistant. Shipstack uses:

- **Gateway** — OpenClaw's HTTP gateway for routing messages and managing the bot lifecycle
- **Agent System** — AI agent orchestration that processes prompts and invokes skills
- **Skill Infrastructure** — the pluggable skill system (`SKILL.md` + `skill.yaml` + `handler.py`) that Shipstack extends with deployment-focused skills
- **Channel Integrations** — Telegram (and other channels) for the bot interface

## Roadmap

- [ ] Publish as npm package (`npm install -g shipstack`)
- [ ] `shipstack build "prompt"` CLI command
- [ ] More project types — React, Next.js, API backends
- [ ] Supabase integration — full-stack apps with database and auth
- [ ] Railway auto-deploy — backend services and APIs
- [ ] GitHub repo creation for generated projects
- [ ] Custom domain support
- [ ] Interactive editing ("change the hero color to blue")
- [ ] Project templates library
- [ ] Deploy to custom hardware via SSH/Docker

## Contributing

Contributions are welcome!

1. Clone the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests: `pnpm test`
5. Submit a pull request

For larger changes, please open an issue first to discuss the approach.

## License

MIT License — see [LICENSE](LICENSE) for details.
