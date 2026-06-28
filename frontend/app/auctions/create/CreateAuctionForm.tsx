"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { apiFetch } from "@/lib/api";
import type { CardCopy } from "@/lib/types";

const DURATIONS = [
  { label: "2 hours", hours: 2 },
  { label: "12 hours", hours: 12 },
  { label: "1 day", hours: 24 },
  { label: "3 days", hours: 72 },
  { label: "7 days", hours: 168 },
];

export function CreateAuctionForm({ copies }: { copies: CardCopy[] }) {
  const router = useRouter();
  const [cardCopyId, setCardCopyId] = useState(copies[0]?.id ?? 0);
  const [startingPrice, setStartingPrice] = useState("");
  const [buyNowPrice, setBuyNowPrice] = useState("");
  const [durationHours, setDurationHours] = useState("24");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (copies.length === 0) {
    return (
      <p className="text-sm text-parchment/60">
        You have no unlisted cards to auction. Add some in{" "}
        <a href="/dashboard/cards" className="text-gold hover:underline">
          My Cards
        </a>{" "}
        first.
      </p>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const endTime = new Date(Date.now() + Number(durationHours) * 3600_000).toISOString();
      const auction = await apiFetch<{ id: number }>("/api/auctions/", {
        method: "POST",
        body: JSON.stringify({
          card_copy_id: cardCopyId,
          starting_price: startingPrice,
          buy_now_price: buyNowPrice || null,
          end_time: endTime,
        }),
      });
      router.push(`/auctions/${auction.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create auction");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <label className="block text-sm">
        <span className="mb-1 block text-parchment/80">Card</span>
        <select
          value={cardCopyId}
          onChange={(e) => setCardCopyId(Number(e.target.value))}
          className="w-full rounded border border-gold-dim/40 bg-ink px-3 py-2 text-parchment focus:border-gold focus:outline-none"
        >
          {copies.map((copy) => (
            <option key={copy.id} value={copy.id}>
              {copy.card.name} ({copy.card.card_id}) · {copy.condition}
            </option>
          ))}
        </select>
      </label>

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
        <span className="mb-1 block text-parchment/80">Duration</span>
        <select
          value={durationHours}
          onChange={(e) => setDurationHours(e.target.value)}
          className="w-full rounded border border-gold-dim/40 bg-ink px-3 py-2 text-parchment focus:border-gold focus:outline-none"
        >
          {DURATIONS.map((d) => (
            <option key={d.hours} value={d.hours}>
              {d.label}
            </option>
          ))}
        </select>
      </label>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded bg-gold py-2 font-medium text-ink hover:bg-gold-bright disabled:opacity-50"
      >
        {submitting ? "Creating…" : "Create auction"}
      </button>
    </form>
  );
}
