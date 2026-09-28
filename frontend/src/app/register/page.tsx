"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import axios from "axios";
import { Brand } from "@/components/shell";
import { useAuth } from "@/context/auth-context";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const update = (field: keyof typeof form) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(form);
      router.push("/login");
    } catch (err) {
      setError(
        (axios.isAxiosError(err) && err.response?.data?.detail) ||
          "Registration failed."
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
        <p className="eyebrow">Begin the expedition</p>
        <h1 className="mt-2 font-display text-3xl font-bold tracking-tight text-ink">
          Create your account
        </h1>
        <p className="mt-1.5 text-[1.05rem] text-ink-soft">
          Solve problems, earn XP, build streaks.
        </p>
        <form onSubmit={handleSubmit} className="mt-7 space-y-5">
          <div>
            <label
              htmlFor="username"
              className="mb-1.5 block text-base font-medium text-ink"
            >
              Username
            </label>
            <input
              id="username"
              type="text"
              required
              minLength={3}
              maxLength={30}
              pattern="[a-zA-Z0-9_]+"
              title="3–30 characters, letters, numbers, underscores only"
              value={form.username}
              onChange={update("username")}
              className="field"
              placeholder="pathfinder_01"
              autoComplete="username"
            />
          </div>
          <div>
            <label
              htmlFor="email"
              className="mb-1.5 block text-base font-medium text-ink"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={form.email}
              onChange={update("email")}
              className="field"
              placeholder="you@example.com"
              autoComplete="email"
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
              minLength={8}
              value={form.password}
              onChange={update("password")}
              className="field"
              placeholder="At least 8 characters"
              autoComplete="new-password"
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
            {submitting ? "Creating account…" : "Create account"}
          </button>
        </form>
        <p className="mt-6 text-center text-[0.95rem] text-ink-soft">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-semibold text-gold-deep hover:underline"
          >
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
