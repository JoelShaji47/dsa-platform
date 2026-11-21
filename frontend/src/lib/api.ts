import axios, { isAxiosError } from "axios";
import { onError } from "@/context/toast-context";

const client = axios.create({
  baseURL: "/api/v1",
  // Fail fast so a sleeping/offline backend surfaces an error instead of
  // leaving the UI waiting for minutes. Longer operations (Judge0 run/submit,
  // tutor) pass an explicit per-request timeout.
  timeout: 20000,
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

// On 401, redirect to login (no Supabase session refresh needed). Any other
// failure is surfaced as a toast so users are never left guessing.
client.interceptors.response.use(
  (res) => res,
  (error) => {
    if (
      typeof window !== "undefined" &&
      isAxiosError(error) &&
      error.response?.status === 401 &&
      !window.location.pathname.startsWith("/login")
    ) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
      return Promise.reject(error);
    }
    const msg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "Request failed.";
    if (typeof window !== "undefined" && onError) {
      onError(msg);
    }
    return Promise.reject(error);
  }
);

export default client;
