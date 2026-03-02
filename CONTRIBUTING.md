# Contributing to ShipStack

Welcome to ShipStack! 🚀

## Quick Links

- **GitHub:** https://github.com/shipstack/shipstack
- **Vision:** [`VISION.md`](VISION.md)
- **Discord:** https://discord.gg/shipstack
- **X/Twitter:** [@shipstack](https://x.com/shipstack)

## How to Contribute

1. **Bugs & small fixes** → Open a PR!
2. **New features / architecture** → Start a [GitHub Discussion](https://github.com/shipstack/shipstack/discussions) or ask in Discord first
3. **Questions** → Discord [#help](https://discord.gg/shipstack) / [#users-helping-users](https://discord.gg/shipstack)

## Before You PR

- Test locally with your ShipStack instance
- Run tests: `pnpm build && pnpm check && pnpm test`
- Ensure CI checks pass
- Keep PRs focused (one thing per PR; do not mix unrelated concerns)
- Describe what & why

## Control UI Decorators

The Control UI uses Lit with **legacy** decorators (current Rollup parsing does not support
`accessor` fields required for standard decorators). When adding reactive fields, keep the
legacy style:

```ts
@state() foo = "bar";
@property({ type: Number }) count = 0;
```

The root `tsconfig.json` is configured for legacy decorators (`experimentalDecorators: true`)
with `useDefineForClassFields: false`. Avoid flipping these unless you are also updating the UI
build tooling to support standard decorators.

## AI/Vibe-Coded PRs Welcome! 🤖

Built with Codex, Claude, or other AI tools? **Awesome - just mark it!**

Please include in your PR:

- [ ] Mark as AI-assisted in the PR title or description
- [ ] Note the degree of testing (untested / lightly tested / fully tested)
- [ ] Include prompts or session logs if possible (super helpful!)
- [ ] Confirm you understand what the code does

AI PRs are first-class citizens here. We just want transparency so reviewers know what to look for.

## Current Focus & Roadmap 🗺

We are currently prioritizing:

- **Stability**: Fixing edge cases in channel connections (WhatsApp/Telegram).
- **UX**: Improving the onboarding wizard and error messages.
- **Skills**: For skill contributions, head to [ShipHub](https://shiphub.com/) — the community hub for ShipStack skills.
- **Performance**: Optimizing token usage and compaction logic.

Check the [GitHub Issues](https://github.com/shipstack/shipstack/issues) for "good first issue" labels!

## Becoming a Maintainer

We're selectively expanding the maintainer team.
If you're an experienced contributor who wants to help shape ShipStack's direction — whether through code, docs, or community — we'd like to hear from you.

Being a maintainer is a responsibility, not an honorary title. We expect active, consistent involvement — triaging issues, reviewing PRs, and helping move the project forward.

Still interested? Email contributing@shipstack.ai with:

- Links to your PRs on ShipStack (if you don't have any, start there first)
- Links to open source projects you maintain or actively contribute to
- Your GitHub, Discord, and X/Twitter handles
- A brief intro: background, experience, and areas of interest
- Languages you speak and where you're based
- How much time you can realistically commit

We welcome people across all skill sets — engineering, documentation, community management, and more.
We review every human-only-written application carefully and add maintainers slowly and deliberately.
Please allow a few weeks for a response.

## Report a Vulnerability

We take security reports seriously. Report vulnerabilities directly to the repository where the issue lives:

- **Core CLI and gateway** — [shipstack/shipstack](https://github.com/shipstack/shipstack)
- **macOS desktop app** — [shipstack/shipstack](https://github.com/shipstack/shipstack) (apps/macos)
- **iOS app** — [shipstack/shipstack](https://github.com/shipstack/shipstack) (apps/ios)
- **Android app** — [shipstack/shipstack](https://github.com/shipstack/shipstack) (apps/android)
- **ShipHub** — [shipstack/shiphub](https://github.com/shipstack/shiphub)

For issues that don't fit a specific repo, or if you're unsure, email **security@shipstack.ai** and we'll route it.

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

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@shipstack.ai.

## License

By contributing to ShipStack, you agree that your contributions will be licensed under the MIT License.
