import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View } from "react-native";

export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>FoodSupply IQ</Text>
      <Text style={styles.subtitle}>Field Rep app — offline-first</Text>
      <Text style={styles.note}>
        Scaffolding live (Story 0.1). Visits, samples, orders, map &amp; offline sync land in
        Epics 3–7.
      </Text>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    gap: 8,
  },
  title: { fontSize: 28, fontWeight: "600" },
  subtitle: { fontSize: 16, color: "#444" },
  note: { fontSize: 13, color: "#777", textAlign: "center", marginTop: 8 },
});
