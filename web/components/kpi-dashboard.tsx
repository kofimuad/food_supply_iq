"use client";

import { useState } from "react";
import { Sparkline } from "@/components/sparkline";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { KpiMetric } from "@/lib/types";
import { useReps } from "@/lib/use-activity";
import { type KpiFilters, useKpis, useSetTargets, useTargets } from "@/lib/use-kpis";

const controlClass = "rounded-md border border-input bg-background px-3 py-2 text-sm";

function fmt(key: string, value: number): string {
  if (key === "revenue") return value.toLocaleString(undefined, { minimumFractionDigits: 2 });
  return String(Math.round(value));
}

function KpiCard({ m }: { m: KpiMetric }) {
  const pct = m.target ? Math.min(100, (m.value / m.target) * 100) : null;
  return (
    <Card>
      <CardContent className="flex flex-col gap-2 pt-6">
        <p className="text-xs uppercase tracking-wide text-muted-foreground">{m.label}</p>
        <div className="flex items-end justify-between">
          <span className="text-2xl font-semibold">{fmt(m.key, m.value)}</span>
          <Sparkline data={m.spark} />
        </div>
        {m.target != null ? (
          <div className="flex flex-col gap-1">
            <div className="h-1.5 w-full rounded bg-secondary">
              <div className="h-1.5 rounded bg-primary" style={{ width: `${pct}%` }} />
            </div>
            <p className="text-xs text-muted-foreground">
              {pct?.toFixed(0)}% of target {fmt(m.key, m.target)}
            </p>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground">No target set</p>
        )}
      </CardContent>
    </Card>
  );
}

function TargetEditor({ metrics }: { metrics: KpiMetric[] }) {
  const targetsQ = useTargets();
  const setM = useSetTargets();
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<Record<string, string>>({});

  function start() {
    const current = targetsQ.data?.targets ?? {};
    setDraft(Object.fromEntries(metrics.map((m) => [m.key, String(current[m.key] ?? "")])));
    setOpen(true);
  }

  function save() {
    const targets: Record<string, number> = {};
    for (const [k, v] of Object.entries(draft)) {
      if (v.trim() !== "" && !Number.isNaN(Number(v))) targets[k] = Number(v);
    }
    setM.mutate(targets, { onSuccess: () => setOpen(false) });
  }

  if (!open) {
    return (
      <Button variant="outline" size="sm" onClick={start}>
        Set targets
      </Button>
    );
  }

  return (
    <Card>
      <CardContent className="flex flex-col gap-3 pt-6">
        <p className="font-semibold">Targets (for the selected window)</p>
        <div className="grid gap-3 sm:grid-cols-3">
          {metrics.map((m) => (
            <label key={m.key} className="flex flex-col gap-1 text-sm">
              {m.label}
              <input
                className={controlClass}
                inputMode="decimal"
                value={draft[m.key] ?? ""}
                onChange={(e) => setDraft((d) => ({ ...d, [m.key]: e.target.value }))}
              />
            </label>
          ))}
        </div>
        <div className="flex gap-2">
          <Button size="sm" onClick={save} disabled={setM.isPending}>
            {setM.isPending ? "Saving…" : "Save targets"}
          </Button>
          <Button size="sm" variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function KpiDashboard() {
  const [filters, setFilters] = useState<KpiFilters>({});
  const kpisQ = useKpis(filters);
  const reps = useReps();
  const metrics = kpisQ.data?.metrics ?? [];

  return (
    <section className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-semibold">KPIs</h2>
        <div className="flex flex-wrap items-center gap-2">
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
          <input
            type="date"
            className={controlClass}
            value={filters.dateFrom ?? ""}
            onChange={(e) => setFilters((f) => ({ ...f, dateFrom: e.target.value || undefined }))}
          />
          <input
            type="date"
            className={controlClass}
            value={filters.dateTo ?? ""}
            onChange={(e) => setFilters((f) => ({ ...f, dateTo: e.target.value || undefined }))}
          />
          {metrics.length > 0 && <TargetEditor metrics={metrics} />}
        </div>
      </div>

      {kpisQ.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading KPIs…</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {metrics.map((m) => (
            <KpiCard key={m.key} m={m} />
          ))}
        </div>
      )}
    </section>
  );
}
