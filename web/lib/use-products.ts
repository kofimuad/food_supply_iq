"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "./auth-context";
import type { Product, ProductCreate, ProductUpdate } from "./types";

interface ProductsPage {
  items: Product[];
  total: number;
  limit: number;
  offset: number;
}

export function useProducts(opts: { q?: string; includeInactive?: boolean }) {
  const { authedFetch } = useAuth();
  return useQuery({
    queryKey: ["products", opts],
    queryFn: () => {
      const params = new URLSearchParams();
      if (opts.q) params.set("q", opts.q);
      if (opts.includeInactive) params.set("include_inactive", "true");
      const qs = params.toString();
      return authedFetch<ProductsPage>(`/products${qs ? `?${qs}` : ""}`);
    },
  });
}

export function useCreateProduct() {
  const { authedFetch } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: ProductCreate) =>
      authedFetch<Product>("/products", { method: "POST", body: JSON.stringify(body) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["products"] }),
  });
}

export function useUpdateProduct() {
  const { authedFetch } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: ProductUpdate }) =>
      authedFetch<Product>(`/products/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["products"] }),
  });
}

export function useDeactivateProduct() {
  const { authedFetch } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => authedFetch<Product>(`/products/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["products"] }),
  });
}
