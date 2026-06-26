"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { apiFetch } from "./api";
import type { TokenPair, User } from "./types";

const ACCESS_KEY = "fsiq_access";
const REFRESH_KEY = "fsiq_refresh";

type Status = "loading" | "authed" | "anon";

interface AuthState {
  user: User | null;
  status: Status;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  /** Fetch against the API with the current access token, retrying once after a refresh. */
  authedFetch: <T>(path: string, options?: RequestInit) => Promise<T>;
}

const AuthContext = createContext<AuthState | null>(null);

function readTokens() {
  if (typeof window === "undefined") return { access: null, refresh: null };
  return {
    access: localStorage.getItem(ACCESS_KEY),
    refresh: localStorage.getItem(REFRESH_KEY),
  };
}

function writeTokens(tokens: TokenPair) {
  localStorage.setItem(ACCESS_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
}

function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<Status>("loading");

  const refreshAccess = useCallback(async (): Promise<string | null> => {
    const { refresh } = readTokens();
    if (!refresh) return null;
    try {
      const tokens = await apiFetch<TokenPair>("/auth/refresh", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refresh }),
      });
      writeTokens(tokens);
      return tokens.access_token;
    } catch {
      clearTokens();
      return null;
    }
  }, []);

  const authedFetch = useCallback(
    async <T,>(path: string, options: RequestInit = {}): Promise<T> => {
      const { access } = readTokens();
      try {
        return await apiFetch<T>(path, options, access);
      } catch (err) {
        if (err instanceof Error && "status" in err && (err as { status: number }).status === 401) {
          const fresh = await refreshAccess();
          if (fresh) return await apiFetch<T>(path, options, fresh);
        }
        throw err;
      }
    },
    [refreshAccess],
  );

  const loadMe = useCallback(async () => {
    try {
      const me = await authedFetch<User>("/auth/me");
      setUser(me);
      setStatus("authed");
    } catch {
      setUser(null);
      setStatus("anon");
    }
  }, [authedFetch]);

  useEffect(() => {
    const { access, refresh } = readTokens();
    if (!access && !refresh) {
      setStatus("anon");
      return;
    }
    void loadMe();
  }, [loadMe]);

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await apiFetch<TokenPair>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    writeTokens(tokens);
    const me = await apiFetch<User>("/auth/me", {}, tokens.access_token);
    setUser(me);
    setStatus("authed");
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
    setStatus("anon");
  }, []);

  return (
    <AuthContext.Provider value={{ user, status, login, logout, authedFetch }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
