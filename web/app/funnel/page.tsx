"use client";

import Link from "next/link";
import { useState } from "react";
import { RequireAuth } from "@/components/require-auth";
import { Card, CardContent } from "@/components/ui/card";
import { statusLabel } from "@/lib/constants";
import { useReps } from "@/lib/use-activity";
import { type FunnelFilters, useFunnel, useFunnelAccounts } from "@/lib/use-funnel";

const controlClass = "rounded-md border border-input bg-background px-3 py-2 text-sm";

export default function FunnelPage() {
  return (
    <RequireAuth>
      <FunnelView />
    </RequireAuth>
  );
}

function FunnelView() {
  const [filters, setFilters] = useState<FunnelFilters>({});
  const [stage, setStage] = useState<string | null>(null);
  const funnel = useFunnel(filters);
  const reps = useReps();
  const drill = useFunnelAccounts(stage, filters);

  const stages = funnel.data ?? [];
  const max = Math.max(1, ...stages.map((s) => s.count));

  return (
    <main className="container mx-auto flex min-h-screen flex-col gap-6 py-10">
      <header className="flex items-center justify-between border-b pb-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Sample → Trial → Repeat funnel</h1>
          <Link href="/dashboard" className="text-sm text-muted-foreground hover:underline">
            ← Back to dashboard
          </Link>
        </div>
      </header>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <select
          className={controlClass}
          value={filters.repId ?? ""}
          onChange={(e) => setFilters((f) => ({ ...f, repId: e.target.value || undefined }))}
        >
          <option value="">All reps</option>
          {(reps.data ?? []).map((r) => (
            <option key={r.id} value={r.id}>
              {r.full_name}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-1 text-sm text-muted-foreground">
          From
          <input
            type="date"
            className={controlClass}
            value={filters.dateFrom ?? ""}
            onChange={(e) => setFilters((f) => ({ ...f, dateFrom: e.target.value || undefined }))}
          />
        </label>
        <label className="flex items-center gap-1 text-sm text-muted-foreground">
          To
          <input
            type="date"
            className={controlClass}
            value={filters.dateTo ?? ""}
            onChange={(e) => setFilters((f) => ({ ...f, dateTo: e.target.value || undefined }))}
          />
        </label>
      </div>

      {/* Funnel bars */}
      <Card>
        <CardContent className="flex flex-col gap-4 pt-6">
          {funnel.isLoading ? (
            <p className="text-sm text-muted-foreground">Loading…</p>
          ) : (
            stages.map((s) => (
              <button
                key={s.key}
                onClick={() => setStage(s.key)}
                className="flex flex-col gap-1 text-left"
              >
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{s.label}</span>
                  <span className="text-muted-foreground">
                    {s.count}
                    {s.conversion_from_prev != null && ` · ${s.conversion_from_prev}% from prev`}
                  </span>
                </div>
                <div className="h-6 w-full rounded bg-secondary">
                  <div
                    className={`h-6 rounded bg-primary ${stage === s.key ? "opacity-100" : "opacity-80"}`}
                    style={{ width: `${(s.count / max) * 100}%` }}
                  />
                </div>
              </button>
            ))
          )}
          <p className="text-xs text-muted-foreground">Click a stage to list its accounts.</p>
        </CardContent>
      </Card>

      {/* Drill-down */}
      {stage && (
        <Card>
          <CardContent className="pt-6">
            <h2 className="mb-2 font-semibold capitalize">{stage} accounts</h2>
            {drill.isLoading ? (
              <p className="text-sm text-muted-foreground">Loading…</p>
            ) : (drill.data ?? []).length === 0 ? (
              <p className="text-sm text-muted-foreground">No accounts at this stage.</p>
            ) : (
              <ul className="flex flex-col divide-y">
                {(drill.data ?? []).map((a) => (
                  <li key={a.id} className="flex justify-between py-2 text-sm">
                    <Link href={`/accounts/${a.id}`} className="font-medium hover:underline">
                      {a.name}
                    </Link>
                    <span className="text-muted-foreground">{statusLabel(a.status)}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      )}
    </main>
  );
}
