"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "./auth-context";
import type { KpiResponse } from "./types";

export interface KpiFilters {
  repId?: string;
  dateFrom?: string;
  dateTo?: string;
}

export function useKpis(filters: KpiFilters) {
  const { authedFetch } = useAuth();
  return useQuery({
    queryKey: ["kpis", filters],
    queryFn: () => {
      const params = new URLSearchParams();
      if (filters.repId) params.set("rep_id", filters.repId);
      if (filters.dateFrom) params.set("date_from", filters.dateFrom);
      if (filters.dateTo) params.set("date_to", filters.dateTo);
      const qs = params.toString();
      return authedFetch<KpiResponse>(`/kpis${qs ? `?${qs}` : ""}`);
    },
  });
}

export function useTargets() {
  const { authedFetch } = useAuth();
  return useQuery({
    queryKey: ["kpi-targets"],
    queryFn: () => authedFetch<{ targets: Record<string, number> }>("/kpis/targets"),
  });
}

export function useSetTargets() {
  const { authedFetch } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (targets: Record<string, number>) =>
      authedFetch<{ targets: Record<string, number> }>("/kpis/targets", {
        method: "PUT",
        body: JSON.stringify({ targets }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["kpi-targets"] });
      qc.invalidateQueries({ queryKey: ["kpis"] });
    },
  });
}
