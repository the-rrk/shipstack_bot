# Security Policy

If you believe you've found a security issue in ShipStack, please report it privately.

## Reporting

Report vulnerabilities directly to the repository where the issue lives:

- **Core CLI and gateway** — [shipstack/shipstack](https://github.com/shipstack/shipstack)
- **macOS desktop app** — [shipstack/shipstack](https://github.com/shipstack/shipstack) (apps/macos)
- **iOS app** — [shipstack/shipstack](https://github.com/shipstack/shipstack) (apps/ios)
- **Android app** — [shipstack/shipstack](https://github.com/shipstack/shipstack) (apps/android)
- **ShipHub** — [shipstack/shiphub](https://github.com/shipstack/shiphub)

For issues that don't fit a specific repo, or if you're unsure, email **[security@shipstack.ai](mailto:security@shipstack.ai)** and we'll route it.

For full reporting instructions see our [Trust page](https://trust.shipstack.ai).

### Required in Reports

1. **Title**
2. **Severity Assessment**
3. **Impact**
4. **Affected Component**
5. **Technical Reproduction**
6. **Demonstrated Impact**
7. **Environment**
8. **Remediation Advice**

Reports without reproduction steps, demonstrated impact, and remediation advice will be deprioritized. Given the volume of AI-generated scanner findings, we must ensure we're receiving vetted reports from researchers who understand the issues.

### Report Acceptance Gate (Triage Fast Path)

For fastest triage, include all of the following:

- Exact vulnerable path (`file`, function, and line range) on a current revision.
- Tested version details (ShipStack version and/or commit SHA).
- Reproducible PoC against latest `main` or latest released version.
- Demonstrated impact tied to ShipStack's documented trust boundaries.
- For exposed-secret reports: proof the credential is ShipStack-owned (or grants access to ShipStack-operated infrastructure/services).
- Explicit statement that the report does not rely on adversarial operators sharing one gateway host/config.
- Scope check explaining why the report is **not** covered by the Out of Scope section below.
- For command-risk/parity reports (for example obfuscation detection differences), a concrete boundary-bypass path is required (auth/approval/allowlist/sandbox). Parity-only findings are treated as hardening, not vulnerabilities.

Reports that miss these requirements may be closed as `invalid` or `no-action`.

### Common False-Positive Patterns

These are frequently reported but are typically closed with no code change:

- Prompt-injection-only chains without a boundary bypass (prompt injection is out of scope).
- Operator-intended local features (for example TUI local `!` shell) presented as remote injection.
- Authorized user-triggered local actions presented as privilege escalation.
- Reports that only show a malicious plugin executing privileged actions after a trusted operator installs/enables it.
- Reports that assume per-user multi-tenant authorization on a shared gateway host/config.
- Reports that only show differences in heuristic detection/parity without demonstrating bypass of auth, approvals, allowlist enforcement, sandboxing, or other documented trust boundaries.
- ReDoS/DoS claims that require trusted operator configuration input without a trust-boundary bypass.
- Missing HSTS findings on default local/loopback deployments.
- Scanner-only claims against stale/nonexistent paths, or claims without a working repro.

### Duplicate Report Handling

- Search existing advisories before filing.
- Include likely duplicate GHSA IDs in your report when applicable.
- Maintainers may close lower-quality/later duplicates in favor of the earliest high-quality canonical report.

## Bug Bounties

ShipStack is an open source project. There is no bug bounty program and no budget for paid reports. Please still disclose responsibly so we can fix issues quickly.
The best way to help the project right now is by sending PRs.

## Operator Trust Model (Important)

ShipStack does **not** model one gateway as a multi-tenant, adversarial user boundary.

- Authenticated Gateway callers are treated as trusted operators for that gateway instance.
- Session identifiers (`sessionKey`, session IDs, labels) are routing controls, not per-user authorization boundaries.
- If one operator can view data from another operator on the same gateway, that is expected in this trust model.
- Recommended mode: one user per machine/host (or VPS), one gateway for that user, and one or more agents inside that gateway.
- If multiple users need ShipStack, use one VPS (or host/OS user boundary) per user.
- Exec behavior is host-first by default: `agents.defaults.sandbox.mode` defaults to `off`.

## Trusted Plugin Concept (Core)

Plugins/extensions are part of ShipStack's trusted computing base for a gateway.

- Installing or enabling a plugin grants it the same trust level as local code running on that gateway host.
- Plugin behavior such as reading env/files or running host commands is expected inside this trust boundary.
- Security reports must show a boundary bypass (for example unauthenticated plugin load, allowlist/policy bypass, or sandbox/path-safety bypass), not only malicious behavior from a trusted-installed plugin.

## Out of Scope

- Public Internet Exposure
- Using ShipStack in ways that the docs recommend not to
- Deployments where mutually untrusted/adversarial operators share one gateway host and config
- Prompt-injection-only attacks (without a policy/auth/sandbox boundary bypass)
- Reports that require write access to trusted local state (`~/.shipstack`, workspace files)
- Reports where the only demonstrated impact is an already-authorized sender intentionally invoking a local-action command without bypassing auth, sandbox, or another documented boundary
- Reports where the only claim is that a trusted-installed/enabled plugin can execute with gateway/host privileges (documented trust model behavior)
- Any report whose only claim is that an operator-enabled `dangerous*`/`dangerously*` config option weakens defaults
- Reports that depend on trusted operator-supplied configuration values to trigger availability impact
- Reports whose only claim is heuristic/parity drift in command-risk detection across exec surfaces, without a demonstrated trust-boundary bypass
- Exposed secrets that are third-party/user-controlled credentials without demonstrated ShipStack impact
- Reports whose only claim is host-side exec when sandbox runtime is disabled/unavailable, without a boundary bypass

## Deployment Assumptions

ShipStack security guidance assumes:

- The host where ShipStack runs is within a trusted OS/admin boundary.
- Anyone who can modify `~/.shipstack` state/config (including `shipstack.json`) is effectively a trusted operator.
- A single Gateway shared by mutually untrusted people is **not a recommended setup**. Use separate gateways (or at minimum separate OS users/hosts) per trust boundary.
- Authenticated Gateway callers are treated as trusted operators.

## One-User Trust Model (Personal Assistant)

ShipStack's security model is "personal assistant" (one trusted operator, potentially many agents), not "shared multi-tenant bus."

- If multiple people can message the same tool-enabled agent, they can all steer that agent within its granted permissions.
- Session or memory scoping reduces context bleed, but does **not** create per-user host authorization boundaries.
- For mixed-trust or adversarial users, isolate by OS user/host/gateway and use separate credentials per boundary.

## Agent and Model Assumptions

- The model/agent is **not** a trusted principal. Assume prompt/content injection can manipulate behavior.
- Security boundaries come from host/config trust, auth, tool policy, sandboxing, and exec approvals.
- Prompt injection by itself is not a vulnerability report unless it crosses one of those boundaries.

## Operational Guidance

For threat model + hardening guidance, see:

- `https://docs.shipstack.ai/gateway/security`

### Tool filesystem hardening

- `tools.exec.applyPatch.workspaceOnly: true` (recommended): keeps `apply_patch` writes/deletes within the configured workspace directory.
- `tools.fs.workspaceOnly: true` (optional): restricts `read`/`write`/`edit`/`apply_patch` paths and native prompt image auto-load paths to the workspace directory.

### Web Interface Safety

ShipStack's web interface (Gateway Control UI + HTTP endpoints) is intended for **local use only**.

- Recommended: keep the Gateway **loopback-only** (`127.0.0.1` / `::1`).
  - Config: `gateway.bind="loopback"` (default).
  - CLI: `shipstack gateway run --bind loopback`.
- Do **not** expose it to the public internet. It is not hardened for public exposure.
- If you need remote access, prefer an SSH tunnel or Tailscale serve/funnel (so the Gateway still binds to loopback), plus strong Gateway auth.

## Runtime Requirements

### Node.js Version

ShipStack requires **Node.js 22.12.0 or later** (LTS). This version includes important security patches.

Verify your Node.js version:

```bash
node --version  # Should be v22.12.0 or later
```

### Docker Security

When running ShipStack in Docker:

1. The official image runs as a non-root user (`node`) for reduced attack surface
2. Use `--read-only` flag when possible for additional filesystem protection
3. Limit container capabilities with `--cap-drop=ALL`

Example secure Docker run:

```bash
docker run --read-only --cap-drop=ALL \
  -v shipstack-data:/app/data \
  shipstack/shipstack:latest
```

## Security Scanning

This project uses `detect-secrets` for automated secret detection in CI/CD.
See `.detect-secrets.cfg` for configuration and `.secrets.baseline` for the baseline.

Run locally:

```bash
pip install detect-secrets==1.5.0
detect-secrets scan --baseline .secrets.baseline
