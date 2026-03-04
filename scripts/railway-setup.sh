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
node openclaw.mjs config set 'channels.telegram.allowFrom ["*"]'
node openclaw.mjs config set channels.telegram.groupPolicy open

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
