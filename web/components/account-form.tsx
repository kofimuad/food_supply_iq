"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ACCOUNT_CATEGORIES, ACCOUNT_STATUSES } from "@/lib/constants";
import type { Account, AccountCreate } from "@/lib/types";

const inputClass = "rounded-md border border-input bg-background px-3 py-2 text-sm";

interface Props {
  initial?: Account | null;
  submitting?: boolean;
  error?: string | null;
  onSubmit: (body: AccountCreate) => void;
  onCancel: () => void;
}

export function AccountForm({ initial, submitting, error, onSubmit, onCancel }: Props) {
  const [name, setName] = useState(initial?.name ?? "");
  const [category, setCategory] = useState(initial?.category ?? "grocery_store");
  const [status, setStatus] = useState(initial?.status ?? "lead");
  const [address, setAddress] = useState(initial?.address ?? "");
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [lat, setLat] = useState(initial?.lat != null ? String(initial.lat) : "");
  const [lng, setLng] = useState(initial?.lng != null ? String(initial.lng) : "");

  function submit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      name: name.trim(),
      category: category as AccountCreate["category"],
      status: status as AccountCreate["status"],
      address: address.trim() || null,
      notes: notes.trim() || null,
      lat: lat ? Number(lat) : null,
      lng: lng ? Number(lng) : null,
    });
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-4 rounded-lg border p-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm">
          Name
          <input
            className={inputClass}
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Category
          <select
            className={inputClass}
            value={category}
            onChange={(e) => setCategory(e.target.value as typeof category)}
          >
            {ACCOUNT_CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Status
          <select
            className={inputClass}
            value={status}
            onChange={(e) => setStatus(e.target.value as typeof status)}
          >
            {ACCOUNT_STATUSES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Address
          <input
            className={inputClass}
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Geocoded on save"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Latitude (optional)
          <input
            className={inputClass}
            value={lat}
            onChange={(e) => setLat(e.target.value)}
            inputMode="decimal"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Longitude (optional)
          <input
            className={inputClass}
            value={lng}
            onChange={(e) => setLng(e.target.value)}
            inputMode="decimal"
          />
        </label>
      </div>
      <label className="flex flex-col gap-1 text-sm">
        Notes
        <textarea
          className={inputClass}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
        />
      </label>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <div className="flex gap-2">
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving…" : initial ? "Save changes" : "Create account"}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
