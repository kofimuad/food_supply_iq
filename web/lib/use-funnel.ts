"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "./auth-context";
import type { Account, FunnelStage } from "./types";

export interface FunnelFilters {
  repId?: string;
  dateFrom?: string;
  dateTo?: string;
}

function toQuery(f: FunnelFilters): string {
  const params = new URLSearchParams();
  if (f.repId) params.set("rep_id", f.repId);
  if (f.dateFrom) params.set("date_from", f.dateFrom);
  if (f.dateTo) params.set("date_to", f.dateTo);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export function useFunnel(filters: FunnelFilters) {
  const { authedFetch } = useAuth();
  return useQuery({
    queryKey: ["funnel", filters],
    queryFn: () => authedFetch<FunnelStage[]>(`/funnel${toQuery(filters)}`),
  });
}

export function useFunnelAccounts(stage: string | null, filters: FunnelFilters) {
  const { authedFetch } = useAuth();
  return useQuery({
    enabled: stage !== null,
    queryKey: ["funnel-accounts", stage, filters],
    queryFn: () => {
      const params = new URLSearchParams(toQuery(filters).replace(/^\?/, ""));
      params.set("stage", stage as string);
      return authedFetch<Account[]>(`/funnel/accounts?${params.toString()}`);
    },
  });
}
