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

## Epic 1 — Accounts & Contacts  🚧 IN PROGRESS
- [x] 1.1 Add & categorize accounts — backend CRUD + geocoding + filters
      (`app/routers/accounts.py`, `app/schemas/account.py`, `app/services/geocoding.py`,
      `app/utils/geo.py`; rep-scoped; 15 tests; types in `@fsiq/api-types`)
- [ ] 1.1 Accounts UI (web): form + table
- [ ] 1.2 Account profile, history & status (endpoint + web page + mobile read-only)
- [ ] 1.3 Attach contacts (CRUD + web editor + mobile tap-to-call)
- [ ] 1.4 Account pipeline status transitions (+ status_history table)

## Epic 2 — Product Catalog  ⬜ NOT STARTED
- [ ] 2.1 Maintain product catalog (CRUD, soft-delete, currency)

## Epic 3 — Field Visits  ⬜
- [ ] 3.1 Check-in + log visit (mvp) · [ ] 3.2 Live activity feed (mvp) · [ ] 3.3 Visit photos (p2)

## Epic 4 — Samples & Orders (core loop)  ⬜
- [ ] 4.1 Record sample · [ ] 4.2 Trial order · [ ] 4.3 Repeat orders · [ ] 4.4 Sample→Trial→Repeat funnel

## Epic 5 — Map & Territory  ⬜
- [ ] 5.1 Rep accounts on map · [ ] 5.2 Manager clusters/coverage

## Epic 6 — Dashboard & KPIs  ⬜
- [ ] 6.1 Manager KPI dashboard vs target

## Epic 7 — Rep Mobile (offline-first)  ⬜
- [ ] 7.1 Today's schedule · [ ] 7.2 Offline logging + sync

## Later (p2+)
- Epic 8 Intelligence · Epic 9 Supply Chain · Epic 10 Advanced · Epic 11 Market Intelligence

---
**MVP cut line:** Epics 0–7 (minus 3.3 photos). Currently on **Epic 1**.
