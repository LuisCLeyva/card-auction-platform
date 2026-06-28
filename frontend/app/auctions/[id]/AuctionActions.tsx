"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { apiFetch } from "@/lib/api";
import type { Auction } from "@/lib/types";

interface AuctionActionsProps {
  auction: Auction;
  isOwner: boolean;
  isLoggedIn: boolean;
}

export function AuctionActions({ auction, isOwner, isLoggedIn }: AuctionActionsProps) {
  const router = useRouter();
  const [amount, setAmount] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const minBid = auction.highest_bid
    ? Number(auction.highest_bid.amount) + Number(auction.min_increment)
    : Number(auction.starting_price);

  async function placeBid(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await apiFetch(`/api/auctions/${auction.id}/bid/`, {
        method: "POST",
        body: JSON.stringify({ amount }),
      });
      setAmount("");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Bid failed");
    } finally {
      setBusy(false);
    }
  }

  async function buyNow() {
    if (!confirm(`Buy now for $${auction.buy_now_price}?`)) return;
    setBusy(true);
    setError(null);
    try {
      await apiFetch(`/api/auctions/${auction.id}/buy-now/`, { method: "POST" });
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Buy now failed");
    } finally {
      setBusy(false);
    }
  }

  async function cancelAuction() {
    if (!confirm("Cancel this auction?")) return;
    setBusy(true);
    setError(null);
    try {
      await apiFetch(`/api/auctions/${auction.id}/cancel/`, { method: "POST" });
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cancel failed");
    } finally {
      setBusy(false);
    }
  }

  if (auction.status !== "ACTIVE") {
    return (
      <p className="text-sm text-parchment/60">
        This auction has ended ({auction.status.toLowerCase()}).
      </p>
    );
  }

  if (isOwner) {
    return (
      <div className="space-y-2">
        {!auction.highest_bid ? (
          <div className="flex gap-3">
            <Link
              href={`/auctions/${auction.id}/edit`}
              className="rounded border border-gold-dim px-4 py-2 text-sm hover:border-gold hover:text-gold"
            >
              Edit
            </Link>
            <button
              onClick={cancelAuction}
              disabled={busy}
              className="rounded border border-red-800 px-4 py-2 text-sm text-red-400 hover:border-red-500"
            >
              Cancel auction
            </button>
          </div>
        ) : (
          <p className="text-sm text-parchment/60">
            Bids have been placed — this auction can no longer be edited or cancelled.
          </p>
        )}
        {error && <p className="text-sm text-red-400">{error}</p>}
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <p className="text-sm text-parchment/60">
        <Link href="/login" className="text-gold hover:underline">
          Sign in
        </Link>{" "}
        to bid on this auction.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      <form onSubmit={placeBid} className="flex gap-2">
        <input
          type="number"
          step="0.01"
          min={minBid}
          required
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder={`$${minBid.toFixed(2)} or more`}
          className="flex-1 rounded border border-gold-dim/40 bg-ink px-3 py-2 text-parchment focus:border-gold focus:outline-none"
        />
        <button
          type="submit"
          disabled={busy}
          className="rounded bg-gold px-4 py-2 font-medium text-ink hover:bg-gold-bright disabled:opacity-50"
        >
          Bid
        </button>
      </form>
      {auction.buy_now_price && (
        <button
          onClick={buyNow}
          disabled={busy}
          className="w-full rounded border border-gold-bright py-2 text-sm text-gold-bright hover:bg-gold-bright hover:text-ink"
        >
          Buy now for ${auction.buy_now_price}
        </button>
      )}
      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  );
}
