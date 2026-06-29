import { authedFetch } from "./auth";
import type { Account, AccountProfile } from "./types";

interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

/** The rep's accounts (the API scopes this to the signed-in rep). */
export function fetchAccounts(): Promise<Page<Account>> {
  return authedFetch<Page<Account>>("/accounts");
}

export function fetchProfile(id: string): Promise<AccountProfile> {
  return authedFetch<AccountProfile>(`/accounts/${id}/profile`);
}

export function changeStatus(id: string, status: string, note?: string): Promise<Account> {
  return authedFetch<Account>(`/accounts/${id}/status`, {
    method: "POST",
    body: JSON.stringify({ status, note: note ?? null }),
  });
}
