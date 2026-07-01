"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { ActivityFeed } from "@/components/activity-feed";
import { KpiDashboard } from "@/components/kpi-dashboard";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/lib/auth-context";

export default function DashboardPage() {
  const { user, status, logout } = useAuth();
  const router = useRouter();

  // Client-side route guard.
  useEffect(() => {
    if (status === "anon") router.replace("/login");
  }, [status, router]);

  if (status !== "authed" || !user) {
    return (
      <main className="container mx-auto flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted-foreground">Loading…</p>
      </main>
    );
  }

  return (
    <main className="container mx-auto flex min-h-screen flex-col gap-6 py-12">
      <header className="flex items-center justify-between border-b pb-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">FoodSupply IQ</h1>
          <p className="text-sm text-muted-foreground">Manager dashboard</p>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-muted-foreground">
            {user.full_name} · <span className="font-medium">{user.role}</span>
          </span>
          <Button variant="outline" size="sm" onClick={logout}>
            Sign out
          </Button>
        </div>
      </header>

      <nav className="flex gap-3">
        <Link href="/accounts">
          <Button variant="outline">Accounts</Button>
        </Link>
        <Link href="/products">
          <Button variant="outline">Product catalog</Button>
        </Link>
        <Link href="/map">
          <Button variant="outline">Map</Button>
        </Link>
        {user.role === "manager" && (
          <Link href="/funnel">
            <Button variant="outline">Funnel</Button>
          </Link>
        )}
      </nav>

      {user.role === "manager" ? (
        <>
          <KpiDashboard />
          <ActivityFeed />
        </>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">
              Signed in as <span className="font-medium text-foreground">{user.email}</span>.
            </p>
          </CardContent>
        </Card>
      )}
    </main>
  );
}
