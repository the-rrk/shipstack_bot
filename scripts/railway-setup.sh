#!/bin/bash
set -e

echo "🚀 Starting ShipStack Railway Setup..."

# Ensure we're in the app directory
cd /app

# 1. Force gateway mode to local
echo "🔹 Configuring gateway mode..."
node openclaw.mjs config set gateway.mode local

# 2. Disable Control UI for security/CSRF on public URLs
echo "🔹 Disabling Control UI..."
node openclaw.mjs config set gateway.controlUi.enabled false

# 3. Configure Telegram access policy
# "dmPolicy: open" and "allowFrom: ['*']" allows anyone to message the bot
echo "🔹 Configuring Telegram access (Policy: open)..."
node openclaw.mjs config set channels.telegram.dmPolicy open
node openclaw.mjs config set channels.telegram.allowFrom '["*"]'
node openclaw.mjs config set channels.telegram.groupPolicy open

# 3b. Optional: set up Python venv for website_builder skill
echo "🔹 Setting up Python venv for website_builder (optional)..."
if command -v python3 >/dev/null 2>&1; then
  python3 -m venv /app/.venv || true
  # shellcheck source=/dev/null
  . /app/.venv/bin/activate || true
  pip install --upgrade pip || true
  pip install openai || true
fi

echo "🔹 Setting default model to openai/gpt-5.1-codex..."
node openclaw.mjs config set agents.defaults.model "openai/gpt-5.1-codex"

# 4. Bind the default agent to the telegram channel
# This ensures messages are routed to your AI agent
echo "🔹 Binding agent 'dev' to telegram..."
node openclaw.mjs agents bind --agent dev --bind telegram || true

# 5. Run doctor --fix to onboard Telegram/OpenAI from environment variables
echo "🔹 Running OpenClaw Doctor..."
node openclaw.mjs doctor --fix

echo "✅ Setup complete. Starting Gateway..."

# 6. Start the gateway in the foreground using Railway-assigned PORT
exec node openclaw.mjs gateway run --allow-unconfigured --bind lan --port "${PORT:-18789}" --verbose
