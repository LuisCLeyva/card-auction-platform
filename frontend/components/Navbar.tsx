"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api";
import { useCurrentUser } from "@/lib/auth";

export function Navbar() {
  const { user, loading, setUser } = useCurrentUser();
  const router = useRouter();

  async function handleLogout() {
    await apiFetch("/api/auth/logout/", { method: "POST" });
    setUser(null);
    router.push("/");
    router.refresh();
  }

  return (
    <header className="border-b border-gold-dim/30 bg-ink-light/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link href="/" className="font-display text-xl tracking-wide text-gold-bright">
          ⚔ Card Auction House
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link href="/" className="hover:text-gold">
            Auctions
          </Link>
          {!loading && user && (
            <>
              <Link href="/dashboard" className="hover:text-gold">
                Dashboard
              </Link>
              <Link href="/dashboard/cards" className="hover:text-gold">
                My Cards
              </Link>
              <span className="text-parchment/60">{user.display_name}</span>
              <button
                onClick={handleLogout}
                className="rounded border border-gold-dim px-3 py-1 hover:border-gold hover:text-gold"
              >
                Logout
              </button>
            </>
          )}
          {!loading && !user && (
            <>
              <Link href="/login" className="hover:text-gold">
                Login
              </Link>
              <Link
                href="/register"
                className="rounded bg-gold px-3 py-1 font-medium text-ink hover:bg-gold-bright"
              >
                Register
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
