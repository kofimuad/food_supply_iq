import { redirect } from "next/navigation";

export default function Home() {
  // Auth state lives client-side; the dashboard guard bounces anon users to /login.
  redirect("/dashboard");
}
