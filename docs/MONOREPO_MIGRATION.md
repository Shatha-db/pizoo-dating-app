# Pizoo Monorepo Migration Documentation

## Overview

This document describes the migration of 5 separate repositories into a single Turborepo monorepo structure.

## Migration Date
November 2, 2025

## Repositories Merged

### Source Repositories
1. **pizoo-dating-app** (Target/Host)
   - Original main application
   - Backend: FastAPI
   - Frontend: React
   - Path: Root of monorepo

2. **pizoo**
   - Additional frontend components
   - Backend utilities
   - Migrated to: `packages/ui/components` and `packages/backend`

3. **create-react-app**
   - Reusable React components
   - Migrated to: `packages/ui/react-components`

4. **shatha-site1**
   - Admin/marketing site
   - Migrated to: `apps/admin`

5. **shatha-site**
   - Static assets and marketing content
   - Migrated to: `apps/web/public/marketing`

## New Monorepo Structure

```
pizoo-monorepo/
├── apps/
│   ├── web/              # Main React frontend (from pizoo-dating-app/frontend)
│   └── admin/            # Admin dashboard (from shatha-site1)
├── packages/
│   ├── backend/          # FastAPI backend (from pizoo-dating-app/backend + pizoo/backend)
│   ├── ui/               # Shared UI components (from pizoo + create-react-app)
│   ├── shared/           # Shared utilities and types
│   └── config/           # Shared ESLint, TypeScript, Prettier configs
├── tools/                # Build tools and scripts
├── docs/                 # Documentation
├── .github/workflows/    # CI/CD pipelines
├── package.json          # Root workspace config
├── pnpm-workspace.yaml   # pnpm workspace definition
├── turbo.json            # Turborepo configuration
├── .nvmrc                # Node version (18)
├── .prettierrc           # Prettier configuration
└── .env.example          # Environment variables template
```

## Migration Mapping

| Source Repository | Source Path | Target Path | Notes |
|-------------------|-------------|-------------|-------|
| pizoo-dating-app | `/backend` | `/packages/backend` | Main FastAPI backend |
| pizoo-dating-app | `/frontend` | `/apps/web` | Main React frontend |
| pizoo | `/frontend/src/components` | `/packages/ui/components` | Shared components |
| pizoo | `/backend/*.py` | `/packages/backend` | Backend utilities (merged) |
| create-react-app | `/src` | `/packages/ui/react-components` | Reusable React components |
| shatha-site1 | `/` | `/apps/admin` | Admin dashboard |
| shatha-site | `/` | `/apps/web/public/marketing` | Static marketing assets |

## Backup Tags Created

All repositories have backup tags for rollback:
- Tag format: `backup/pre-monorepo-20251102-HHMM`
- Created on: November 2, 2025
- Location: In each repository's tag list

To rollback a specific repository:
```bash
git checkout backup/pre-monorepo-20251102-HHMM
```

## Branch Normalization

### Before Migration
- pizoo-dating-app: `conflict_311025_1520` (default)
- pizoo: `main`
- shatha-site1: `main`
- create-react-app: `main`
- shatha-site: `main`

### After Migration
- **All repositories**: `main` (default branch)

## Installation & Setup

### Prerequisites
- Node.js >= 18.18.0
- pnpm >= 8.0.0
- Python >= 3.11
- MongoDB >= 7.0

### Install Dependencies
```bash
# Install Node.js dependencies
pnpm install

# Install Python backend dependencies
cd packages/backend
pip install -r requirements.txt
```

### Environment Configuration
1. Copy environment templates:
```bash
cp .env.example .env
cp apps/web/.env.example apps/web/.env
cp packages/backend/.env.example packages/backend/.env
```

2. Fill in required values:
   - `GITHUB_ACCESS_TOKEN`: GitHub PAT with repo scope
   - `MONGO_URL`: MongoDB connection string
   - `CLOUDINARY_URL`: Cloudinary credentials
   - `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`: LiveKit credentials
   - `SENTRY_DSN_BACKEND`, `SENTRY_DSN`: Sentry DSNs
   - `SECRET_KEY`: JWT secret key

## Development

### Run All Services
```bash
# Start all apps and packages in development mode
pnpm dev
```

### Run Specific App/Package
```bash
# Frontend only
pnpm --filter @pizoo/web dev

# Admin dashboard only
pnpm --filter @pizoo/admin dev

# Backend only
cd packages/backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### Build
```bash
# Build all packages
pnpm build

# Build specific package
pnpm --filter @pizoo/web build
```

### Lint & Format
```bash
# Lint all packages
pnpm lint

# Format all code
pnpm format

# Type check
pnpm typecheck
```

### Test
```bash
# Run all tests
pnpm test

# Backend tests
cd packages/backend
pytest -v
```

## CI/CD Pipeline

### GitHub Actions Workflows

1. **Lint** (`.github/workflows/lint.yml`)
   - Runs on: PRs and pushes to main
   - Checks: ESLint, Ruff, Mypy, Prettier
   - Node matrix: [18]

2. **Build** (`.github/workflows/build.yml`)
   - Runs on: PRs and pushes to main
   - Builds all apps and packages
   - Backend health check with MongoDB
   - Node matrix: [18]

3. **Test** (`.github/workflows/test.yml`)
   - Runs on: PRs and pushes to main
   - Frontend and backend tests
   - Coverage reporting

### Required GitHub Secrets
- `SENTRY_DSN_BACKEND`
- `SENTRY_DSN`
- (Others can be mocked for CI)

## Integration Configuration

### LiveKit
- **Location**: `packages/backend/.env`
- **Required**:
  - `LIVEKIT_URL`: WebSocket URL
  - `LIVEKIT_API_KEY`: API key
  - `LIVEKIT_API_SECRET`: API secret
- **Endpoint**: `/api/livekit/token`
- **Rate Limit**: 30 requests/hour per user
- **Token TTL**: 10 minutes

### Cloudinary
- **Location**: `packages/backend/.env` and `apps/web/.env`
- **Format**: `CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name`
- **Features**:
  - Auto-orientation
  - EXIF stripping
  - WebP preview generation
  - Per-user folder structure

### Sentry
- **Backend DSN**: `SENTRY_DSN_BACKEND`
- **Frontend DSN**: `SENTRY_DSN` (in `apps/web/.env`)
- **Traces Sample Rate**: `0.2` (20%)
- **Environment**: Set via `SENTRY_ENVIRONMENT`

### MongoDB
- **Connection**: `MONGO_URL` or `MONGODB_URI`
- **Database**: `MONGODB_DB_NAME`
- **Health Check**: `/health` endpoint pings database

## Removed Duplicates

### Files Removed
- Duplicate `package.json` files (consolidated to workspace)
- Duplicate ESLint configs (moved to `packages/config`)
- Duplicate TypeScript configs (moved to `packages/config`)
- Redundant `.gitignore` entries (consolidated to root)

### Dependencies Deduplicated
- React & React-DOM (managed at workspace level)
- TypeScript (managed at workspace level)
- ESLint & Prettier (managed at workspace level)

## Known Issues & Limitations

1. **Git History**: Direct file copy was used instead of subtree merge due to complexity. Full git history is preserved in backup tags.

2. **Admin Dashboard**: `apps/admin` needs Next.js setup if it's meant to be a functional dashboard.

3. **Backend Health Check**: MongoDB health endpoint needs to be added to `packages/backend/server.py`.

4. **Integration Tests**: E2E tests need to be set up for cross-package testing.

## Rollback Procedure

If issues arise, rollback using backup tags:

```bash
# 1. Navigate to the affected repository
cd /path/to/repo

# 2. Checkout backup tag
git checkout backup/pre-monorepo-20251102-HHMM

# 3. Create a new branch from backup
git checkout -b rollback-branch

# 4. Push to remote
git push origin rollback-branch

# 5. Create PR to merge rollback
```

## Next Steps

1. **Verify All Integrations**: Test LiveKit, Cloudinary, Sentry, MongoDB
2. **Add Backend Health Endpoint**: Implement `/health` with database ping
3. **Set Up Admin Dashboard**: Complete Next.js setup for apps/admin
4. **E2E Testing**: Set up Playwright or Cypress tests
5. **Documentation**: Update README with monorepo instructions
6. **Release Tag**: Create `v0.1.0-monorepo` after verification

## Support & Contact

- **Repository**: https://github.com/Shatha-db/pizoo-dating-app
- **Issues**: https://github.com/Shatha-db/pizoo-dating-app/issues
- **Email**: support@pizoo.app

## Contributors

- Migration performed by: Emergent AI Agent (e1)
- Date: November 2, 2025
- Version: 0.1.0

---

**Last Updated**: November 2, 2025
