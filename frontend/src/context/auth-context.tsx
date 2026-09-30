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

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const supabase = createClient();
    supabase.auth.getSession().then(({ data }) => {
      const token = data.session?.access_token;
      if (token) localStorage.setItem("token", token);
      const stored = localStorage.getItem("token");
      if (!stored) {
        if (!cancelled) setLoading(false);
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
      }
    });
    return () => {
      cancelled = true;
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
