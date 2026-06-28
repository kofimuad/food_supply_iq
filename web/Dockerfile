# FoodSupply IQ web (Next.js standalone).
# Build context: the REPO ROOT (so the pnpm workspace + packages/ are available).
# On Railway: set the web service Root Directory = "/" and config path = web/railway.json.
FROM node:20-slim AS builder
RUN corepack enable
WORKDIR /repo

# NEXT_PUBLIC_* are inlined into the client bundle at build time, so they must be
# present during `next build`. Railway passes service variables as build args;
# declare them here so they reach the build (and fail loudly if unset is fine —
# it falls back to the localhost default in lib/api.ts).
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_MAPBOX_TOKEN
ENV NEXT_PUBLIC_MAPBOX_TOKEN=$NEXT_PUBLIC_MAPBOX_TOKEN

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
# Next's standalone server binds to localhost unless HOSTNAME is set; bind to
# all interfaces so Railway's healthcheck (external) can reach it.
ENV HOSTNAME=0.0.0.0

# Standalone bundle (traced from the monorepo root) + static assets.
COPY --from=builder /repo/web/.next/standalone ./
COPY --from=builder /repo/web/.next/static ./web/.next/static

EXPOSE 3000
CMD ["node", "web/server.js"]
