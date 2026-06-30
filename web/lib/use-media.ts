"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "./auth-context";
import type { Media } from "./types";

export function useVisitMedia(visitId: string) {
  const { authedFetch } = useAuth();
  return useQuery({
    queryKey: ["visit-media", visitId],
    queryFn: () => authedFetch<Media[]>(`/visits/${visitId}/media`),
  });
}
