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
