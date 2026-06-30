# FoodSupply IQ — Build Progress

Living checklist of the epic → story backlog. Update as stories land so any
session can resume from here. See the architecture/backlog brief for full ACs,
`docs/erd.md` for the data model, and `docs/deploy.md` for deployment.

## Deployment
- **Live on Railway**: api `https://api-production-19cc.up.railway.app`,
  web `https://web-production-a328bf.up.railway.app`, plus PostGIS + Redis.
- Push to `main` auto-deploys api + web. Mobile ships via Expo EAS (not Railway).
- Demo login: `manager@foodsupplyiq.com` / `password123` (run `python -m app.seed` on a fresh DB).

## Epic 0 — Foundation & Platform ✅ COMPLETE
- [x] 0.1 Monorepo & environment scaffolding
- [x] 0.2 Database schema & migrations (PostGIS, core entities, ERD)
- [x] 0.3 Auth & role-based access (JWT + refresh, argon2, manager/rep)
- [x] 0.4 Shared API contract (`@fsiq/api-types`) + design system
- [x] 0.5 Railway deploy + EAS config + runbook

## Epic 1 — Accounts & Contacts  ✅ COMPLETE
- [x] 1.1 Add & categorize accounts — backend CRUD + geocoding + filters
      (`app/routers/accounts.py`, `app/schemas/account.py`, `app/services/geocoding.py`,
      `app/utils/geo.py`; rep-scoped; 15 tests; types in `@fsiq/api-types`)
- [x] 1.1 Accounts UI (web): form + table
      (`/accounts` page: filters by category/status/search, create+edit form,
      delete; `lib/use-accounts.ts` TanStack Query hooks; `RequireAuth` guard;
      dashboard links to it)
- [x] 1.2 Account profile, history & status
      (`GET /accounts/{id}/profile` → account + contacts + recent visits + counts;
      web `/accounts/[id]` overview/history/contacts tabs; mobile accounts list +
      read-only profile screen w/ tap-to-call. Offline caching deferred to Epic 7.)
- [x] 1.3 Attach contacts — CRUD scoped to account (`routers/contacts.py`,
      manager-only writes, single-primary enforcement); web inline ContactsEditor
      on the profile contacts tab; mobile contact list + tap-to-call (from 1.2)
- [x] 1.4 Account pipeline status transitions — `POST /accounts/{id}/status`
      (validated transitions via `utils/transitions.py`, `account_status_history`
      table records actor+timestamp+note, updates last_verified_at) +
      `GET /accounts/{id}/status-history`; web StatusControl on profile; mobile
      status chips. Offline-queued change deferred to Epic 7.

## Epic 2 — Product Catalog  ✅ COMPLETE
- [x] 2.1 Maintain product catalog — backend CRUD (`routers/products.py`,
      manager-only writes, soft-delete via is_active, currency, search +
      include_inactive); web `/products` catalog (table + form + deactivate/
      reactivate). Mobile cached product picker deferred to Epic 4 (where the
      sample/order flows consume it).

## Epic 3 — Field Visits  ✅ COMPLETE
- [x] 3.1 Check-in + log visit (mvp) — `routers/visits.py` (POST/list/detail,
      rep-scoped, geo+outcome+notes); mobile check-in with expo-location GPS +
      outcome chips + notes on the profile; web shows visits in profile history.
- [x] 3.2 Live activity feed (mvp) — `routers/activity.py` (unions visits/
      samples/orders, newest-first, rep filter + before cursor, manager-only);
      `routers/users.py` (rep list); web ActivityFeed on the manager dashboard
      with rep filter + 15s auto-refresh.
- [x] 3.3 Visit photos — MinIO (docker) / R2 (prod) S3 storage; `services/storage.py`
      presigned PUT/GET; `visit_media` table; presign/attach/list/delete endpoints;
      mobile capture (expo-image-picker, compress, upload); web thumbnail gallery
      on visit history. Prod needs an R2/MinIO bucket + creds (config only).

## Epic 4 — Samples & Orders (core loop)  ✅ COMPLETE
- [x] 4.1 Record sample — `routers/samples.py` (POST/list, product[]+qty, rep-scoped,
      validates products); mobile SampleForm with cached product picker
      (`src/products.ts` session cache); samples surface in web activity feed +
      profile sample count. 3 tests.
- [x] 4.2 Trial order — `routers/orders.py` (POST/list, computes total from
      catalog prices w/ unit-price snapshot, optional sample link, rep-scoped);
      mobile OrderForm (trial) with live total; orders in activity feed + counts.
- [x] 4.3 Repeat orders + metrics — account `is_repeating` (≥2 orders) +
      `repeat_order_count` + `last_order_at` (migration w/ server_default);
      recomputed on order create + nightly arq cron (`recompute_repeat_metrics`);
      web "Repeating" badge on account list + profile; mobile "+ Repeat order".
- [x] 4.4 Sample→Trial→Repeat funnel — `routers/funnel.py` (GET /funnel counts +
      conversion %, GET /funnel/accounts drill-down, filters rep/date/product,
      manager-only); web /funnel page (stage bars + filters + drill-down list).
      Tremol viz deferred — custom bars used (Tremor can come in Epic 6).

## Epic 5 — Map & Territory  ✅ (web + backend; mobile native map deferred)
- [x] 5.1 Accounts on map — `GET /geo/accounts/nearby` (ST_DWithin, rep-scoped);
      web `/map` (MapLibre GL, OSM tiles, no token): status-colored markers +
      client clustering + popups linking to profiles.
- [x] 5.2 Manager clusters/coverage — `GET /geo/accounts/clusters` (grid rollup);
      web area summary panel (status counts + cluster count).
- [ ] Mobile native map (Mapbox RN) deferred — needs a custom Expo dev build
      (ties into Epic 7); backend nearby endpoint is ready for it.

## Epic 6 — Dashboard & KPIs  ⬜
- [ ] 6.1 Manager KPI dashboard vs target

## Epic 7 — Rep Mobile (offline-first)  ⬜
- [ ] 7.1 Today's schedule · [ ] 7.2 Offline logging + sync

## Later (p2+)
- Epic 8 Intelligence · Epic 9 Supply Chain · Epic 10 Advanced · Epic 11 Market Intelligence

---
**MVP cut line:** Epics 0–7 (minus 3.3 photos). Currently on **Epic 1**.
