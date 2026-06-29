"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "./auth-context";
import type { Account, AccountCreate, AccountProfile, AccountUpdate } from "./types";

export interface AccountFilters {
  category?: string;
  status?: string;
  q?: string;
}

interface AccountsPage {
  items: Account[];
  total: number;
  limit: number;
  offset: number;
}

function toQuery(filters: AccountFilters): string {
  const params = new URLSearchParams();
  if (filters.category) params.set("category", filters.category);
  if (filters.status) params.set("status", filters.status);
  if (filters.q) params.set("q", filters.q);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export function useAccounts(filters: AccountFilters) {
  const { authedFetch } = useAuth();
  return useQuery({
    queryKey: ["accounts", filters],
    queryFn: () => authedFetch<AccountsPage>(`/accounts${toQuery(filters)}`),
  });
}

export function useAccountProfile(id: string) {
  const { authedFetch } = useAuth();
  return useQuery({
    queryKey: ["account-profile", id],
    queryFn: () => authedFetch<AccountProfile>(`/accounts/${id}/profile`),
  });
}

export function useCreateAccount() {
  const { authedFetch } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: AccountCreate) =>
      authedFetch<Account>("/accounts", { method: "POST", body: JSON.stringify(body) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["accounts"] }),
  });
}

export function useUpdateAccount() {
  const { authedFetch } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: AccountUpdate }) =>
      authedFetch<Account>(`/accounts/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["accounts"] }),
  });
}

export function useChangeStatus(id: string) {
  const { authedFetch } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { status: string; note?: string | null }) =>
      authedFetch<Account>(`/accounts/${id}/status`, {
        method: "POST",
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["account-profile", id] });
      qc.invalidateQueries({ queryKey: ["accounts"] });
    },
  });
}

export function useDeleteAccount() {
  const { authedFetch } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => authedFetch<void>(`/accounts/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["accounts"] }),
  });
}
