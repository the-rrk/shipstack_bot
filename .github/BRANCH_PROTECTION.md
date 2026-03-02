# Branch Protection Setup Guide

This document explains how to set up branch protection rules for the ShipStack repository to ensure only the owner has write access to the main branch.

## Setting Up Branch Protection (GitHub Web UI)

1. Go to your repository: https://github.com/albinjoseph03/shipstack_bot
2. Click **Settings** → **Branches**
3. Under "Branch protection rules", click **Add rule**
4. Configure the following:

### Branch name pattern
```
main
```

### Protection Settings

#### ✅ Require a pull request before merging
- ✅ Require approvals: **1**
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners
- ✅ Require approval of the most recent reviewable push

#### ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- Add these required status checks:
  - `Lint`
  - `Type Check`
  - `Test`

#### ✅ Require conversation resolution before merging

#### ✅ Require signed commits (optional but recommended)

#### ✅ Require linear history
- This prevents merge commits and keeps history clean

#### ✅ Do not allow bypassing the above settings
- **Important**: Uncheck this if you (the owner) need to push directly in emergencies

#### ❌ Allow force pushes
- Keep this **disabled** for safety

#### ❌ Allow deletions
- Keep this **disabled** to prevent accidental branch deletion

## Additional Security Settings

### Repository Settings → General

1. **Default branch**: Set to `main`
2. **Features**:
   - ✅ Issues
   - ✅ Discussions (for community Q&A)
   - ✅ Projects (optional)

### Repository Settings → Actions → General

1. **Actions permissions**: Allow all actions and reusable workflows
2. **Workflow permissions**: Read and write permissions
3. **Allow GitHub Actions to create and approve pull requests**: ✅ Enable

### Repository Settings → Code security and analysis

1. ✅ Dependency graph
2. ✅ Dependabot alerts
3. ✅ Dependabot security updates
4. ✅ Secret scanning
5. ✅ Push protection

## How It Works

With these settings:

1. **Contributors** can:
   - Fork the repository
   - Create branches in their fork
   - Submit Pull Requests to `main`
   - Comment on issues and PRs

2. **Only you (owner)** can:
   - Approve and merge PRs to `main`
   - Push directly to `main` (if bypass is enabled)
   - Modify branch protection rules
   - Manage repository settings

3. **Automated checks** will:
   - Run CI on every PR
   - Block merging if tests fail
   - Require your approval before merge

## Quick Setup via GitHub CLI (Optional)

If you have GitHub CLI installed, you can run:

```bash
gh api repos/albinjoseph03/shipstack_bot/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Lint","Type Check","Test"]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
  --field restrictions=null \
  --field required_linear_history=true \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

## Workflow Summary

```
Contributor                    You (Owner)
    │                              │
    ├─► Fork repo                  │
    ├─► Create branch              │
    ├─► Make changes               │
    ├─► Submit PR ─────────────────┼─► Review PR
    │                              ├─► CI runs automatically
    │                              ├─► Approve if good
    │                              └─► Merge to main
    │                              │
    └─► PR merged! 🎉              │
