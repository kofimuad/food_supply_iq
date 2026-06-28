# FoodSupply IQ web (Next.js standalone).
# Build context: the REPO ROOT (so the pnpm workspace + packages/ are available).
# On Railway: set the web service Root Directory = "/" and config path = web/railway.json.
FROM node:20-slim AS builder
RUN corepack enable
WORKDIR /repo

# Workspace manifests first for layer caching.
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml .npmrc ./
COPY packages ./packages
COPY web ./web

RUN pnpm install --frozen-lockfile --filter web...
RUN pnpm --filter web build

FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000

# Standalone bundle (traced from the monorepo root) + static assets.
COPY --from=builder /repo/web/.next/standalone ./
COPY --from=builder /repo/web/.next/static ./web/.next/static

EXPOSE 3000
CMD ["node", "web/server.js"]
