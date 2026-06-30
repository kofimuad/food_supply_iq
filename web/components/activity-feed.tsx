"use client";

import Link from "next/link";
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { useActivity, useReps } from "@/lib/use-activity";

const controlClass = "rounded-md border border-input bg-background px-3 py-2 text-sm";

const TYPE_LABEL: Record<string, string> = {
  visit: "Visit",
  sample: "Sample",
  order: "Order",
};

export function ActivityFeed() {
  const [repId, setRepId] = useState("");
  const feed = useActivity(repId || undefined);
  const reps = useReps();

  const items = feed.data?.items ?? [];

  return (
    <Card>
      <CardContent className="flex flex-col gap-3 pt-6">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Team activity</h2>
          <select className={controlClass} value={repId} onChange={(e) => setRepId(e.target.value)}>
            <option value="">All reps</option>
            {(reps.data ?? []).map((r) => (
              <option key={r.id} value={r.id}>
                {r.full_name}
              </option>
            ))}
          </select>
        </div>

        {feed.isLoading ? (
          <p className="text-sm text-muted-foreground">Loading activity…</p>
        ) : items.length === 0 ? (
          <p className="text-sm text-muted-foreground">No recent activity.</p>
        ) : (
          <ul className="flex flex-col divide-y">
            {items.map((e) => (
              <li
                key={`${e.type}-${e.id}`}
                className="flex items-center justify-between py-2 text-sm"
              >
                <div className="flex items-center gap-2">
                  <span className="rounded bg-secondary px-2 py-0.5 text-xs font-medium">
                    {TYPE_LABEL[e.type] ?? e.type}
                  </span>
                  <Link href={`/accounts/${e.account_id}`} className="font-medium hover:underline">
                    {e.account_name}
                  </Link>
                  <span className="text-muted-foreground">· {e.detail}</span>
                </div>
                <span className="text-muted-foreground">
                  {new Date(e.occurred_at).toLocaleString(undefined, {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
