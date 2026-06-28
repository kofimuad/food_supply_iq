import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Standalone server for a small production image.
  output: "standalone",
  experimental: {
    // Trace workspace deps from the monorepo root so the standalone bundle is complete.
    // (Top-level in Next 15; under `experimental` in Next 14.)
    outputFileTracingRoot: path.join(__dirname, ".."),
  },
};

export default nextConfig;
