"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "./auth-context";
import type { Contact, ContactCreate, ContactUpdate } from "./types";

/** All contact mutations refresh the owning account's profile query. */
function useInvalidateProfile(accountId: string) {
  const qc = useQueryClient();
  return () => qc.invalidateQueries({ queryKey: ["account-profile", accountId] });
}

export function useCreateContact(accountId: string) {
  const { authedFetch } = useAuth();
  const invalidate = useInvalidateProfile(accountId);
  return useMutation({
    mutationFn: (body: ContactCreate) =>
      authedFetch<Contact>(`/accounts/${accountId}/contacts`, {
        method: "POST",
        body: JSON.stringify(body),
      }),
    onSuccess: invalidate,
  });
}

export function useUpdateContact(accountId: string) {
  const { authedFetch } = useAuth();
  const invalidate = useInvalidateProfile(accountId);
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: ContactUpdate }) =>
      authedFetch<Contact>(`/contacts/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
    onSuccess: invalidate,
  });
}

export function useDeleteContact(accountId: string) {
  const { authedFetch } = useAuth();
  const invalidate = useInvalidateProfile(accountId);
  return useMutation({
    mutationFn: (id: string) => authedFetch<void>(`/contacts/${id}`, { method: "DELETE" }),
    onSuccess: invalidate,
  });
}
