"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { RequireAuth } from "@/components/require-auth";
import { Card, CardContent } from "@/components/ui/card";
import { ACCOUNT_STATUSES, STATUS_COLORS, statusLabel } from "@/lib/constants";
import { useAuth } from "@/lib/auth-context";
import { useClusters, useMapAccounts } from "@/lib/use-map";

// MapLibre touches `window`, so load the map only on the client.
const AccountMap = dynamic(() => import("@/components/account-map").then((m) => m.AccountMap), {
  ssr: false,
  loading: () => <div className="h-[70vh] w-full rounded-lg border" />,
});

export default function MapPage() {
  return (
    <RequireAuth>
      <MapView />
    </RequireAuth>
  );
}

function MapView() {
  const { user } = useAuth();
  const isManager = user?.role === "manager";
  const accountsQ = useMapAccounts();
  const clustersQ = useClusters(1);

  const accounts = accountsQ.data?.items ?? [];
  const geocoded = accounts.filter((a) => a.lat != null && a.lng != null);
  const counts = ACCOUNT_STATUSES.map((s) => ({
    ...s,
    n: geocoded.filter((a) => a.status === s.value).length,
  }));

  return (
    <main className="container mx-auto flex min-h-screen flex-col gap-6 py-10">
      <header className="flex items-center justify-between border-b pb-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Map &amp; territory</h1>
          <Link href="/dashboard" className="text-sm text-muted-foreground hover:underline">
            ← Back to dashboard
          </Link>
        </div>
        <span className="text-sm text-muted-foreground">
          {geocoded.length} of {accounts.length} accounts mapped
        </span>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1fr_260px]">
        <AccountMap accounts={geocoded} />

        <aside className="flex flex-col gap-4">
          <Card>
            <CardContent className="flex flex-col gap-2 pt-6 text-sm">
              <p className="font-semibold">By status</p>
              {counts.map((s) => (
                <div key={s.value} className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <span
                      className="inline-block h-3 w-3 rounded-full"
                      style={{ backgroundColor: STATUS_COLORS[s.value] }}
                    />
                    {s.label}
                  </span>
                  <span className="text-muted-foreground">{s.n}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          {isManager && (
            <Card>
              <CardContent className="pt-6 text-sm">
                <p className="font-semibold">Coverage</p>
                <p className="mt-1 text-muted-foreground">
                  {clustersQ.data
                    ? `${clustersQ.data.length} area cluster(s) across the geocoded accounts.`
                    : "Loading clusters…"}
                </p>
              </CardContent>
            </Card>
          )}

          <p className="text-xs text-muted-foreground">
            Markers are colored by pipeline status; click a cluster to zoom, a marker for its
            profile. {statusLabel("repeat")} = won, repeating accounts.
          </p>
        </aside>
      </div>
    </main>
  );
}
