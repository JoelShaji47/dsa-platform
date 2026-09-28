import axios from "axios";
import { createClient } from "./supabase/client";

const client = axios.create({
  baseURL: "/api/v1",
  timeout: 30000,
});

client.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// On 401, try one silent Supabase session refresh before giving up.
// Legacy local tokens have no Supabase session, so they fall straight
// through to logout + login redirect.
client.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error?.config as
      | (typeof error.config & { _retried?: boolean })
      | undefined;
    if (
      typeof window === "undefined" ||
      !axios.isAxiosError(error) ||
      error.response?.status !== 401 ||
      !original ||
      original._retried
    ) {
      return Promise.reject(error);
    }
    original._retried = true;
    try {
      const supabase = createClient();
      const { data, error: refreshError } = await supabase.auth.refreshSession();
      const token = data.session?.access_token;
      if (refreshError || !token) throw refreshError ?? new Error("no session");
      localStorage.setItem("token", token);
      original.headers.Authorization = `Bearer ${token}`;
      return client(original);
    } catch {
      localStorage.removeItem("token");
      try {
        await createClient().auth.signOut();
      } catch {
      }
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
      return Promise.reject(error);
    }
  }
);

export default client;
