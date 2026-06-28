"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { apiFetch } from "@/lib/api";
import type { Auction } from "@/lib/types";

function toLocalInputValue(iso: string): string {
  const date = new Date(iso);
  const offsetMs = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

export function EditAuctionForm({ auction }: { auction: Auction }) {
  const router = useRouter();
  const [startingPrice, setStartingPrice] = useState(auction.starting_price);
  const [buyNowPrice, setBuyNowPrice] = useState(auction.buy_now_price ?? "");
  const [endTime, setEndTime] = useState(toLocalInputValue(auction.end_time));
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await apiFetch(`/api/auctions/${auction.id}/`, {
        method: "PATCH",
        body: JSON.stringify({
          starting_price: startingPrice,
          buy_now_price: buyNowPrice || null,
          end_time: new Date(endTime).toISOString(),
        }),
      });
      router.push(`/auctions/${auction.id}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update auction");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <label className="block text-sm">
        <span className="mb-1 block text-parchment/80">Starting price ($)</span>
        <input
          type="number"
          min="0.01"
          step="0.01"
          required
          value={startingPrice}
          onChange={(e) => setStartingPrice(e.target.value)}
          className="w-full rounded border border-gold-dim/40 bg-ink px-3 py-2 text-parchment focus:border-gold focus:outline-none"
        />
      </label>
      <label className="block text-sm">
        <span className="mb-1 block text-parchment/80">Buy now price ($, optional)</span>
        <input
          type="number"
          min="0.01"
          step="0.01"
          value={buyNowPrice}
          onChange={(e) => setBuyNowPrice(e.target.value)}
          className="w-full rounded border border-gold-dim/40 bg-ink px-3 py-2 text-parchment focus:border-gold focus:outline-none"
        />
      </label>
      <label className="block text-sm">
        <span className="mb-1 block text-parchment/80">Ends at</span>
        <input
          type="datetime-local"
          required
          value={endTime}
          onChange={(e) => setEndTime(e.target.value)}
          className="w-full rounded border border-gold-dim/40 bg-ink px-3 py-2 text-parchment focus:border-gold focus:outline-none"
        />
      </label>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded bg-gold py-2 font-medium text-ink hover:bg-gold-bright disabled:opacity-50"
      >
        {submitting ? "Saving…" : "Save changes"}
      </button>
    </form>
  );
}
