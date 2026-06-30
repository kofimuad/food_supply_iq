"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "./auth-context";
import type { Account, ClusterCell } from "./types";

interface AccountsPage {
  items: Account[];
}

export function useMapAccounts() {
  const { authedFetch } = useAuth();
  return useQuery({
    queryKey: ["map-accounts"],
    queryFn: () => authedFetch<AccountsPage>("/accounts?limit=200"),
  });
}

export function useClusters(precision = 1) {
  const { authedFetch } = useAuth();
  return useQuery({
    queryKey: ["clusters", precision],
    queryFn: () => authedFetch<ClusterCell[]>(`/geo/accounts/clusters?precision=${precision}`),
  });
}
