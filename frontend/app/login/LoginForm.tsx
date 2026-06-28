"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import { Field } from "@/components/Field";
import { apiFetch } from "@/lib/api";
import { useCurrentUser, type CurrentUser } from "@/lib/auth";

export function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const { setUser } = useCurrentUser();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await apiFetch("/api/auth/login/", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      const me = await apiFetch<CurrentUser>("/api/auth/me/");
      setUser(me);
      router.push(params.get("next") ?? "/dashboard");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm">
      <h1 className="mb-6 font-display text-2xl text-gold-bright">Sign in</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Email" type="email" value={email} onChange={setEmail} required />
        <Field label="Password" type="password" value={password} onChange={setPassword} required />
        {error && <p className="text-sm text-red-400">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded bg-gold py-2 font-medium text-ink hover:bg-gold-bright disabled:opacity-50"
        >
          {submitting ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <p className="mt-4 text-sm text-parchment/60">
        No account?{" "}
        <Link href="/register" className="text-gold hover:underline">
          Register
        </Link>
      </p>
    </div>
  );
}
