"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "./auth-context";
import type { ActivityFeed, User } from "./types";

export function useActivity(repId?: string) {
  const { authedFetch } = useAuth();
  return useQuery({
    queryKey: ["activity", repId ?? null],
    queryFn: () => authedFetch<ActivityFeed>(`/activity${repId ? `?rep_id=${repId}` : ""}`),
    refetchInterval: 15000, // near-real-time polling
  });
}

export function useReps() {
  const { authedFetch } = useAuth();
  return useQuery({
    queryKey: ["reps"],
    queryFn: () => authedFetch<User[]>("/users?role=rep"),
  });
}
