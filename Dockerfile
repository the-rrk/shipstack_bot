FROM node:22-bookworm@sha256:20a424ecd1d2064a44e12fe287bf3dae443aab31dc5e0c0cb6c74bef9c78911c

# Install Bun (required for build scripts)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

RUN corepack enable

WORKDIR /app
RUN chown node:node /app

# Install Python 3 for website_builder skill
USER root
RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  python3 python3-venv python3-pip && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

ARG OPENCLAW_DOCKER_APT_PACKAGES=""
RUN if [ -n "$OPENCLAW_DOCKER_APT_PACKAGES" ]; then \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends $OPENCLAW_DOCKER_APT_PACKAGES && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*; \
  fi

COPY --chown=node:node package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY --chown=node:node ui/package.json ./ui/package.json
COPY --chown=node:node patches ./patches
COPY --chown=node:node scripts ./scripts

USER node
# Reduce OOM risk on low-memory hosts during dependency installation.
# Docker builds on small VMs may otherwise fail with "Killed" (exit 137).
RUN NODE_OPTIONS=--max-old-space-size=2048 pnpm install --frozen-lockfile
# Optionally install Chromium and Xvfb for browser automation.
# Build with: docker build --build-arg OPENCLAW_INSTALL_BROWSER=1 ...
# Adds ~300MB but eliminates the 60-90s Playwright install on every container start.
# Must run after pnpm install so playwright-core is available in node_modules.
USER root
ARG OPENCLAW_INSTALL_BROWSER=""
RUN if [ -n "$OPENCLAW_INSTALL_BROWSER" ]; then \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends xvfb && \
  mkdir -p /home/node/.cache/ms-playwright && \
  PLAYWRIGHT_BROWSERS_PATH=/home/node/.cache/ms-playwright \
  node /app/node_modules/playwright-core/cli.js install --with-deps chromium && \
  chown -R node:node /home/node/.cache/ms-playwright && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*; \
  fi

USER node
COPY --chown=node:node . .
RUN pnpm build
# Force pnpm for UI build (Bun may fail on ARM/Synology architectures)
ENV OPENCLAW_PREFER_PNPM=1
RUN pnpm ui:build

# Expose the CLI binary without requiring npm global writes as non-root.
USER root
RUN ln -sf /app/openclaw.mjs /usr/local/bin/openclaw \
  && chmod 755 /app/openclaw.mjs

# Install Vercel CLI for website_builder deployments
RUN npm install -g vercel

ENV NODE_ENV=production

# Security hardening: Run as non-root user
# The node:22-bookworm image includes a 'node' user (uid 1000)
# This reduces the attack surface by preventing container escape via root privileges
USER node

# Start gateway server with default config.
# Binds to loopback (127.0.0.1) by default for security.
#
# For container platforms requiring external health checks:
#   1. Set OPENCLAW_GATEWAY_TOKEN or OPENCLAW_GATEWAY_PASSWORD env var
#   2. Override CMD: ["node","openclaw.mjs","gateway","--allow-unconfigured","--bind","lan"]
CMD ["node", "openclaw.mjs", "gateway", "--allow-unconfigured"]
# Note: To disable Control UI on public deployments, set the start command to:
#   node openclaw.mjs config set gateway.controlUi.enabled false && node openclaw.mjs gateway --allow-unconfigured --bind lan
