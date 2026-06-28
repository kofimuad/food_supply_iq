# FoodSupply IQ — Deployment (Story 0.5)

Everything in the repo is wired for deploy. What's **already done in code**:

- `api/Dockerfile` + `api/railway.json` — API image; Alembic runs as the
  `preDeployCommand` on every deploy; healthcheck on `/health`.
- `web/Dockerfile` + `web/railway.json` — Next.js standalone image (monorepo-aware).
- `mobile/eas.json` — EAS build profiles (development / preview / production).
- The API normalizes `postgresql://` → `postgresql+asyncpg://`, so Railway's
  managed DB URL works without editing.

What **you** still have to do lives in Railway's dashboard and your Expo account —
the checklist below.

---

## ✅ Your checklist

### Railway (one project, Hobby plan — templates don't deploy on the free trial)

- [ ] Create a Railway account and a new **project**; upgrade to the **Hobby plan**.
- [ ] Connect the GitHub repo `kofimuad/food_supply_iq` to Railway.
- [ ] **Database:** add the **PostGIS template** (`postgis/postgis:17-3.5`) from the
      Railway marketplace — *not* the default Postgres. Attach a **Volume** to it.
- [ ] **Redis:** add a Redis service (marketplace) to the same project.
- [ ] **API service:** new service from the GitHub repo →
      Settings → **Root Directory = `/api`** (it auto-detects `api/railway.json`).
- [ ] **Web service:** new service from the same repo →
      Settings → **Root Directory = `/`** and **Config-as-code path = `web/railway.json`**
      (the web image must build from the repo root to see the pnpm workspace).
- [ ] (Optional, needed for background jobs in Epic 4+) **Worker service:** another
      service, Root Directory = `/api`, **Custom Start Command = `arq app.worker.WorkerSettings`**,
      and turn its healthcheck **off**.
- [ ] Set the environment variables below on each service.
- [ ] Generate a JWT secret: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
- [ ] Push to `main` → Railway auto-builds + deploys. Confirm:
      `https://<api-domain>/health`, `/health/db`, `/docs`, and the web `/login`.
- [ ] (Optional) seed prod once — see "Seeding production" below.

### Expo / EAS (mobile)

- [ ] Create an Expo account; `npm i -g eas-cli` and `eas login`.
- [ ] From `mobile/`: `eas init` (writes the EAS `projectId` into `app.json`).
- [ ] In `mobile/eas.json`, replace `REPLACE-ME-api.up.railway.app` with the real
      API domain in the `preview` and `production` profiles.
- [ ] Build an internal test build: `eas build --profile preview --platform android`.

---

## Environment variables

### API service (and Worker service, if used)

| Variable        | Value                                                            |
| --------------- | --------------------------------------------------------------- |
| `DATABASE_URL`  | reference the PostGIS service over **private networking**, e.g. `postgresql://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.RAILWAY_PRIVATE_DOMAIN}}:5432/${{Postgres.PGDATABASE}}` (the app rewrites the scheme to asyncpg) |
| `REDIS_URL`     | `redis://${{Redis.RAILWAY_PRIVATE_DOMAIN}}:6379/0`              |
| `JWT_SECRET`    | the generated secret                                            |
| `ENVIRONMENT`   | `production`                                                    |
| `DEBUG`         | `false`                                                         |
| `CORS_ORIGINS`  | `["https://<your-web-domain>"]`                                 |

> Use the **private** domain (`*.railway.internal`) for DB/Redis so traffic stays
> inside the project and there's no egress cost. Don't append `?sslmode=...` — the
> asyncpg driver doesn't accept it (private networking doesn't need it).

### Web service

| Variable                     | Value                          |
| ---------------------------- | ------------------------------ |
| `NEXT_PUBLIC_API_URL`        | `https://<your-api-domain>`    |
| `NEXT_PUBLIC_MAPBOX_TOKEN`   | your Mapbox token (Epic 5)     |

`NEXT_PUBLIC_*` vars are baked at **build time**, so set them before the first web
deploy (or redeploy after changing them).

---

## How the pieces fit

- **Migrations** run automatically: `api/railway.json` sets
  `preDeployCommand: "alembic upgrade head"`, so the schema is migrated before each
  new API version goes live.
- **Auto-deploy**: pushing to `main` triggers Railway to rebuild any service whose
  watched paths changed.
- **Private networking**: API/Worker reach Postgres and Redis via
  `*.railway.internal`; only the API and web expose public domains.

## Seeding production (optional, once)

The seed is idempotent (no-ops if users already exist). From the API service shell
(Railway → service → "Shell"/"Run command") or locally with prod `DATABASE_URL`:

```bash
python -m app.seed
```

> ⚠️ The demo seed creates users with the password `password123`. Only use it for a
> demo environment, and rotate/delete those users before any real use.

## Local Docker parity

Build the images locally exactly as Railway will (requires Docker running):

```bash
docker build -t fsiq-api ./api                      # API (context = api/)
docker build -t fsiq-web -f web/Dockerfile .        # web (context = repo root)
```
