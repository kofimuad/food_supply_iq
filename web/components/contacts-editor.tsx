"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import type { Contact, ContactCreate } from "@/lib/types";
import { useCreateContact, useDeleteContact, useUpdateContact } from "@/lib/use-contacts";

const inputClass = "rounded-md border border-input bg-background px-3 py-2 text-sm";

interface Props {
  accountId: string;
  contacts: Contact[];
  editable: boolean;
}

const EMPTY: ContactCreate = { name: "", role: null, phone: null, is_primary: false };

export function ContactsEditor({ accountId, contacts, editable }: Props) {
  const createM = useCreateContact(accountId);
  const updateM = useUpdateContact(accountId);
  const deleteM = useDeleteContact(accountId);

  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<ContactCreate>(EMPTY);

  function startAdd() {
    setEditingId("new");
    setForm(EMPTY);
  }
  function startEdit(c: Contact) {
    setEditingId(c.id);
    setForm({ name: c.name, role: c.role, phone: c.phone, is_primary: c.is_primary });
  }
  function reset() {
    setEditingId(null);
    setForm(EMPTY);
  }

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const body = {
      name: form.name.trim(),
      role: form.role?.trim() || null,
      phone: form.phone?.trim() || null,
      is_primary: form.is_primary,
    };
    if (editingId && editingId !== "new") {
      updateM.mutate({ id: editingId, body }, { onSuccess: reset });
    } else {
      createM.mutate(body, { onSuccess: reset });
    }
  }

  return (
    <div className="flex flex-col gap-3">
      {contacts.length === 0 && editingId === null && (
        <p className="text-sm text-muted-foreground">No contacts yet.</p>
      )}

      <ul className="flex flex-col gap-2">
        {contacts.map((c) => (
          <li
            key={c.id}
            className="flex items-center justify-between rounded-lg border p-3 text-sm"
          >
            <div>
              <span className="font-medium">{c.name}</span>
              {c.is_primary && (
                <span className="ml-2 text-xs text-muted-foreground">(primary)</span>
              )}
              {c.role && <span className="ml-2 text-muted-foreground">· {c.role}</span>}
            </div>
            <div className="flex items-center gap-3">
              {c.phone && (
                <a href={`tel:${c.phone}`} className="text-muted-foreground hover:underline">
                  {c.phone}
                </a>
              )}
              {editable && (
                <div className="flex gap-1">
                  <Button variant="outline" size="sm" onClick={() => startEdit(c)}>
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => confirm(`Remove ${c.name}?`) && deleteM.mutate(c.id)}
                  >
                    Remove
                  </Button>
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>

      {editable &&
        (editingId !== null ? (
          <form onSubmit={submit} className="flex flex-col gap-3 rounded-lg border p-4">
            <div className="grid gap-3 sm:grid-cols-3">
              <input
                className={inputClass}
                placeholder="Name"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                required
              />
              <input
                className={inputClass}
                placeholder="Role"
                value={form.role ?? ""}
                onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
              />
              <input
                className={inputClass}
                placeholder="Phone"
                value={form.phone ?? ""}
                onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
              />
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.is_primary ?? false}
                onChange={(e) => setForm((f) => ({ ...f, is_primary: e.target.checked }))}
              />
              Primary contact
            </label>
            <div className="flex gap-2">
              <Button type="submit" disabled={createM.isPending || updateM.isPending}>
                {editingId === "new" ? "Add contact" : "Save"}
              </Button>
              <Button type="button" variant="outline" onClick={reset}>
                Cancel
              </Button>
            </div>
          </form>
        ) : (
          <div>
            <Button variant="outline" size="sm" onClick={startAdd}>
              Add contact
            </Button>
          </div>
        ))}
    </div>
  );
}
