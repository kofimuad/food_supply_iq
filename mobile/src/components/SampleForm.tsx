import { useEffect, useState } from "react";
import { ActivityIndicator, Alert, Pressable, StyleSheet, Text, View } from "react-native";
import { fetchActiveProducts } from "../products";
import { recordSample } from "../sales";
import { colors, fontSize, radius, spacing } from "../theme";
import type { Product } from "../types";

interface Props {
  accountId: string;
  onDone: () => void;
}

export function SampleForm({ accountId, onDone }: Props) {
  const [products, setProducts] = useState<Product[] | null>(null);
  const [qty, setQty] = useState<Record<string, number>>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchActiveProducts()
      .then(setProducts)
      .catch(() => setProducts([]));
  }, []);

  function bump(id: string, delta: number) {
    setQty((q) => {
      const next = Math.max(0, (q[id] ?? 0) + delta);
      return { ...q, [id]: next };
    });
  }

  async function submit() {
    const items = Object.entries(qty)
      .filter(([, n]) => n > 0)
      .map(([product_id, quantity]) => ({ product_id, quantity }));
    if (items.length === 0) {
      Alert.alert("Pick at least one product");
      return;
    }
    setSaving(true);
    try {
      await recordSample(accountId, { items });
      Alert.alert("Sample recorded");
      onDone();
    } catch (e) {
      Alert.alert("Could not record sample", e instanceof Error ? e.message : "Failed");
    } finally {
      setSaving(false);
    }
  }

  if (products === null) return <ActivityIndicator />;
  if (products.length === 0)
    return <Text style={styles.muted}>No active products in the catalog.</Text>;

  return (
    <View style={{ gap: spacing.sm }}>
      {products.map((p) => (
        <View key={p.id} style={styles.row}>
          <Text style={styles.name}>
            {p.name}
            {p.pack_size ? ` (${p.pack_size})` : ""}
          </Text>
          <View style={styles.stepper}>
            <Pressable style={styles.step} onPress={() => bump(p.id, -1)}>
              <Text style={styles.stepText}>−</Text>
            </Pressable>
            <Text style={styles.qty}>{qty[p.id] ?? 0}</Text>
            <Pressable style={styles.step} onPress={() => bump(p.id, 1)}>
              <Text style={styles.stepText}>+</Text>
            </Pressable>
          </View>
        </View>
      ))}
      <Pressable
        style={[styles.submit, saving && { opacity: 0.5 }]}
        onPress={submit}
        disabled={saving}
      >
        <Text style={styles.submitText}>{saving ? "Saving…" : "Record sample"}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  muted: { fontSize: fontSize.sm, color: colors.muted },
  row: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  name: { flex: 1, fontSize: fontSize.base, color: colors.foreground },
  stepper: { flexDirection: "row", alignItems: "center", gap: spacing.md },
  step: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    width: 32,
    height: 32,
    alignItems: "center",
    justifyContent: "center",
  },
  stepText: { fontSize: 18, color: colors.foreground },
  qty: { minWidth: 20, textAlign: "center", fontSize: fontSize.base, color: colors.foreground },
  submit: {
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    paddingVertical: spacing.md,
    alignItems: "center",
    marginTop: spacing.sm,
  },
  submitText: { color: colors.primaryForeground, fontWeight: "600" },
});
