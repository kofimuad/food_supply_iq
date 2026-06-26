import * as SecureStore from "expo-secure-store";
import { apiFetch, ApiError } from "./api";
import type { TokenPair, User } from "./types";

// Tokens live in the OS keychain/keystore via expo-secure-store, so they
// survive app restarts — the rep stays signed in across an offline field day.
const ACCESS_KEY = "fsiq_access";
const REFRESH_KEY = "fsiq_refresh";

export async function saveTokens(tokens: TokenPair): Promise<void> {
  await SecureStore.setItemAsync(ACCESS_KEY, tokens.access_token);
  await SecureStore.setItemAsync(REFRESH_KEY, tokens.refresh_token);
}

export async function clearTokens(): Promise<void> {
  await SecureStore.deleteItemAsync(ACCESS_KEY);
  await SecureStore.deleteItemAsync(REFRESH_KEY);
}

async function refreshAccess(): Promise<string | null> {
  const refresh = await SecureStore.getItemAsync(REFRESH_KEY);
  if (!refresh) return null;
  try {
    const tokens = await apiFetch<TokenPair>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refresh }),
    });
    await saveTokens(tokens);
    return tokens.access_token;
  } catch {
    await clearTokens();
    return null;
  }
}

/** Fetch with the stored access token, retrying once after a refresh on 401. */
export async function authedFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const access = await SecureStore.getItemAsync(ACCESS_KEY);
  try {
    return await apiFetch<T>(path, options, access);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      const fresh = await refreshAccess();
      if (fresh) return apiFetch<T>(path, options, fresh);
    }
    throw err;
  }
}

export async function login(email: string, password: string): Promise<User> {
  const tokens = await apiFetch<TokenPair>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  await saveTokens(tokens);
  return apiFetch<User>("/auth/me", {}, tokens.access_token);
}

/** On app start: return the current user if a valid token exists, else null. */
export async function bootstrap(): Promise<User | null> {
  const access = await SecureStore.getItemAsync(ACCESS_KEY);
  const refresh = await SecureStore.getItemAsync(REFRESH_KEY);
  if (!access && !refresh) return null;
  try {
    return await authedFetch<User>("/auth/me");
  } catch {
    return null;
  }
}
