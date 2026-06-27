# FoodSupply IQ — Distribution Intelligence

Offline-first field-sales + distribution intelligence for African food distribution
(sister product to AFDP & the DMV African Market Intelligence System).

This is a monorepo with three apps that share one Postgres+PostGIS database and a
Redis-backed job queue.

```
api/      FastAPI + SQLAlchemy + Alembic   (REST API, auth, geo, scoring)
web/      Next.js 14 + shadcn/ui + Tremor  (manager dashboard)
mobile/   Expo / React Native              (field rep app, offline-first)
```

See the product/architecture brief for the full epic → story backlog. Current
status: **Story 0.1 — Monorepo & environment scaffolding** is complete.

---

## Prerequisites

- **Docker Desktop** — local Postgres+PostGIS and Redis
- **Python 3.12+** — the API
- **Node 20+** and **pnpm 9+** — web + mobile (`npm i -g pnpm`)
- (mobile only) the **Expo Go** app on a phone, or an Android/iOS emulator

> **Ports:** local infra runs on **5440** (Postgres) and **6380** (Redis) to avoid
> clashing with a native Windows PostgreSQL (5432) and the sister AFDP project's
> Redis (6379). Override via `DATABASE_URL` / `REDIS_URL` if you don't need that.

---

## 1. Start local infrastructure

```bash
pnpm infra:up        # docker compose up -d  (Postgres+PostGIS + Redis)
```

Uses the `postgis/postgis:17-3.5` image — the same PostGIS template you deploy on
Railway. The plain `postgres` image does **not** ship the `postgis` extension.

## 2. API (FastAPI)

```bash
cd api
python -m venv .venv
# Windows:  .venv\Scripts\activate     macOS/Linux:  source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head                   # enables PostGIS + future migrations
uvicorn app.main:app --reload          # http://localhost:8000
```

- Health: <http://localhost:8000/health> · DB/PostGIS: <http://localhost:8000/health/db>
- API docs: <http://localhost:8000/docs>
- Background worker (arq): `arq app.worker.WorkerSettings`
- Tests: `pytest` · Lint: `ruff check .`

## 3. Web dashboard (Next.js)

```bash
pnpm install                           # run once at repo root (covers web + mobile)
cp web/.env.example web/.env.local
pnpm web                               # http://localhost:3000
```

## 4. Mobile app (Expo)

```bash
cp mobile/.env.example mobile/.env
pnpm mobile                            # opens Expo dev tools; scan QR with Expo Go
```

> Android emulator can't reach `localhost` — set `EXPO_PUBLIC_API_URL=http://10.0.2.2:8000`
> (emulator) or your machine's LAN IP (physical device).

---

## Repo layout & tooling

| Path                 | What                                                            |
| -------------------- | -------------------------------------------------------------- |
| `docker-compose.yml` | Local Postgres+PostGIS + Redis                                 |
| `api/`               | FastAPI app, Alembic migrations (`api/alembic/`), arq worker   |
| `web/`               | Next.js App Router, Tailwind + shadcn tokens, TanStack Query   |
| `mobile/`            | Expo / React Native app                                        |
| `packages/api-types/`| Typed API contract generated from OpenAPI (`@fsiq/api-types`)  |
| `docs/`              | `erd.md` (data model), `design-system.md` (tokens/components)  |
| `.pre-commit-config.yaml` | ruff (api) + prettier (web/mobile) — `pre-commit install` |

Code style: **ruff** for Python, **eslint + prettier** for TS/JS.

### API contract & typed clients

The FastAPI app publishes OpenAPI at `/openapi.json` (Swagger UI at `/docs`).
Web and mobile share generated types from `packages/api-types` — never hand-write
request/response shapes. Regenerate after any API change (needs the api venv +
Node):

```bash
pnpm gen:api    # export openapi.json from FastAPI, then run openapi-typescript
```
