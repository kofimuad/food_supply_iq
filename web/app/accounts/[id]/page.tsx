"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { ContactsEditor } from "@/components/contacts-editor";
import { RequireAuth } from "@/components/require-auth";
import { StatusControl } from "@/components/status-control";
import { VisitPhotos } from "@/components/visit-photos";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/lib/auth-context";
import { categoryLabel, statusLabel } from "@/lib/constants";
import { useAccountProfile } from "@/lib/use-accounts";

type Tab = "overview" | "history" | "contacts";

export default function AccountProfilePage() {
  return (
    <RequireAuth>
      <ProfileView />
    </RequireAuth>
  );
}

function ProfileView() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>("overview");
  const { data, isLoading, isError } = useAccountProfile(params.id);

  if (isLoading) {
    return <Centered>Loading profile…</Centered>;
  }
  if (isError || !data) {
    return <Centered>Account not found.</Centered>;
  }

  const { account, contacts, recent_visits, summary } = data;

  return (
    <main className="container mx-auto flex min-h-screen flex-col gap-6 py-10">
      <header className="border-b pb-4">
        <Link href="/accounts" className="text-sm text-muted-foreground hover:underline">
          ← Back to accounts
        </Link>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight">
          {account.name}
          {account.is_repeating && (
            <span className="ml-2 align-middle rounded bg-secondary px-2 py-0.5 text-xs font-medium text-muted-foreground">
              Repeating
            </span>
          )}
        </h1>
        <p className="text-sm text-muted-foreground">
          {categoryLabel(account.category)} · {statusLabel(account.status)}
          {account.repeat_order_count > 0 && ` · ${account.repeat_order_count} repeat order(s)`}
        </p>
      </header>

      <nav className="flex gap-1 border-b">
        {(["overview", "history", "contacts"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`border-b-2 px-4 py-2 text-sm capitalize ${
              tab === t
                ? "border-foreground font-medium"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {t}
            {t === "contacts" ? ` (${contacts.length})` : ""}
            {t === "history" ? ` (${recent_visits.length})` : ""}
          </button>
        ))}
      </nav>

      {tab === "overview" && (
        <div className="flex flex-col gap-4">
          <div className="grid gap-3 sm:grid-cols-4">
            <Stat label="Visits" value={summary.visits} />
            <Stat label="Samples" value={summary.samples} />
            <Stat label="Orders" value={summary.orders} />
            <Stat
              label="Last visit"
              value={summary.last_visit_at ? formatDate(summary.last_visit_at) : "—"}
            />
          </div>
          <Card>
            <CardContent className="pt-6">
              <StatusControl accountId={account.id} current={account.status} />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="grid gap-3 pt-6 text-sm sm:grid-cols-2">
              <Field label="Address" value={account.address ?? "—"} />
              <Field
                label="Location"
                value={
                  account.lat != null && account.lng != null
                    ? `${account.lat.toFixed(4)}, ${account.lng.toFixed(4)}`
                    : "Not geocoded"
                }
              />
              <Field label="Notes" value={account.notes ?? "—"} />
            </CardContent>
          </Card>
        </div>
      )}

      {tab === "history" &&
        (recent_visits.length === 0 ? (
          <p className="text-sm text-muted-foreground">No visits logged yet.</p>
        ) : (
          <ul className="flex flex-col gap-3">
            {recent_visits.map((v) => (
              <li key={v.id} className="rounded-lg border p-4 text-sm">
                <div className="flex justify-between">
                  <span className="font-medium">{v.outcome ?? "visit"}</span>
                  <span className="text-muted-foreground">{formatDate(v.occurred_at)}</span>
                </div>
                {v.notes && <p className="mt-1 text-muted-foreground">{v.notes}</p>}
                <VisitPhotos visitId={v.id} />
              </li>
            ))}
          </ul>
        ))}

      {tab === "contacts" && (
        <ContactsEditor
          accountId={account.id}
          contacts={contacts}
          editable={user?.role === "manager"}
        />
      )}
    </main>
  );
}

function Centered({ children }: { children: React.ReactNode }) {
  return (
    <main className="container mx-auto flex min-h-screen items-center justify-center">
      <p className="text-sm text-muted-foreground">{children}</p>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-xl font-semibold">{value}</p>
      </CardContent>
    </Card>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p>{value}</p>
    </div>
  );
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}
