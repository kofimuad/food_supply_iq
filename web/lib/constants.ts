import type { AccountCategory, AccountStatus } from "./types";

export const ACCOUNT_CATEGORIES: { value: AccountCategory; label: string }[] = [
  { value: "grocery_store", label: "Grocery store" },
  { value: "wholesaler", label: "Wholesaler" },
  { value: "restaurant", label: "Restaurant" },
  { value: "caterer", label: "Caterer" },
  { value: "vendor", label: "Vendor" },
];

export const ACCOUNT_STATUSES: { value: AccountStatus; label: string }[] = [
  { value: "lead", label: "Lead" },
  { value: "in_discussion", label: "In discussion" },
  { value: "sampled", label: "Sampled" },
  { value: "trial", label: "Trial" },
  { value: "repeat", label: "Repeat" },
  { value: "not_interested", label: "Not interested" },
];

// Marker/legend colors per pipeline status (data viz — distinct from the
// black-on-white chrome). Keep in sync with ACCOUNT_STATUSES.
export const STATUS_COLORS: Record<string, string> = {
  lead: "#9ca3af",
  in_discussion: "#3b82f6",
  sampled: "#f59e0b",
  trial: "#8b5cf6",
  repeat: "#10b981",
  not_interested: "#ef4444",
};

export function categoryLabel(value: string): string {
  return ACCOUNT_CATEGORIES.find((c) => c.value === value)?.label ?? value;
}

export function statusLabel(value: string): string {
  return ACCOUNT_STATUSES.find((s) => s.value === value)?.label ?? value;
}
