"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ACCOUNT_STATUSES, statusLabel } from "@/lib/constants";
import { useChangeStatus } from "@/lib/use-accounts";

const inputClass = "rounded-md border border-input bg-background px-3 py-2 text-sm";

export function StatusControl({ accountId, current }: { accountId: string; current: string }) {
  const [next, setNext] = useState(current);
  const [note, setNote] = useState("");
  const [error, setError] = useState<string | null>(null);
  const changeM = useChangeStatus(accountId);

  function apply() {
    setError(null);
    if (next === current) return;
    if (!confirm(`Change status to "${statusLabel(next)}"?`)) return;
    changeM.mutate(
      { status: next, note: note.trim() || null },
      {
        onSuccess: () => setNote(""),
        onError: (e) => setError(e instanceof Error ? e.message : "Status change failed"),
      },
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs text-muted-foreground">Pipeline status</p>
      <div className="flex flex-wrap items-center gap-2">
        <select className={inputClass} value={next} onChange={(e) => setNext(e.target.value)}>
          {ACCOUNT_STATUSES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
        <input
          className={`${inputClass} flex-1`}
          placeholder="Note (optional)"
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
        <Button onClick={apply} disabled={next === current || changeM.isPending}>
          {changeM.isPending ? "Updating…" : "Update"}
        </Button>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  );
}
