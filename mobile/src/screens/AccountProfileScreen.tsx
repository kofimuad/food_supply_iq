import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Linking,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { fetchProfile } from "../accounts";
import { colors, fontSize, radius, spacing } from "../theme";
import type { AccountProfile } from "../types";

interface Props {
  accountId: string;
  onBack: () => void;
}

export function AccountProfileScreen({ accountId, onBack }: Props) {
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProfile(accountId)
      .then(setProfile)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, [accountId]);

  return (
    <View style={styles.container}>
      <Pressable onPress={onBack} style={styles.back}>
        <Text style={styles.backText}>← Accounts</Text>
      </Pressable>

      {error ? (
        <Text style={styles.error}>{error}</Text>
      ) : profile === null ? (
        <ActivityIndicator style={{ marginTop: spacing.xl }} />
      ) : (
        <ScrollView contentContainerStyle={{ gap: spacing.lg, paddingBottom: spacing.xl }}>
          <View>
            <Text style={styles.title}>{profile.account.name}</Text>
            <Text style={styles.muted}>
              {profile.account.category} · {profile.account.status}
            </Text>
            {profile.account.address ? (
              <Text style={styles.muted}>{profile.account.address}</Text>
            ) : null}
          </View>

          <View style={styles.statsRow}>
            <Stat label="Visits" value={profile.summary.visits} />
            <Stat label="Samples" value={profile.summary.samples} />
            <Stat label="Orders" value={profile.summary.orders} />
          </View>

          <Section title={`Contacts (${profile.contacts.length})`}>
            {profile.contacts.length === 0 ? (
              <Text style={styles.muted}>No contacts.</Text>
            ) : (
              profile.contacts.map((c) => (
                <Pressable
                  key={c.id}
                  style={styles.row}
                  onPress={() => c.phone && Linking.openURL(`tel:${c.phone}`)}
                >
                  <Text style={styles.rowName}>
                    {c.name}
                    {c.is_primary ? "  (primary)" : ""}
                  </Text>
                  {c.phone ? <Text style={styles.link}>{c.phone}</Text> : null}
                </Pressable>
              ))
            )}
          </Section>

          <Section title={`Recent visits (${profile.recent_visits.length})`}>
            {profile.recent_visits.length === 0 ? (
              <Text style={styles.muted}>No visits logged yet.</Text>
            ) : (
              profile.recent_visits.map((v) => (
                <View key={v.id} style={styles.row}>
                  <Text style={styles.rowName}>{v.outcome ?? "visit"}</Text>
                  <Text style={styles.muted}>{new Date(v.occurred_at).toLocaleDateString()}</Text>
                </View>
              ))
            )}
          </Section>
        </ScrollView>
      )}
      <StatusBar style="auto" />
    </View>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <View style={styles.stat}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.muted}>{label}</Text>
    </View>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={{ gap: spacing.sm }}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg, paddingTop: 64 },
  back: { marginBottom: spacing.md },
  backText: { color: colors.muted, fontSize: fontSize.sm },
  title: { fontSize: 24, fontWeight: "600", color: colors.foreground },
  muted: { fontSize: fontSize.sm, color: colors.muted },
  error: { color: colors.destructive, fontSize: fontSize.sm },
  statsRow: { flexDirection: "row", gap: spacing.md },
  stat: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: spacing.md,
  },
  statValue: { fontSize: 20, fontWeight: "600", color: colors.foreground },
  sectionTitle: { fontSize: fontSize.base, fontWeight: "600", color: colors.foreground },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: spacing.md,
  },
  rowName: { fontSize: fontSize.base, color: colors.foreground },
  link: { color: colors.foreground, fontWeight: "600", fontSize: fontSize.sm },
});
