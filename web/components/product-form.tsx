"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import type { Product, ProductCreate } from "@/lib/types";

const inputClass = "rounded-md border border-input bg-background px-3 py-2 text-sm";

interface Props {
  initial?: Product | null;
  submitting?: boolean;
  error?: string | null;
  onSubmit: (body: ProductCreate) => void;
  onCancel: () => void;
}

export function ProductForm({ initial, submitting, error, onSubmit, onCancel }: Props) {
  const [name, setName] = useState(initial?.name ?? "");
  const [packSize, setPackSize] = useState(initial?.pack_size ?? "");
  const [price, setPrice] = useState(initial?.price != null ? String(initial.price) : "");
  const [currency, setCurrency] = useState(initial?.currency ?? "USD");

  function submit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      name: name.trim(),
      pack_size: packSize.trim() || null,
      price: price ? Number(price) : null,
      currency: currency.trim().toUpperCase() || "USD",
      is_active: initial?.is_active ?? true,
    });
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-4 rounded-lg border p-4">
      <div className="grid gap-4 sm:grid-cols-4">
        <label className="flex flex-col gap-1 text-sm sm:col-span-2">
          Name
          <input
            className={inputClass}
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Pack size
          <input
            className={inputClass}
            value={packSize}
            onChange={(e) => setPackSize(e.target.value)}
            placeholder="e.g. 5kg"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Price
          <input
            className={inputClass}
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            inputMode="decimal"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Currency
          <input
            className={inputClass}
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            maxLength={3}
          />
        </label>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <div className="flex gap-2">
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving…" : initial ? "Save changes" : "Add product"}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
