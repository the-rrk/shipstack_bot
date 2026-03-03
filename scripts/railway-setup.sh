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

# 3. Run doctor --fix to onboard Telegram/OpenAI from environment variables
echo "🔹 Running OpenClaw Doctor..."
node openclaw.mjs doctor --fix

echo "✅ Setup complete. Starting Gateway..."

# 4. Start the gateway in the foreground
# Binding to 0.0.0.0 and using the Railway-assigned PORT
exec node openclaw.mjs gateway run --allow-unconfigured --bind 0.0.0.0 --port "${PORT:-18789}" --verbose
