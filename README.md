# ClinicOS

Telegram-first clinic AI assistant MVP.

## Current MVP scope

- Telegram patient intake and conversation handling
- Clinic/tenant-scoped patient identity
- AI replies through FreeLLMAPI (OpenAI-compatible endpoint)
- Medical-risk escalation to human staff
- Lead creation and pipeline tracking
- Clinic-scoped knowledge base / FAQ reuse
- Appointment request and confirmation workflow
- Staff/doctor/secretary role handling
- Working-hours aware auto-reply
- Facial analysis with MediaPipe landmarks and safety-sanitized recommendations
- Optional PDF facial report
- Redis-backed provider state when Redis is configured
- Regression tests and GitHub Actions test workflow

## Required environment

- `BOT_TOKEN`
- `OWNER_TELEGRAM_ID`
- `DATABASE_URL`
- `FREELLMAPI_API_KEY`

Recommended:
- `REDIS_URL`
- `FREELLMAPI_BASE_URL`
- `FREELLMAPI_DEFAULT_MODEL`
- `PDF_REPORT_ENABLED`

## Railway

The repository includes a Dockerfile and Procfile. The container starts with:

```
python bot.py
```

Set the required variables in Railway before deployment. On startup the application creates missing tables and initializes the bootstrap clinic/owner for the initial single-clinic deployment.

## Safety / tenancy

Patient identity is resolved through platform aliases and trusted clinic context. Cross-clinic patient lookup, session access, appointment actions, identity merges, and facial analysis persistence are fail-closed.

Facial-analysis LLM output is accepted only as structured JSON and is sanitized before persistence or delivery. Prescriptive quantities are never persisted.

## Verification

Run locally:

```
python -m pytest -q
```

The GitHub workflow at `.github/workflows/tests.yml` runs the same test command for pushes to the main/phase branches and pull requests targeting main.

Runtime tests must be considered unverified until a real CI run or local test execution reports success.
