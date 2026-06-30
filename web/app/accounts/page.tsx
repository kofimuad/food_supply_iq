"use client";

import Link from "next/link";
import { useState } from "react";
import { AccountForm } from "@/components/account-form";
import { RequireAuth } from "@/components/require-auth";
import { Button } from "@/components/ui/button";
import { ACCOUNT_CATEGORIES, ACCOUNT_STATUSES, categoryLabel, statusLabel } from "@/lib/constants";
import type { Account, AccountCreate } from "@/lib/types";
import {
  useAccounts,
  useCreateAccount,
  useDeleteAccount,
  useUpdateAccount,
  type AccountFilters,
} from "@/lib/use-accounts";

const controlClass = "rounded-md border border-input bg-background px-3 py-2 text-sm";

export default function AccountsPage() {
  return (
    <RequireAuth>
      <AccountsView />
    </RequireAuth>
  );
}

function AccountsView() {
  const [filters, setFilters] = useState<AccountFilters>({});
  const [editing, setEditing] = useState<"new" | Account | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const accounts = useAccounts(filters);
  const createM = useCreateAccount();
  const updateM = useUpdateAccount();
  const deleteM = useDeleteAccount();

  const editingAccount = editing && editing !== "new" ? editing : null;
  const submitting = createM.isPending || updateM.isPending;

  function handleSubmit(body: AccountCreate) {
    setFormError(null);
    const onError = (e: unknown) => setFormError(e instanceof Error ? e.message : "Save failed");
    const onSuccess = () => setEditing(null);
    if (editingAccount) {
      updateM.mutate({ id: editingAccount.id, body }, { onSuccess, onError });
    } else {
      createM.mutate(body, { onSuccess, onError });
    }
  }

  function handleDelete(a: Account) {
    if (confirm(`Delete "${a.name}"? This cannot be undone.`)) deleteM.mutate(a.id);
  }

  const items = accounts.data?.items ?? [];

  return (
    <main className="container mx-auto flex min-h-screen flex-col gap-6 py-10">
      <header className="flex items-center justify-between border-b pb-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Accounts</h1>
          <Link href="/dashboard" className="text-sm text-muted-foreground hover:underline">
            ← Back to dashboard
          </Link>
        </div>
        <Button
          onClick={() => {
            setFormError(null);
            setEditing("new");
          }}
        >
          Add account
        </Button>
      </header>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <input
          className={controlClass}
          placeholder="Search by name…"
          value={filters.q ?? ""}
          onChange={(e) => setFilters((f) => ({ ...f, q: e.target.value || undefined }))}
        />
        <select
          className={controlClass}
          value={filters.category ?? ""}
          onChange={(e) => setFilters((f) => ({ ...f, category: e.target.value || undefined }))}
        >
          <option value="">All categories</option>
          {ACCOUNT_CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
        <select
          className={controlClass}
          value={filters.status ?? ""}
          onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value || undefined }))}
        >
          <option value="">All statuses</option>
          {ACCOUNT_STATUSES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      {editing !== null && (
        <AccountForm
          initial={editingAccount}
          submitting={submitting}
          error={formError}
          onSubmit={handleSubmit}
          onCancel={() => {
            setEditing(null);
            setFormError(null);
          }}
        />
      )}

      {/* Table / states */}
      {accounts.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading accounts…</p>
      ) : accounts.isError ? (
        <p className="text-sm text-destructive">Failed to load accounts.</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-muted-foreground">No accounts yet. Add your first one.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="border-b bg-muted/50 text-left text-muted-foreground">
              <tr>
                <th className="px-4 py-2 font-medium">Name</th>
                <th className="px-4 py-2 font-medium">Category</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 font-medium">Address</th>
                <th className="px-4 py-2 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((a) => (
                <tr key={a.id} className="border-b last:border-0">
                  <td className="px-4 py-2 font-medium">
                    <Link href={`/accounts/${a.id}`} className="hover:underline">
                      {a.name}
                    </Link>
                    {a.is_repeating && (
                      <span className="ml-2 rounded bg-secondary px-1.5 py-0.5 text-xs font-medium text-muted-foreground">
                        Repeating
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2 text-muted-foreground">{categoryLabel(a.category)}</td>
                  <td className="px-4 py-2">{statusLabel(a.status)}</td>
                  <td className="px-4 py-2 text-muted-foreground">{a.address ?? "—"}</td>
                  <td className="px-4 py-2">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setFormError(null);
                          setEditing(a);
                        }}
                      >
                        Edit
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(a)}>
                        Delete
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-xs text-muted-foreground">
        {accounts.data ? `${accounts.data.total} account(s)` : ""}
      </p>
    </main>
  );
}
