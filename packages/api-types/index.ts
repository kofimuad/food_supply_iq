// Type-only client contract, generated from the FastAPI OpenAPI schema.
// Regenerate with `pnpm gen:api` whenever the API changes. Do not edit by hand.
export type { components, paths } from "./schema";

import type { components } from "./schema";

type Schemas = components["schemas"];

export type User = Schemas["UserOut"];
export type UserRole = Schemas["UserRole"];
export type TokenPair = Schemas["TokenPair"];
export type LoginRequest = Schemas["LoginRequest"];
export type RefreshRequest = Schemas["RefreshRequest"];

export type Account = Schemas["AccountOut"];
export type AccountCreate = Schemas["AccountCreate"];
export type AccountUpdate = Schemas["AccountUpdate"];
export type AccountCategory = Schemas["AccountCategory"];
export type AccountStatus = Schemas["AccountStatus"];
export type AccountProfile = Schemas["AccountProfile"];
export type Contact = Schemas["ContactOut"];
export type ContactCreate = Schemas["ContactCreate"];
export type ContactUpdate = Schemas["ContactUpdate"];
export type Visit = Schemas["VisitOut"];
export type VisitCreate = Schemas["VisitCreate"];
export type VisitOutcome = Schemas["VisitOutcome"];
export type Media = Schemas["MediaOut"];
export type PresignResponse = Schemas["PresignResponse"];

export type Product = Schemas["ProductOut"];
export type ProductCreate = Schemas["ProductCreate"];
export type ProductUpdate = Schemas["ProductUpdate"];

export type ActivityEvent = Schemas["ActivityEvent"];
export type ActivityFeed = Schemas["ActivityFeed"];

export type Sample = Schemas["SampleOut"];
export type SampleCreate = Schemas["SampleCreate"];
export type Order = Schemas["OrderOut"];
export type OrderCreate = Schemas["OrderCreate"];
export type OrderType = Schemas["OrderType"];
export type FunnelStage = Schemas["FunnelStage"];
export type ClusterCell = Schemas["ClusterCell"];
