"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import client from "@/lib/api";
import { createClient } from "@/lib/supabase/client";
import type { UserOut } from "@/lib/types";

export interface RegisterResult {
  needsVerification: boolean;
}

interface AuthContextValue {
  user: UserOut | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: {
    username: string;
    email: string;
    password: string;
  }) => Promise<RegisterResult>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// Cached identity so the app can open instantly (and stay open when the API is
// asleep or unreachable) instead of sitting on a full-screen loader.
const USER_CACHE_KEY = "user";
const BOOT_TIMEOUT_MS = 6000;

function readCachedUser(): UserOut | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(USER_CACHE_KEY);
    return raw ? (JSON.parse(raw) as UserOut) : null;
  } catch {
    return null;
  }
}

function cacheUser(user: UserOut | null) {
  if (typeof window === "undefined") return;
  try {
    if (user) window.localStorage.setItem(USER_CACHE_KEY, JSON.stringify(user));
    else window.localStorage.removeItem(USER_CACHE_KEY);
  } catch {
    /* private mode / quota — caching is best-effort */
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const finish = () => {
      if (!cancelled) setLoading(false);
    };

    // 1. Unblock immediately from the cached snapshot. A slow or sleeping
    //    backend must never trap the user behind a loading screen.
    const cached = readCachedUser();
    if (cached) {
      setUser(cached);
      finish();
    }

    // 2. Hard ceiling: even if Supabase or the API hangs, stop blocking.
    const bootTimer = setTimeout(finish, BOOT_TIMEOUT_MS);

    const supabase = createClient();
    supabase.auth
      .getSession()
      .then(({ data }) => {
        const token = data.session?.access_token;
        if (token) localStorage.setItem("token", token);
        const stored = localStorage.getItem("token");
        if (!stored) {
          finish();
          return;
        }
        client
          .get<UserOut>("/auth/me", { timeout: BOOT_TIMEOUT_MS })
          .then((res) => {
            if (cancelled) return;
            setUser(res.data);
            cacheUser(res.data);
          })
          .catch((err) => {
            const status = (err as { response?: { status?: number } })?.response
              ?.status;
            // Only a definitive auth rejection logs the user out. A network
            // error or timeout keeps the cached identity so the site still
            // opens and can recover when the server comes back.
            if (status === 401 || status === 403) {
              localStorage.removeItem("token");
              cacheUser(null);
              if (!cancelled) setUser(null);
              supabase.auth.getSession().then(({ data }) => {
                if (data.session) void supabase.auth.signOut().catch(() => {});
              });
            }
          })
          .finally(finish);
      })
      .catch(finish);

    const { data: sub } = supabase.auth.onAuthStateChange((event, session) => {
      if (session?.access_token) {
        localStorage.setItem("token", session.access_token);
        return;
      }
      // Explicit sign-out (in this tab or another): drop the cached identity
      // too, so the next visit doesn't open with a stale user.
      if (event === "SIGNED_OUT") {
        localStorage.removeItem("token");
        cacheUser(null);
        if (!cancelled) setUser(null);
      }
    });
    return () => {
      cancelled = true;
      clearTimeout(bootTimer);
      sub.subscription.unsubscribe();
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const address = email.trim().toLowerCase();
    if (!address.includes("@")) {
      throw new Error("Log in with your email address.");
    }
    const supabase = createClient();
    const { data, error } = await supabase.auth.signInWithPassword({
      email: address,
      password,
    });
    if (error) throw new Error(error.message);
    if (data.session?.access_token) {
      localStorage.setItem("token", data.session.access_token);
    }
    const me = await client.get<UserOut>("/auth/me");
    setUser(me.data);
    cacheUser(me.data);
  }, []);

  const register = useCallback(
    async (payload: {
      username: string;
      email: string;
      password: string;
    }): Promise<RegisterResult> => {
      const supabase = createClient();
      const { data, error } = await supabase.auth.signUp({
        email: payload.email.trim().toLowerCase(),
        password: payload.password,
        options: { data: { username: payload.username } },
      });
      if (error) throw new Error(error.message);
      if (data.session?.access_token) {
        localStorage.setItem("token", data.session.access_token);
        const me = await client.get<UserOut>("/auth/me");
        setUser(me.data);
        cacheUser(me.data);
        return { needsVerification: false };
      }
      // Email confirmation is on: the account exists, but there is no
      // session until the user clicks the link in their inbox.
      return { needsVerification: true };
    },
    []
  );

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    cacheUser(null);
    setUser(null);
    const supabase = createClient();
    supabase.auth.getSession().then(({ data }) => {
      if (data.session) void supabase.auth.signOut().catch(() => {});
    });
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
