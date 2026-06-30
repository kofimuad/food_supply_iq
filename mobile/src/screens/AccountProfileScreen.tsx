import * as ImagePicker from "expo-image-picker";
import * as Location from "expo-location";
import { StatusBar } from "expo-status-bar";
import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Linking,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { changeStatus, fetchProfile, logVisit } from "../accounts";
import { uploadPhoto } from "../media";
import { colors, fontSize, radius, spacing } from "../theme";
import type { AccountProfile, AccountStatus, VisitOutcome } from "../types";

const STATUSES: AccountStatus[] = [
  "lead",
  "in_discussion",
  "sampled",
  "trial",
  "repeat",
  "not_interested",
];

const OUTCOMES: VisitOutcome[] = [
  "interested",
  "not_interested",
  "sample_given",
  "order_placed",
  "follow_up_needed",
  "no_contact",
];

/** Best-effort GPS: returns coords if permission is granted, else null. */
async function getCoords(): Promise<{ lat: number; lng: number } | null> {
  try {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== "granted") return null;
    const pos = await Location.getCurrentPositionAsync({});
    return { lat: pos.coords.latitude, lng: pos.coords.longitude };
  } catch {
    return null;
  }
}

interface Props {
  accountId: string;
  onBack: () => void;
}

export function AccountProfileScreen({ accountId, onBack }: Props) {
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [outcome, setOutcome] = useState<VisitOutcome | null>(null);
  const [notes, setNotes] = useState("");
  const [checkingIn, setCheckingIn] = useState(false);

  const load = useCallback(() => {
    fetchProfile(accountId)
      .then(setProfile)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, [accountId]);

  useEffect(load, [load]);

  async function onCheckIn() {
    setCheckingIn(true);
    try {
      const coords = await getCoords();
      await logVisit(accountId, {
        notes: notes.trim() || null,
        outcome,
        lat: coords?.lat ?? null,
        lng: coords?.lng ?? null,
      });
      setNotes("");
      setOutcome(null);
      load();
      Alert.alert("Visit logged", coords ? "Captured your location." : "Logged without location.");
    } catch (e) {
      Alert.alert("Could not log visit", e instanceof Error ? e.message : "Failed");
    } finally {
      setCheckingIn(false);
    }
  }

  async function onAddPhoto(visitId: string) {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) {
      Alert.alert("Permission needed", "Allow photo access to attach a photo.");
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({ quality: 0.5 });
    if (result.canceled) return;
    const asset = result.assets[0];
    try {
      await uploadPhoto(visitId, asset.uri, asset.mimeType ?? "image/jpeg");
      Alert.alert("Photo attached");
    } catch (e) {
      Alert.alert("Upload failed", e instanceof Error ? e.message : "Try again");
    }
  }

  function onChangeStatus(status: AccountStatus) {
    Alert.alert("Change status", `Move this account to "${status}"?`, [
      { text: "Cancel", style: "cancel" },
      {
        text: "Confirm",
        onPress: () =>
          changeStatus(accountId, status)
            .then(load)
            .catch((e) =>
              Alert.alert("Could not change status", e instanceof Error ? e.message : "Failed"),
            ),
      },
    ]);
  }

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

          <Section title="Change status">
            <View style={styles.statusRow}>
              {STATUSES.filter((s) => s !== profile.account.status).map((s) => (
                <Pressable key={s} style={styles.statusChip} onPress={() => onChangeStatus(s)}>
                  <Text style={styles.statusChipText}>{s}</Text>
                </Pressable>
              ))}
            </View>
          </Section>

          <Section title="Log a visit">
            <View style={styles.statusRow}>
              {OUTCOMES.map((o) => (
                <Pressable
                  key={o}
                  style={[styles.statusChip, outcome === o && styles.statusChipActive]}
                  onPress={() => setOutcome(outcome === o ? null : o)}
                >
                  <Text
                    style={[styles.statusChipText, outcome === o && styles.statusChipTextActive]}
                  >
                    {o}
                  </Text>
                </Pressable>
              ))}
            </View>
            <TextInput
              style={styles.input}
              value={notes}
              onChangeText={setNotes}
              placeholder="Notes (optional)"
              multiline
            />
            <Pressable
              style={[styles.checkIn, checkingIn && { opacity: 0.5 }]}
              onPress={onCheckIn}
              disabled={checkingIn}
            >
              <Text style={styles.checkInText}>
                {checkingIn ? "Checking in…" : "Check in with GPS"}
              </Text>
            </Pressable>
          </Section>

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
                  <View>
                    <Text style={styles.rowName}>{v.outcome ?? "visit"}</Text>
                    <Text style={styles.muted}>{new Date(v.occurred_at).toLocaleDateString()}</Text>
                  </View>
                  <Pressable onPress={() => onAddPhoto(v.id)}>
                    <Text style={styles.link}>+ Photo</Text>
                  </Pressable>
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
  statusRow: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  statusChip: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  statusChipText: { color: colors.foreground, fontSize: fontSize.sm },
  statusChipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  statusChipTextActive: { color: colors.primaryForeground },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: spacing.md,
    fontSize: fontSize.base,
    minHeight: 44,
  },
  checkIn: {
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    paddingVertical: spacing.md,
    alignItems: "center",
  },
  checkInText: { color: colors.primaryForeground, fontWeight: "600" },
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
