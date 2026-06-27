# FoodSupply IQ — Design System (locked, Story 0.4)

**Aesthetic:** plain, data-dense, black-on-white. Neutral greys, near-black
primary, generous whitespace, no decorative color. Color is reserved for *data*
(funnel stages, KPI status, map markers) — not chrome.

## Tokens — single source of truth

| Token            | Light value (HSL)   | Hex approx | Use                          |
| ---------------- | ------------------- | ---------- | ---------------------------- |
| `background`     | `0 0% 100%`         | `#ffffff`  | page background              |
| `foreground`     | `0 0% 3.9%`         | `#0a0a0a`  | primary text                 |
| `primary`        | `0 0% 9%`           | `#111111`  | buttons, emphasis            |
| `muted-foreground` | `0 0% 45.1%`      | `#737373`  | secondary text               |
| `border` / `input` | `0 0% 89.8%`      | `#cccccc`  | borders, dividers, fields    |
| `accent`         | `0 0% 96.1%`        | `#f5f5f5`  | hover surfaces               |
| `destructive`    | `0 84% 60%`         | `#c0392b`  | errors, danger               |
| `radius`         | `0.5rem`            | —          | corner rounding              |

- **Web:** defined as CSS variables in `web/app/globals.css` and surfaced to
  Tailwind via `web/tailwind.config.ts` (e.g. `bg-primary`, `text-muted-foreground`).
  A dark theme is defined under `.dark` but the product ships light-first.
- **Mobile:** the same palette lives in `mobile/src/theme.ts` (`colors`,
  `spacing`, `radius`, `fontSize`). Keep the two in sync by hand when tokens change.

## Components

- **Web base components** live in `web/components/ui/` (shadcn/ui *new-york*
  style, configured in `web/components.json`). Shipped so far: `Button`
  (variants: default / outline / ghost / destructive; sizes: sm / default / lg)
  and `Card`. Add more with the shadcn CLI or by hand following the same pattern.
  Compose classes with the `cn()` helper (`web/lib/utils.ts`).
- **Charts/KPIs** (Epic 6): use **Tremor** for KPI cards and the funnel; reach
  for Recharts only when a chart is too custom for Tremor.
- **Mobile:** plain React Native primitives styled from `theme.ts` tokens. No
  component kit yet — promote shared widgets into `mobile/src/components/` as they
  recur.

## API contract types

UI types are **generated**, never hand-written: `packages/api-types` is produced
from the FastAPI OpenAPI schema. Both apps import from `@fsiq/api-types`
(re-exported through `web/lib/types.ts` / `mobile/src/types.ts`). Regenerate
after any API change:

```bash
pnpm gen:api   # export openapi.json from FastAPI, then run openapi-typescript
```
