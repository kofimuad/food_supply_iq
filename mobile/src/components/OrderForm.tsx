import { useEffect, useState } from "react";
import { ActivityIndicator, Alert, Pressable, StyleSheet, Text, View } from "react-native";
import { fetchActiveProducts } from "../products";
import { createOrder } from "../sales";
import { colors, fontSize, radius, spacing } from "../theme";
import type { OrderType, Product } from "../types";

interface Props {
  accountId: string;
  orderType: OrderType;
  onDone: () => void;
}

export function OrderForm({ accountId, orderType, onDone }: Props) {
  const [products, setProducts] = useState<Product[] | null>(null);
  const [qty, setQty] = useState<Record<string, number>>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchActiveProducts()
      .then(setProducts)
      .catch(() => setProducts([]));
  }, []);

  function bump(id: string, delta: number) {
    setQty((q) => ({ ...q, [id]: Math.max(0, (q[id] ?? 0) + delta) }));
  }

  const total = (products ?? []).reduce((sum, p) => sum + (qty[p.id] ?? 0) * (p.price ?? 0), 0);
  const currency = products?.find((p) => (qty[p.id] ?? 0) > 0)?.currency ?? "USD";

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
      await createOrder(accountId, { order_type: orderType, items });
      Alert.alert(`${orderType === "trial" ? "Trial" : "Repeat"} order logged`);
      onDone();
    } catch (e) {
      Alert.alert("Could not log order", e instanceof Error ? e.message : "Failed");
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
            {p.price != null ? ` · ${p.price.toFixed(2)} ${p.currency}` : ""}
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
      <Text style={styles.total}>
        Total: {total.toFixed(2)} {currency}
      </Text>
      <Pressable
        style={[styles.submit, saving && { opacity: 0.5 }]}
        onPress={submit}
        disabled={saving}
      >
        <Text style={styles.submitText}>{saving ? "Saving…" : `Log ${orderType} order`}</Text>
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
  total: {
    fontSize: fontSize.base,
    fontWeight: "600",
    color: colors.foreground,
    textAlign: "right",
  },
  submit: {
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    paddingVertical: spacing.md,
    alignItems: "center",
  },
  submitText: { color: colors.primaryForeground, fontWeight: "600" },
});
