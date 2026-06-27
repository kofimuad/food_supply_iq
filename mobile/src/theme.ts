// FoodSupply IQ mobile design tokens — mirrors the web shadcn palette
// (plain, data-dense, black-on-white). Keep in sync with web/app/globals.css
// and docs/design-system.md.

export const colors = {
  background: "#ffffff",
  foreground: "#0a0a0a",
  muted: "#737373",
  border: "#cccccc",
  primary: "#111111",
  primaryForeground: "#fafafa",
  accent: "#f5f5f5",
  destructive: "#c0392b",
} as const;

export const spacing = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24 } as const;

export const radius = { sm: 6, md: 8 } as const;

export const fontSize = { sm: 13, base: 15, lg: 16, title: 28 } as const;
