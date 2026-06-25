# FoodSupply IQ — Data Model (ERD)

Core schema delivered in **Story 0.2**. All primary keys are UUIDs (generated
client-side by the offline mobile app so syncs are idempotent — Epic 7).
Geospatial columns are PostGIS `geography(Point, 4326)` with GiST indexes.

```mermaid
erDiagram
    users ||--o{ accounts : "assigned_rep"
    users ||--o{ visits : "logged_by"
    users ||--o{ samples : "given_by"
    users ||--o{ orders : "placed_by"

    accounts ||--o{ contacts : has
    accounts ||--o{ visits : receives
    accounts ||--o{ samples : receives
    accounts ||--o{ orders : receives

    visits |o--o{ samples : "during"
    visits |o--o{ orders : "during"
    samples |o--o{ orders : "converted_to (trial)"

    samples ||--o{ sample_items : contains
    orders  ||--o{ order_items : contains
    products ||--o{ sample_items : "sampled_as"
    products ||--o{ order_items : "ordered_as"

    users {
        uuid id PK
        string email UK
        string full_name
        string hashed_password "nullable until Story 0.3"
        enum role "manager | rep"
        bool is_active
    }
    accounts {
        uuid id PK
        string name
        enum category "grocery_store | wholesaler | restaurant | caterer | vendor"
        enum status "lead | in_discussion | sampled | trial | repeat | not_interested"
        string address
        geography location "Point(4326), GiST"
        text notes
        timestamptz last_verified_at
        uuid assigned_rep_id FK
    }
    contacts {
        uuid id PK
        uuid account_id FK
        string name
        string role
        string phone
        bool is_primary
    }
    products {
        uuid id PK
        string name
        string pack_size
        numeric price
        string currency
        bool is_active "soft-delete"
    }
    visits {
        uuid id PK
        uuid account_id FK
        uuid rep_id FK
        geography location "Point(4326)"
        timestamptz occurred_at
        enum outcome "no_contact | interested | not_interested | sample_given | order_placed | follow_up_needed"
        text notes
    }
    samples {
        uuid id PK
        uuid account_id FK
        uuid rep_id FK
        uuid visit_id FK "nullable"
        timestamptz occurred_at
    }
    sample_items {
        uuid id PK
        uuid sample_id FK
        uuid product_id FK
        int quantity
    }
    orders {
        uuid id PK
        uuid account_id FK
        uuid rep_id FK
        enum order_type "trial | repeat"
        uuid sample_id FK "nullable; trial provenance"
        uuid visit_id FK "nullable"
        timestamptz occurred_at
        numeric total_value
        string currency
    }
    order_items {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        numeric unit_price "captured at order time"
    }
```

## Notes & design choices

- **The core loop (Epic 4):** `samples` → `orders(type=trial)` → `orders(type=repeat)`.
  A trial order optionally references the `sample` it converted from, and any
  sample/order optionally references the `visit` it happened during. This is what
  Story 4.4's Sample → Trial → Repeat funnel aggregates over.
- **Line items:** `sample_items` / `order_items` model the many-products-per-event
  relationship. `order_items.unit_price` is captured at order time so later catalog
  price edits never rewrite historical order value.
- **Soft delete:** products use `is_active` rather than hard delete, so historical
  samples/orders keep a valid product reference (`ON DELETE RESTRICT`).
- **Geo:** `accounts.location` and `visits.location` are `geography(Point, 4326)`.
  geoalchemy2 auto-creates the GiST index (`idx_accounts_location`). Distance/
  radius queries use `ST_DWithin` / `ST_Distance` (metres) — see `app/seed.py`.
- **Migrations:** `alembic/versions/` — `0001` enables PostGIS, the core-entities
  revision creates everything above. `alembic/env.py` filters out the PostGIS
  tiger-geocoder / topology tables so autogenerate only manages our tables.
