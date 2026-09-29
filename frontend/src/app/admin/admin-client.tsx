"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Check,
  Eye,
  EyeOff,
  Loader2,
  Plus,
  Search,
  ShieldCheck,
  Trash2,
  Users,
  X,
  Zap,
} from "lucide-react";
import ProtectedRoute from "@/components/protected-route";
import { TopBar, UserChip } from "@/components/shell";
import { useAuth } from "@/context/auth-context";
import client from "@/lib/api";
import { cn } from "@/lib/utils";

type Tab = "overview" | "problems" | "users";

interface Overview {
  users: number;
  admins: number;
  problems: number;
  published: number;
  solvable: number;
  submissions_7d: number;
}

interface AdminProblem {
  slug: string;
  title: string;
  difficulty: string;
  topic: string;
  pattern_key: string | null;
  is_published: boolean;
  solvable: boolean;
}

interface AdminProblemDetail extends AdminProblem {
  id: string;
  description: string;
  starter_code: Record<string, string>;
  test_cases: { input: string; expected_output: string; is_hidden: boolean }[];
  function_starter: Record<string, string>;
  sources: string[];
  companies: string[];
  editorial_url: string | null;
  video_url: string | null;
}

interface AdminUser {
  id: string;
  username: string;
  email: string;
  xp: number;
  current_streak: number;
  streak_freezes: number;
  league_tier: number;
  is_admin: boolean;
  created_at: string | null;
}

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="panel p-5">
      <p className="eyebrow">{label}</p>
      <p className="mt-2 font-display text-3xl font-bold text-ink">{value}</p>
    </div>
  );
}

function ProblemEditor({
  slug,
  onClose,
  onSaved,
}: {
  slug: string;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [doc, setDoc] = useState<AdminProblemDetail | null>(null);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [lang, setLang] = useState("python");

  useEffect(() => {
    client
      .get<AdminProblemDetail>(`/admin/problems/${slug}`)
      .then((res) => setDoc(res.data))
      .catch(() => setMsg("Couldn't load this problem."));
  }, [slug]);

  const set = (patch: Partial<AdminProblemDetail>) =>
    setDoc((d) => (d ? { ...d, ...patch } : d));

  const save = async () => {
    if (!doc) return;
    setSaving(true);
    setMsg(null);
    try {
      const res = await client.patch<AdminProblemDetail>(
        `/admin/problems/${slug}`,
        {
          title: doc.title,
          description: doc.description,
          difficulty: doc.difficulty,
          topic: doc.topic,
          starter_code: doc.starter_code,
          test_cases: doc.test_cases,
          pattern_key: doc.pattern_key,
          companies: doc.companies,
          editorial_url: doc.editorial_url,
          video_url: doc.video_url,
          is_published: doc.is_published,
        }
      );
      setDoc(res.data);
      setMsg("Saved.");
      onSaved();
    } catch (err) {
      setMsg(
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Save failed."
      );
    } finally {
      setSaving(false);
    }
  };

  const togglePublish = async () => {
    if (!doc) return;
    setSaving(true);
    try {
      const res = await client.patch<AdminProblemDetail>(
        `/admin/problems/${slug}`,
        { is_published: !doc.is_published }
      );
      setDoc(res.data);
      onSaved();
    } catch {
      setMsg("Couldn't flip publish state.");
    } finally {
      setSaving(false);
    }
  };

  if (!doc)
    return (
      <div className="flex items-center gap-2 py-10 text-sm text-ink-faint">
        <Loader2 size={15} className="animate-spin" />{" "}
        {msg ?? "Loading problem…"}
      </div>
    );

  const setCase = (
    i: number,
    patch: Partial<AdminProblemDetail["test_cases"][number]>
  ) =>
    set({
      test_cases: doc.test_cases.map((t, j) => (i === j ? { ...t, ...patch } : t)),
    });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <button
          onClick={togglePublish}
          disabled={saving}
          className={cn(
            "btn px-3 py-1.5 text-sm",
            doc.is_published ? "btn-ink" : "btn-quest"
          )}
        >
          {doc.is_published ? <Eye size={14} /> : <EyeOff size={14} />}
          {doc.is_published ? "Published" : "Unpublished"}
        </button>
        <span
          className={cn(
            "rounded-full px-2.5 py-1 font-mono text-[11px]",
            doc.solvable ? "bg-quest/10 text-quest" : "bg-rust/10 text-rust"
          )}
        >
          {doc.solvable ? "solvable" : "shell"}
        </span>
        <button onClick={onClose} className="btn ml-auto border border-ink/12 px-3 py-1.5 text-sm">
          <X size={14} /> Close
        </button>
      </div>

      <label className="block">
        <span className="eyebrow">Title</span>
        <input
          value={doc.title}
          onChange={(e) => set({ title: e.target.value })}
          className="field mt-1"
        />
      </label>
      <label className="block">
        <span className="eyebrow">Description (markdown)</span>
        <textarea
          value={doc.description}
          onChange={(e) => set({ description: e.target.value })}
          rows={8}
          className="field mt-1 font-mono text-[13px]"
        />
      </label>

      <div>
        <div className="flex items-center gap-1">
          {(["python", "cpp", "java"] as const).map((l) => (
            <button
              key={l}
              type="button"
              onClick={() => setLang(l)}
              className={cn(
                "rounded-lg px-3 py-1 font-mono text-xs",
                lang === l ? "bg-ink text-white" : "text-ink-faint hover:text-ink"
              )}
            >
              {l}
            </button>
          ))}
          <span className="ml-auto font-mono text-[11px] text-ink-faint">
            starter · {lang}
          </span>
        </div>
        <textarea
          value={doc.starter_code[lang] ?? ""}
          onChange={(e) =>
            set({ starter_code: { ...doc.starter_code, [lang]: e.target.value } })
          }
          rows={10}
          spellCheck={false}
          className="field mt-1 font-mono text-[13px]"
        />
      </div>

      <div>
        <div className="flex items-center">
          <span className="eyebrow">Test cases ({doc.test_cases.length})</span>
          <button
            type="button"
            onClick={() =>
              set({
                test_cases: [
                  ...doc.test_cases,
                  { input: "", expected_output: "", is_hidden: true },
                ],
              })
            }
            className="btn ml-auto border border-ink/12 px-2.5 py-1 text-xs"
          >
            <Plus size={12} /> Add case
          </button>
        </div>
        <div className="mt-2 space-y-2">
          {doc.test_cases.map((t, i) => (
            <div
              key={i}
              className="grid grid-cols-1 gap-2 rounded-xl border border-ink/10 bg-paper p-3 sm:grid-cols-[1fr_1fr_auto]"
            >
              <textarea
                value={t.input}
                onChange={(e) => setCase(i, { input: e.target.value })}
                rows={3}
                placeholder="stdin"
                className="field font-mono text-xs"
              />
              <textarea
                value={t.expected_output}
                onChange={(e) => setCase(i, { expected_output: e.target.value })}
                rows={3}
                placeholder="expected stdout"
                className="field font-mono text-xs"
              />
              <div className="flex flex-row gap-1 sm:flex-col">
                <button
                  type="button"
                  title="Toggle hidden"
                  onClick={() => setCase(i, { is_hidden: !t.is_hidden })}
                  className={cn(
                    "rounded-lg border px-2 py-1 font-mono text-[11px]",
                    t.is_hidden
                      ? "border-gold/50 bg-gold/10 text-gold-deep"
                      : "border-ink/10 text-ink-faint"
                  )}
                >
                  {t.is_hidden ? "hidden" : "visible"}
                </button>
                <button
                  type="button"
                  title="Delete case"
                  onClick={() =>
                    set({ test_cases: doc.test_cases.filter((_, j) => j !== i) })
                  }
                  className="rounded-lg border border-ink/10 px-2 py-1 text-rust"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <label className="block">
          <span className="eyebrow">Editorial URL</span>
          <input
            value={doc.editorial_url ?? ""}
            onChange={(e) => set({ editorial_url: e.target.value || null })}
            className="field mt-1 text-sm"
          />
        </label>
        <label className="block">
          <span className="eyebrow">Video URL</span>
          <input
            value={doc.video_url ?? ""}
            onChange={(e) => set({ video_url: e.target.value || null })}
            className="field mt-1 text-sm"
          />
        </label>
      </div>

      <div className="flex items-center gap-3">
        <button onClick={save} disabled={saving} className="btn btn-quest px-5 py-2.5">
          {saving ? <Loader2 size={15} className="animate-spin" /> : <Check size={15} />}
          Save problem
        </button>
        {msg && <span className="text-sm text-ink-soft">{msg}</span>}
      </div>
    </div>
  );
}

export default function AdminClient() {
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>("overview");
  const [overview, setOverview] = useState<Overview | null>(null);
  const [problems, setProblems] = useState<AdminProblem[]>([]);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "shells" | "unpublished">("all");
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState<string | null>(null);
  const [denied, setDenied] = useState(false);

  const loadOverview = makeOverviewLoader("/admin/overview", setOverview, setDenied);
  const loadProblems = useCallback(() => {
    setLoading(true);
    const params: Record<string, string> = {};
    if (search) params.search = search;
    if (filter === "unpublished") params.published = "false";
    client
      .get<{ items: AdminProblem[] }>("/admin/problems", { params })
      .then((res) => {
        const items =
          filter === "shells"
            ? res.data.items.filter((p) => !p.solvable)
            : res.data.items;
        setProblems(items);
      })
      .catch((err) => {
        if (err?.response?.status === 403) setDenied(true);
      })
      .finally(() => setLoading(false));
  }, [search, filter]);
  const loadUsers = makeUsersLoader("/admin/users", search, setUsers, setDenied);

  useEffect(() => {
    loadOverview();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => {
    if (tab === "problems") loadProblems();
    if (tab === "users") loadUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab]);

  if (denied)
    return (
      <ProtectedRoute>
        <div className="atlas-bg flex min-h-screen items-center justify-center px-6 text-center">
          <div>
            <ShieldCheck size={36} className="mx-auto text-ink-faint" />
            <h1 className="mt-3 font-display text-2xl font-bold text-ink">
              Admins only
            </h1>
            <p className="mt-1 text-ink-soft">
              Your account doesn&apos;t have admin access.
            </p>
          </div>
        </div>
      </ProtectedRoute>
    );

  return (
    <ProtectedRoute>
      <div className="atlas-bg min-h-screen">
        <TopBar active="dashboard">
          {user && <UserChip username={user.username} />}
        </TopBar>
        <main className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6">
          <div className="flex flex-wrap items-end gap-3">
            <div>
              <p className="eyebrow">Control plane</p>
              <h1 className="mt-1 font-display text-3xl font-bold tracking-tight text-ink">
                Admin
              </h1>
            </div>
            <div className="ml-auto flex gap-1 rounded-xl border border-ink/10 bg-card p-1 shadow-card">
              {(["overview", "problems", "users"] as const).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setTab(t)}
                  className={cn(
                    "rounded-lg px-4 py-1.5 text-sm font-semibold capitalize transition-colors",
                    tab === t ? "bg-ink text-white" : "text-ink-soft hover:text-ink"
                  )}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {tab === "overview" && (
            <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-3">
              <Stat label="Users" value={overview?.users ?? "—"} />
              <Stat label="Problems" value={overview?.problems ?? "—"} />
              <Stat label="Published" value={overview?.published ?? "—"} />
              <Stat label="Solvable" value={overview?.solvable ?? "—"} />
              <Stat label="Submits / 7d" value={overview?.submissions_7d ?? "—"} />
              <Stat label="Admins" value={overview?.admins ?? "—"} />
            </div>
          )}

          {tab === "problems" && (
            <div className="mt-6 space-y-4">
              <div className="flex flex-col gap-2 sm:flex-row">
                <div className="relative flex-1">
                  <Search
                    size={15}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint"
                  />
                  <input
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && loadProblems()}
                    placeholder="Search title or slug…"
                    className="field pl-9"
                  />
                </div>
                <div className="flex gap-1 rounded-xl border border-ink/10 bg-card p-1">
                  {(["all", "shells", "unpublished"] as const).map((f) => (
                    <button
                      key={f}
                      type="button"
                      onClick={() => setFilter(f)}
                      className={cn(
                        "rounded-lg px-3 py-1.5 text-sm font-semibold capitalize",
                        filter === f ? "bg-ink text-white" : "text-ink-soft"
                      )}
                    >
                      {f}
                    </button>
                  ))}
                </div>
                <button onClick={loadProblems} className="btn btn-ink px-4 py-2 text-sm">
                  Search
                </button>
              </div>

              {editing ? (
                <div className="panel p-5">
                  <ProblemEditor
                    slug={editing}
                    onClose={() => setEditing(null)}
                    onSaved={loadProblems}
                  />
                </div>
              ) : (
                <div className="panel overflow-hidden">
                  {loading ? (
                    <div className="flex items-center justify-center gap-2 py-12 text-sm text-ink-faint">
                      <Loader2 size={15} className="animate-spin" /> Loading…
                    </div>
                  ) : (
                    <ul className="divide-y divide-ink/8">
                      {problems.map((p) => (
                        <li key={p.slug}>
                          <button
                            type="button"
                            onClick={() => setEditing(p.slug)}
                            className="flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-ink/[0.03] sm:px-5"
                          >
                            <span
                              className={cn(
                                "h-2.5 w-2.5 shrink-0 rounded-full",
                                p.is_published ? "bg-quest" : "bg-ink/20"
                              )}
                              title={p.is_published ? "Published" : "Unpublished"}
                            />
                            <span className="min-w-0 flex-1">
                              <span className="block truncate text-sm font-medium text-ink">
                                {p.title}
                              </span>
                              <span className="block truncate font-mono text-[11px] text-ink-faint">
                                {p.slug} · {p.topic} · {p.difficulty}
                              </span>
                            </span>
                            {!p.solvable && (
                              <span className="hidden rounded-full bg-rust/10 px-2 py-0.5 font-mono text-[10px] uppercase text-rust sm:inline">
                                shell
                              </span>
                            )}
                            <span className="shrink-0 font-mono text-[11px] text-ink-faint">
                              Edit →
                            </span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          )}

          {tab === "users" && (
            <>
              <div className="mt-6 flex gap-2">
                <div className="relative flex-1">
                  <Search
                    size={15}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint"
                  />
                  <input
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && loadUsers()}
                    placeholder="Search username or email…"
                    className="field pl-9"
                  />
                </div>
                <button onClick={loadUsers} className="btn btn-ink px-4 py-2 text-sm">
                  Search
                </button>
              </div>
              <UsersTab users={users} onChanged={loadUsers} />
            </>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}

function makeOverviewLoader(
  url: string,
  set: (v: Overview | null) => void,
  setDenied: (v: boolean) => void
) {
  const load = () => {
    client
      .get<Overview>(url)
      .then((res) => set(res.data))
      .catch((err) => {
        if (err?.response?.status === 403) setDenied(true);
      });
  };
  return load;
}

function makeUsersLoader(
  url: string,
  search: string,
  set: (v: AdminUser[]) => void,
  setDenied: (v: boolean) => void
) {
  const load = () => {
    client
      .get<{ items: AdminUser[] }>(url, { params: search ? { search } : {} })
      .then((res) => set(res.data.items))
      .catch((err) => {
        if (err?.response?.status === 403) setDenied(true);
      });
  };
  return load;
}

function UsersTab({ users, onChanged }: { users: AdminUser[]; onChanged: () => void }) {
  const [granting, setGranting] = useState<string | null>(null);
  const [amount, setAmount] = useState("50");

  const toggleAdmin = async (u: AdminUser) => {
    await client.patch(`/admin/users/${u.id}`, { is_admin: !u.is_admin });
    onChanged();
  };

  const grant = async (u: AdminUser) => {
    setGranting(u.id);
    try {
      await client.patch(`/admin/users/${u.id}`, { grant_xp: Number(amount) || 0 });
      onChanged();
    } finally {
      setGranting(null);
    }
  };

  return (
    <div className="panel mt-6 overflow-hidden">
      <div className="flex items-center gap-2 border-b border-ink/10 px-4 py-3 sm:px-5">
        <Users size={14} className="text-ink-faint" />
        <span className="font-mono text-xs text-ink-faint">{users.length} shown</span>
        <span className="ml-auto flex items-center gap-2">
          <Zap size={13} className="text-gold-deep" />
          <input
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-20 rounded-lg border border-ink/10 bg-paper px-2 py-1 font-mono text-xs"
          />
        </span>
      </div>
      <ul className="divide-y divide-ink/8">
        {users.map((u) => (
          <li
            key={u.id}
            className="flex flex-col gap-2 px-4 py-3 sm:flex-row sm:items-center sm:px-5"
          >
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-ink">
                {u.username}
                {u.is_admin && (
                  <span className="ml-2 rounded-full bg-gold/15 px-2 py-0.5 font-mono text-[10px] font-semibold uppercase text-gold-deep">
                    admin
                  </span>
                )}
              </p>
              <p className="truncate font-mono text-[11px] text-ink-faint">
                {u.email} · {u.xp} XP · {u.current_streak}d streak · {u.streak_freezes} freezes
              </p>
            </div>
            <div className="flex shrink-0 gap-2">
              <button
                onClick={() => toggleAdmin(u)}
                className="btn border border-ink/12 px-3 py-1.5 text-xs"
              >
                <ShieldCheck size={13} />
                {u.is_admin ? "Demote" : "Promote"}
              </button>
              <button
                onClick={() => grant(u)}
                disabled={granting === u.id}
                className="btn btn-quest px-3 py-1.5 text-xs"
              >
                {granting === u.id ? (
                  <Loader2 size={13} className="animate-spin" />
                ) : (
                  <Zap size={13} />
                )}
                Grant XP
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
