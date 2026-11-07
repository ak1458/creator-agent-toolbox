# Creator Agent Toolbox

A content workflow application with script review, thumbnail selection, and an A/B-testing dashboard.

[![Python: Backend](https://img.shields.io/badge/Python-Backend-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![FastAPI: API](https://img.shields.io/badge/FastAPI-API-009688?style=flat-square&logo=fastapi&logoColor=white)](backend/app/main.py)
[![React: UI](https://img.shields.io/badge/React-UI-149ECA?style=flat-square&logo=react&logoColor=white)](https://react.dev)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-64748B?style=flat-square)](LICENSE)

[Handoff](HANDOFF.md) · [Beta checklist](BETA_CHECKLIST.md) · [Deployment](DEPLOY.md)

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

## License

Copyright © 2026 Ashraf Kamal. Reuse is restricted by [LICENSE](LICENSE).
