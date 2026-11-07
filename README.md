<p align="center"><img src=".github/assets/readme-header.svg" alt="Creator Agent Toolbox — Reviewable scripts, thumbnails &amp; content experiments" width="100%" /></p>

# Creator Agent Toolbox

Creator Agent Toolbox models a content-production workflow with explicit human review steps. A FastAPI backend and LangGraph orchestration prepare script variants, pause for approval, generate thumbnail options, and expose an experiment dashboard. The React frontend presents workflow state and selections. Provider configuration determines whether generation uses a local model, an external API, or mocks. The repository includes a mock analytics implementation, so simulated experiment outcomes must not be presented as measured YouTube performance.

[![Stars](https://img.shields.io/github/stars/ak1458/creator-agent-toolbox?style=flat-square)](https://github.com/ak1458/creator-agent-toolbox/stargazers)
[![Watching](https://img.shields.io/github/watchers/ak1458/creator-agent-toolbox?style=flat-square&label=watching)](https://github.com/ak1458/creator-agent-toolbox/watchers)
[![Forks](https://img.shields.io/github/forks/ak1458/creator-agent-toolbox?style=flat-square)](https://github.com/ak1458/creator-agent-toolbox/forks)
[![Activity](https://img.shields.io/github/last-commit/ak1458/creator-agent-toolbox?style=flat-square)](https://github.com/ak1458/creator-agent-toolbox/activity)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-64748b?style=flat-square)](LICENSE)

**[How it works](#how-it-works) · [Run locally](#run-locally) · [Configuration](#configuration) · [Commands](#development-commands) · [Versions](#versions-and-distribution) · [License](#license)**

## How it works

1. Create a content workflow from the dashboard or workflow API.
2. Review script variants and explicitly approve or reject the selection.
3. Review thumbnail variants and choose the permitted next step.
4. Inspect experiment metrics and completion/export state, distinguishing mock analytics from actual platform data.

## Architecture

| Path | Purpose |
| --- | --- |
| [backend/app/agents/](<backend/app/agents/>) | Trend, script, visual, and A/B orchestration agents. |
| [backend/app/api/](<backend/app/api/>) | Workflow and supporting endpoints. |
| [backend/app/core/config.py](<backend/app/core/config.py>) | Provider, origins, secrets, and persistence settings. |
| [backend/app/services/](<backend/app/services/>) | Analytics, statistics, cache, and external-service adapters. |
| [frontend/src/](<frontend/src/>) | Dashboard, review, and experiment interfaces. |
| [archives/](<archives/>) | Historical generator attempts, not the active application root. |

## What is here

- FastAPI endpoints and LangGraph-based workflow orchestration.
- Script variants followed by explicit review and approval steps.
- Thumbnail selection and experiment-monitoring screens.
- SQLite persistence with configurable generation providers.

## Run locally

Backend:

```bash
cd backend
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

Frontend, in another terminal from the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Review [backend configuration](backend/app/core/config.py) for provider, database, secret, and origin settings. Configuration is environment-specific; paid providers need credentials.

## Current limits

The repository includes a mock analytics provider for A/B demonstrations. Simulated CTR or confidence values do not demonstrate live YouTube performance. Review [the handoff](HANDOFF.md) and [beta checklist](BETA_CHECKLIST.md) before connecting external services or claiming production readiness.

The active application is in `backend/` and `frontend/`; historical generator attempts and run logs should be reviewed in a separate source-cleanup pass.


## Configuration

Settings template: [backend/.env.example](<backend/.env.example>). Copy it to the application’s local environment file and fill only the integrations you use.

| Variable | Purpose |
| --- | --- |
| `LLM_PROVIDER` | Provider selection used by the corresponding integration. |
| `OLLAMA_BASE_URL` | Endpoint for the corresponding integration; verify the expected service and environment. |
| `OLLAMA_SCRIPT_MODEL` | Model identifier used by the selected provider integration. |
| `OLLAMA_TIMEOUT_SECONDS` | Optional configuration; see the linked template and its consuming module for accepted values. |
| `OPENAI_API_KEY` | Provider credential. Keep server-side; public-prefixed legacy options must not contain production secrets. |
| `PERPLEXITY_API_KEY` | Provider credential. Keep server-side; public-prefixed legacy options must not contain production secrets. |
| `YOUTUBE_API_KEY` | Provider credential. Keep server-side; public-prefixed legacy options must not contain production secrets. |
| `PEXELS_API_KEY` | Provider credential. Keep server-side; public-prefixed legacy options must not contain production secrets. |
| `POLLINATIONS_BASE_URL` | Endpoint for the corresponding integration; verify the expected service and environment. |
| `THUMBNAIL_WIDTH` | Optional configuration; see the linked template and its consuming module for accepted values. |
| `THUMBNAIL_HEIGHT` | Optional configuration; see the linked template and its consuming module for accepted values. |
| `DATABASE_URL` | Database connection used by the server or ORM. |
| `CHECKPOINT_DB_URL` | Workflow checkpoint database location. |
| `REDIS_URL` | Endpoint for the corresponding integration; verify the expected service and environment. |
| `ENABLE_CACHE` | Optional cache/service configuration. |
| `CACHE_TTL_SECONDS` | Optional cache/service configuration. |
| `SECRET_KEY` | Backend secret; replace development placeholders before connected use. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Optional configuration; see the linked template and its consuming module for accepted values. |
| `DEBUG` | Optional configuration; see the linked template and its consuming module for accepted values. |
| `ENVIRONMENT` | Optional configuration; see the linked template and its consuming module for accepted values. |

Settings template: [frontend/.env.example](<frontend/.env.example>). Copy it to the application’s local environment file and fill only the integrations you use.

| Variable | Purpose |
| --- | --- |
| `VITE_API_BASE_URL` | Frontend URL for the backend API. |

Environment files and provider tokens must remain untracked. A public client prefix exposes a value in the browser bundle; it is not a safe place for privileged credentials.

## Development commands

Workspace: [frontend/package.json](<frontend/package.json>). Run these commands from its directory.

| Command | Script defined in manifest |
| --- | --- |
| `npm run dev` | `vite` |
| `npm run build` | `tsc -b && vite build` |
| `npm run lint` | `eslint .` |
| `npm run preview` | `vite preview` |

These are available commands, not a claim that all checks passed in this documentation pass. Connected checks require the services, credentials, and isolated data described above.

## Operational notes

Use backend/ and frontend/ as the active applications. The repeated generator-attempt trees are historical material and should not be installed instead of the active workspaces. SQLite and checkpoint persistence need writable local paths. Configure the selected LLM provider deliberately: a mock or fallback response can keep a demo moving but does not verify the external API. Keep real production secrets, nonlocal origins, and Redis/database configuration environment-specific.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Workflow status does not update | Check backend availability, the frontend API base URL, and polling/error output. |
| Generated content looks synthetic or identical | Check the selected provider and fallback path; mock generation is supported. |
| The A/B winner appears without real channel traffic | The repository includes mock analytics. Review the provider implementation before describing results as live measurements. |

## Versions and distribution

Manifest versions are application/workspace metadata, not a certification of release readiness.

| Manifest | Declared version |
| --- | --- |
| [frontend/package.json](<frontend/package.json>) | `0.0.0` |

No published GitHub Release or version tag was recorded in this snapshot. The default branch is a development/source snapshot; it must not be described as a stable downloadable release merely to populate the sidebar.

GitHub Packages is a separate registry. This README does not imply that a registry package exists; use the installation path documented here rather than an invented package-install command.

## Documentation and maintenance

- [HANDOFF.md](<HANDOFF.md>)
- [BETA_CHECKLIST.md](<BETA_CHECKLIST.md>)
- [backend/README.md](<backend/README.md>)
- [DEPLOY.md](<DEPLOY.md>)

For change proposals, see [CONTRIBUTING.md](CONTRIBUTING.md). Include the affected workflow, reproduction steps, and relevant check output when reporting a problem. Do not include credentials or live customer data.

## License

This repository’s project code is **proprietary / all rights reserved**. Public visibility does not grant unrestricted reuse. Read [LICENSE](<LICENSE>) for the exact terms. Third-party dependencies and bundled components retain their own notices.
