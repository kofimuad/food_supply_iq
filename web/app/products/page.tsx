"use client";

import Link from "next/link";
import { useState } from "react";
import { ProductForm } from "@/components/product-form";
import { RequireAuth } from "@/components/require-auth";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";
import type { Product, ProductCreate } from "@/lib/types";
import {
  useCreateProduct,
  useDeactivateProduct,
  useProducts,
  useUpdateProduct,
} from "@/lib/use-products";

const controlClass = "rounded-md border border-input bg-background px-3 py-2 text-sm";

export default function ProductsPage() {
  return (
    <RequireAuth>
      <CatalogView />
    </RequireAuth>
  );
}

function CatalogView() {
  const { user } = useAuth();
  const isManager = user?.role === "manager";
  const [q, setQ] = useState("");
  const [includeInactive, setIncludeInactive] = useState(false);
  const [editing, setEditing] = useState<"new" | Product | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const products = useProducts({ q: q || undefined, includeInactive });
  const createM = useCreateProduct();
  const updateM = useUpdateProduct();
  const deactivateM = useDeactivateProduct();

  const editingProduct = editing && editing !== "new" ? editing : null;
  const submitting = createM.isPending || updateM.isPending;

  function handleSubmit(body: ProductCreate) {
    setFormError(null);
    const onError = (e: unknown) => setFormError(e instanceof Error ? e.message : "Save failed");
    const onSuccess = () => setEditing(null);
    if (editingProduct) {
      updateM.mutate({ id: editingProduct.id, body }, { onSuccess, onError });
    } else {
      createM.mutate(body, { onSuccess, onError });
    }
  }

  const items = products.data?.items ?? [];

  return (
    <main className="container mx-auto flex min-h-screen flex-col gap-6 py-10">
      <header className="flex items-center justify-between border-b pb-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Product catalog</h1>
          <Link href="/dashboard" className="text-sm text-muted-foreground hover:underline">
            ← Back to dashboard
          </Link>
        </div>
        {isManager && (
          <Button
            onClick={() => {
              setFormError(null);
              setEditing("new");
            }}
          >
            Add product
          </Button>
        )}
      </header>

      <div className="flex flex-wrap items-center gap-3">
        <input
          className={controlClass}
          placeholder="Search by name…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <label className="flex items-center gap-2 text-sm text-muted-foreground">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(e) => setIncludeInactive(e.target.checked)}
          />
          Show inactive
        </label>
      </div>

      {editing !== null && isManager && (
        <ProductForm
          initial={editingProduct}
          submitting={submitting}
          error={formError}
          onSubmit={handleSubmit}
          onCancel={() => {
            setEditing(null);
            setFormError(null);
          }}
        />
      )}

      {products.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading catalog…</p>
      ) : products.isError ? (
        <p className="text-sm text-destructive">Failed to load catalog.</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-muted-foreground">No products yet.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="border-b bg-muted/50 text-left text-muted-foreground">
              <tr>
                <th className="px-4 py-2 font-medium">Name</th>
                <th className="px-4 py-2 font-medium">Pack size</th>
                <th className="px-4 py-2 font-medium">Price</th>
                <th className="px-4 py-2 font-medium">Status</th>
                {isManager && <th className="px-4 py-2 text-right font-medium">Actions</th>}
              </tr>
            </thead>
            <tbody>
              {items.map((p) => (
                <tr key={p.id} className="border-b last:border-0">
                  <td className="px-4 py-2 font-medium">{p.name}</td>
                  <td className="px-4 py-2 text-muted-foreground">{p.pack_size ?? "—"}</td>
                  <td className="px-4 py-2">
                    {p.price != null ? `${p.price.toFixed(2)} ${p.currency}` : "—"}
                  </td>
                  <td className="px-4 py-2">
                    <span className={p.is_active ? "" : "text-muted-foreground"}>
                      {p.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  {isManager && (
                    <td className="px-4 py-2">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setFormError(null);
                            setEditing(p);
                          }}
                        >
                          Edit
                        </Button>
                        {p.is_active ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              confirm(`Deactivate "${p.name}"?`) && deactivateM.mutate(p.id)
                            }
                          >
                            Deactivate
                          </Button>
                        ) : (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => updateM.mutate({ id: p.id, body: { is_active: true } })}
                          >
                            Reactivate
                          </Button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
