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

interface AuthContextValue {
  user: UserOut | null;
  loading: boolean;
  login: (identifier: string, password: string) => Promise<void>;
  register: (payload: {
    username: string;
    email: string;
    password: string;
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function supabaseErr(err: unknown): string | null {
  if (typeof err === "object" && err !== null && "message" in err) {
    const m = String((err as { message: unknown }).message);
    return m || null;
  }
  return null;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const supabase = createClient();
    supabase.auth.getSession().then(({ data }) => {
      const token = data.session?.access_token;
      if (token) localStorage.setItem("token", token);
      // Legacy local tokens (pre-Supabase) keep working via backend fallback.
      const stored = localStorage.getItem("token");
      if (!stored) {
        void Promise.resolve().then(() => {
          if (!cancelled) setLoading(false);
        });
        return;
      }
      client
        .get<UserOut>("/auth/me")
        .then((res) => {
          if (!cancelled) setUser(res.data);
        })
        .catch(() => {
          localStorage.removeItem("token");
          void supabase.auth.signOut();
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.access_token) {
        localStorage.setItem("token", session.access_token);
      } else if (!localStorage.getItem("token")) {
        // keep legacy token until explicit logout
      }
    });
    return () => {
      cancelled = true;
      sub.subscription.unsubscribe();
    };
  }, []);

  const login = useCallback(async (identifier: string, password: string) => {
    // Supabase signs in by email; legacy usernames fall back to local /auth/login.
    const supabase = createClient();
    if (identifier.includes("@")) {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: identifier,
        password,
      });
      if (error) throw new Error(error.message);
      if (data.session?.access_token) {
        localStorage.setItem("token", data.session.access_token);
      }
    } else {
      const form = new URLSearchParams();
      form.append("username", identifier);
      form.append("password", password);
      const res = await client.post<{ access_token: string }>(
        "/auth/login",
        form,
        { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
      );
      localStorage.setItem("token", res.data.access_token);
    }
    const me = await client.get<UserOut>("/auth/me");
    setUser(me.data);
  }, []);

  const register = useCallback(
    async (payload: { username: string; email: string; password: string }) => {
      const supabase = createClient();
      const { data, error } = await supabase.auth.signUp({
        email: payload.email,
        password: payload.password,
        options: { data: { username: payload.username } },
      });
      if (error) {
        // "already registered" → try legacy login-shape fallback below.
        throw new Error(supabaseErr(error) || "Sign-up failed. Try again.");
      }
      if (data.session?.access_token) {
        localStorage.setItem("token", data.session.access_token);
        const me = await client.get<UserOut>("/auth/me");
        setUser(me.data);
        return;
      }
      // No session (email confirmation on): fall back to legacy register so
      // the user can log in immediately with a local account.
      await client.post("/auth/register", payload);
    },
    []
  );

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setUser(null);
    void createClient().auth.signOut();
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
