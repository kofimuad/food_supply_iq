import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { bootstrap, clearTokens, login } from "./src/auth";
import type { User } from "./src/types";

type Status = "loading" | "anon" | "authed";

export default function App() {
  const [status, setStatus] = useState<Status>("loading");
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    bootstrap().then((u) => {
      setUser(u);
      setStatus(u ? "authed" : "anon");
    });
  }, []);

  function onAuthed(u: User) {
    setUser(u);
    setStatus("authed");
  }

  async function onSignOut() {
    await clearTokens();
    setUser(null);
    setStatus("anon");
  }

  if (status === "loading") {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
        <StatusBar style="auto" />
      </View>
    );
  }

  return status === "authed" && user ? (
    <HomeScreen user={user} onSignOut={onSignOut} />
  ) : (
    <LoginScreen onAuthed={onAuthed} />
  );
}

function LoginScreen({ onAuthed }: { onAuthed: (u: User) => void }) {
  const [email, setEmail] = useState("rep.dmv@foodsupplyiq.com");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit() {
    setError(null);
    setSubmitting(true);
    try {
      onAuthed(await login(email.trim(), password));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>FoodSupply IQ</Text>
      <Text style={styles.subtitle}>Field Rep — sign in</Text>
      <TextInput
        style={styles.input}
        value={email}
        onChangeText={setEmail}
        placeholder="Email"
        autoCapitalize="none"
        keyboardType="email-address"
      />
      <TextInput
        style={styles.input}
        value={password}
        onChangeText={setPassword}
        placeholder="Password"
        secureTextEntry
      />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Pressable
        style={[styles.button, submitting && styles.buttonDisabled]}
        onPress={onSubmit}
        disabled={submitting}
      >
        <Text style={styles.buttonText}>{submitting ? "Signing in…" : "Sign in"}</Text>
      </Pressable>
      <StatusBar style="auto" />
    </View>
  );
}

function HomeScreen({ user, onSignOut }: { user: User; onSignOut: () => void }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>FoodSupply IQ</Text>
      <Text style={styles.subtitle}>
        {user.full_name} · {user.role}
      </Text>
      <Text style={styles.note}>
        Signed in as {user.email}. Today&apos;s accounts, visits, samples, orders, map &amp; offline
        sync land in Epics 3–7.
      </Text>
      <Pressable style={styles.buttonOutline} onPress={onSignOut}>
        <Text style={styles.buttonOutlineText}>Sign out</Text>
      </Pressable>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: "#fff" },
  container: {
    flex: 1,
    backgroundColor: "#fff",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    gap: 12,
  },
  title: { fontSize: 28, fontWeight: "600" },
  subtitle: { fontSize: 16, color: "#444" },
  note: { fontSize: 13, color: "#777", textAlign: "center", marginTop: 4 },
  input: {
    width: "100%",
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 15,
  },
  error: { color: "#c0392b", fontSize: 13 },
  button: {
    width: "100%",
    backgroundColor: "#111",
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: "center",
  },
  buttonDisabled: { opacity: 0.5 },
  buttonText: { color: "#fff", fontWeight: "600" },
  buttonOutline: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 20,
    marginTop: 8,
  },
  buttonOutlineText: { color: "#111", fontWeight: "600" },
});
