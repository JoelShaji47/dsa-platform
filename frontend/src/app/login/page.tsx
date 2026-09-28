"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import axios from "axios";
import { Brand } from "@/components/shell";
import { useAuth } from "@/context/auth-context";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(identifier, password);
      router.push("/");
    } catch (err) {
      const detail = axios.isAxiosError(err)
        ? err.response?.data?.detail
        : null;
      setError(
        detail === "Incorrect email/username or password"
          ? "That email/username and password combination does not match."
          : detail || "Cannot reach the server. Try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="atlas-bg flex min-h-screen flex-col items-center justify-center px-4 py-12">
      <div className="mb-8">
        <Brand />
      </div>
      <div className="panel w-full max-w-md p-8">
        <p className="eyebrow">Return to the trail</p>
        <h1 className="mt-2 font-display text-3xl font-bold tracking-tight text-ink">
          Welcome back
        </h1>
        <p className="mt-1.5 text-[1.05rem] text-ink-soft">
          Log in to keep your streak alive.
        </p>
        <form onSubmit={handleSubmit} className="mt-7 space-y-5">
          <div>
            <label
              htmlFor="identifier"
              className="mb-1.5 block text-base font-medium text-ink"
            >
              Email or username
            </label>
            <input
              id="identifier"
              type="text"
              required
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              className="field"
              placeholder="you@example.com"
              autoComplete="username"
            />
          </div>
          <div>
            <label
              htmlFor="password"
              className="mb-1.5 block text-base font-medium text-ink"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="field"
              placeholder="Your password"
              autoComplete="current-password"
            />
          </div>
          {error && (
            <p className="rounded-xl border border-rust/30 bg-rust/8 px-4 py-3 text-[0.95rem] text-rust">
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={submitting}
            className="btn btn-ink w-full py-3 text-base"
          >
            {submitting ? "Logging in…" : "Log in"}
          </button>
        </form>
        <p className="mt-6 text-center text-[0.95rem] text-ink-soft">
          New to CodeQuest?{" "}
          <Link
            href="/register"
            className="font-semibold text-gold-deep hover:underline"
          >
            Start your quest
          </Link>
        </p>
      </div>
    </div>
  );
}
