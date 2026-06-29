import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import { ActivityIndicator, View } from "react-native";
import { bootstrap, clearTokens } from "./src/auth";
import { AccountProfileScreen } from "./src/screens/AccountProfileScreen";
import { HomeScreen } from "./src/screens/HomeScreen";
import { LoginScreen } from "./src/screens/LoginScreen";
import type { User } from "./src/types";

type AuthStatus = "loading" | "anon" | "authed";
type Route = { name: "home" } | { name: "profile"; accountId: string };

export default function App() {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [user, setUser] = useState<User | null>(null);
  const [route, setRoute] = useState<Route>({ name: "home" });

  useEffect(() => {
    bootstrap().then((u) => {
      setUser(u);
      setStatus(u ? "authed" : "anon");
    });
  }, []);

  function onAuthed(u: User) {
    setUser(u);
    setRoute({ name: "home" });
    setStatus("authed");
  }

  async function onSignOut() {
    await clearTokens();
    setUser(null);
    setStatus("anon");
  }

  if (status === "loading") {
    return (
      <View
        style={{ flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: "#fff" }}
      >
        <ActivityIndicator />
        <StatusBar style="auto" />
      </View>
    );
  }

  if (status !== "authed" || !user) {
    return <LoginScreen onAuthed={onAuthed} />;
  }

  if (route.name === "profile") {
    return (
      <AccountProfileScreen accountId={route.accountId} onBack={() => setRoute({ name: "home" })} />
    );
  }

  return (
    <HomeScreen
      user={user}
      onSignOut={onSignOut}
      onOpenAccount={(accountId) => setRoute({ name: "profile", accountId })}
    />
  );
}
