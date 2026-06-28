"use client";

import Image from "next/image";
import { useState } from "react";

import { apiFetch } from "@/lib/api";
import type { Card, CardCopy, Paginated } from "@/lib/types";

const CONDITIONS: CardCopy["condition"][] = ["NM", "LP", "MP", "HP", "DMG"];

export function ManageCardsClient({ initialCopies }: { initialCopies: CardCopy[] }) {
  const [copies, setCopies] = useState(initialCopies);
  const [search, setSearch] = useState("");
  const [results, setResults] = useState<Card[]>([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runSearch(query: string) {
    setSearch(query);
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }
    setSearching(true);
    try {
      const data = await apiFetch<Paginated<Card>>(`/api/cards/?search=${encodeURIComponent(query)}`);
      setResults(data.results);
    } finally {
      setSearching(false);
    }
  }

  async function addCard(card: Card) {
    setError(null);
    try {
      const copy = await apiFetch<CardCopy>("/api/inventory/", {
        method: "POST",
        body: JSON.stringify({ card_id: card.card_id, condition: "NM", quantity: 1 }),
      });
      setCopies((prev) => [copy, ...prev]);
      setResults([]);
      setSearch("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add card");
    }
  }

  async function updateCopy(id: number, patch: Partial<Pick<CardCopy, "condition" | "quantity">>) {
    setError(null);
    try {
      const updated = await apiFetch<CardCopy>(`/api/inventory/${id}/`, {
        method: "PATCH",
        body: JSON.stringify(patch),
      });
      setCopies((prev) => prev.map((c) => (c.id === id ? updated : c)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update card");
    }
  }

  async function removeCopy(id: number) {
    setError(null);
    try {
      await apiFetch(`/api/inventory/${id}/`, { method: "DELETE" });
      setCopies((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not remove card");
    }
  }

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-2 font-display text-lg text-gold">Add a card to your collection</h2>
        <input
          value={search}
          onChange={(e) => runSearch(e.target.value)}
          placeholder="Search the catalog by name…"
          className="w-full rounded border border-gold-dim/40 bg-ink px-3 py-2 text-parchment focus:border-gold focus:outline-none"
        />
        {searching && <p className="mt-2 text-sm text-parchment/50">Searching…</p>}
        {results.length > 0 && (
          <ul className="mt-2 max-h-72 overflow-y-auto rounded border border-gold-dim/20">
            {results.map((card) => (
              <li
                key={card.id}
                className="flex items-center justify-between gap-3 border-b border-gold-dim/10 p-2 last:border-b-0"
              >
                <div className="flex items-center gap-2">
                  {card.image_url && (
                    <div className="relative h-12 w-9 flex-shrink-0">
                      <Image src={card.image_url} alt={card.name} fill className="object-contain" sizes="36px" />
                    </div>
                  )}
                  <div>
                    <p className="text-sm text-parchment">{card.name}</p>
                    <p className="text-xs text-parchment/50">
                      {card.card_id} · {card.rarity}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => addCard(card)}
                  className="rounded border border-gold-dim px-3 py-1 text-xs hover:border-gold hover:text-gold"
                >
                  Add
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <section>
        <h2 className="mb-2 font-display text-lg text-gold">Your collection ({copies.length})</h2>
        {copies.length === 0 ? (
          <p className="text-sm text-parchment/60">No cards yet — search above to add your first one.</p>
        ) : (
          <ul className="grid gap-3 sm:grid-cols-2">
            {copies.map((copy) => (
              <li
                key={copy.id}
                className="flex items-center gap-3 rounded border border-gold-dim/20 bg-ink-light p-3"
              >
                {copy.card.image_url && (
                  <div className="relative h-20 w-14 flex-shrink-0">
                    <Image src={copy.card.image_url} alt={copy.card.name} fill className="object-contain" sizes="56px" />
                  </div>
                )}
                <div className="flex-1">
                  <p className="text-sm text-parchment">{copy.card.name}</p>
                  <p className="text-xs text-parchment/50">{copy.card.card_id}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <select
                      value={copy.condition}
                      disabled={copy.is_listed}
                      onChange={(e) =>
                        updateCopy(copy.id, { condition: e.target.value as CardCopy["condition"] })
                      }
                      className="rounded border border-gold-dim/40 bg-ink px-2 py-1 text-xs text-parchment disabled:opacity-50"
                    >
                      {CONDITIONS.map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))}
                    </select>
                    <input
                      type="number"
                      min={1}
                      value={copy.quantity}
                      disabled={copy.is_listed}
                      onChange={(e) => updateCopy(copy.id, { quantity: Number(e.target.value) })}
                      className="w-16 rounded border border-gold-dim/40 bg-ink px-2 py-1 text-xs text-parchment disabled:opacity-50"
                    />
                    {copy.is_listed ? (
                      <span className="text-xs text-gold">Listed</span>
                    ) : (
                      <button onClick={() => removeCopy(copy.id)} className="text-xs text-red-400 hover:underline">
                        Remove
                      </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
