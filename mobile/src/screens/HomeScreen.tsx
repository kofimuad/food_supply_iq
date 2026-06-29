import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import { ActivityIndicator, FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { fetchAccounts } from "../accounts";
import { colors, fontSize, radius, spacing } from "../theme";
import type { Account, User } from "../types";

interface Props {
  user: User;
  onSignOut: () => void;
  onOpenAccount: (id: string) => void;
}

export function HomeScreen({ user, onSignOut, onOpenAccount }: Props) {
  const [accounts, setAccounts] = useState<Account[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAccounts()
      .then((page) => setAccounts(page.items))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, []);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>My accounts</Text>
          <Text style={styles.subtitle}>
            {user.full_name} · {user.role}
          </Text>
        </View>
        <Pressable style={styles.outline} onPress={onSignOut}>
          <Text style={styles.outlineText}>Sign out</Text>
        </Pressable>
      </View>

      {error ? (
        <Text style={styles.error}>{error}</Text>
      ) : accounts === null ? (
        <ActivityIndicator style={{ marginTop: spacing.xl }} />
      ) : accounts.length === 0 ? (
        <Text style={styles.muted}>No accounts assigned to you yet.</Text>
      ) : (
        <FlatList
          data={accounts}
          keyExtractor={(a) => a.id}
          contentContainerStyle={{ gap: spacing.sm, paddingBottom: spacing.xl }}
          renderItem={({ item }) => (
            <Pressable style={styles.card} onPress={() => onOpenAccount(item.id)}>
              <Text style={styles.cardName}>{item.name}</Text>
              <Text style={styles.muted}>
                {item.category} · {item.status}
              </Text>
            </Pressable>
          )}
        />
      )}
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg, paddingTop: 64 },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: spacing.lg,
  },
  title: { fontSize: 24, fontWeight: "600", color: colors.foreground },
  subtitle: { fontSize: fontSize.sm, color: colors.muted },
  muted: { fontSize: fontSize.sm, color: colors.muted },
  error: { color: colors.destructive, fontSize: fontSize.sm },
  card: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: spacing.md,
    gap: 2,
  },
  cardName: { fontSize: fontSize.base, fontWeight: "600", color: colors.foreground },
  outline: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  outlineText: { color: colors.foreground, fontWeight: "600", fontSize: fontSize.sm },
});
