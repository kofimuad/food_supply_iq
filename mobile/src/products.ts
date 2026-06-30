import { authedFetch } from "./auth";
import type { Product } from "./types";

interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

// Simple in-session cache of the catalog for the sample/order pickers.
// (Durable offline caching arrives with Epic 7.)
let cache: Product[] | null = null;

export async function fetchActiveProducts(force = false): Promise<Product[]> {
  if (cache && !force) return cache;
  const page = await authedFetch<Page<Product>>("/products");
  cache = page.items;
  return cache;
}
