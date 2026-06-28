"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";
import type { Card, CardCopy, CardImage, Paginated } from "@/lib/types";

const CONDITIONS: CardCopy["condition"][] = ["NM", "LP", "MP", "HP", "DMG"];

const CARD_TYPES = ["CHARACTER", "LEADER", "EVENT", "STAGE"] as const;
const RARITIES = ["C", "UC", "R", "SR", "SEC", "TR", "SP CARD", "L", "P"] as const;
const COLORS = ["Red", "Blue", "Green", "Purple", "Black", "Yellow"] as const;

interface Filters {
  card_type: string;
  rarity: string;
  color: string;
  set_name: string;
}

export function ManageCardsClient({ initialCopies }: { initialCopies: CardCopy[] }) {
  const [copies, setCopies] = useState(initialCopies);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<Filters>({ card_type: "", rarity: "", color: "", set_name: "" });
  const [results, setResults] = useState<Card[]>([]);
  const [searching, setSearching] = useState(false);
  const [sets, setSets] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [artPicker, setArtPicker] = useState<{ card: Card; selectedImage: CardImage } | null>(null);

  useEffect(() => {
    apiFetch<string[]>("/api/cards/sets/").then(setSets).catch(() => {});
  }, []);

  useEffect(() => {
    const hasFilter = Object.values(filters).some(Boolean);
    if (search.trim().length < 2 && !hasFilter) {
      setResults([]);
      return;
    }
    const controller = new AbortController();
    setSearching(true);
    const params = new URLSearchParams();
    if (search.trim()) params.set("search", search.trim());
    if (filters.card_type) params.set("card_type", filters.card_type);
    if (filters.rarity) params.set("rarity", filters.rarity);
    if (filters.color) params.set("color", filters.color);
    if (filters.set_name) params.set("set_name", filters.set_name);
    params.set("page_size", "50");

    apiFetch<Paginated<Card>>(`/api/cards/?${params}`)
      .then((data) => setResults(data.results))
      .catch(() => {})
      .finally(() => setSearching(false));

    return () => controller.abort();
  }, [search, filters]);

  function setFilter(key: keyof Filters, value: string) {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }

  function selectCard(card: Card) {
    if (card.images.length <= 1) {
      addCard(card, card.images[0] ?? null);
    } else {
      setArtPicker({ card, selectedImage: card.images[0] });
    }
  }

  async function addCard(card: Card, image: CardImage | null) {
    setError(null);
    setArtPicker(null);
    try {
      const copy = await apiFetch<CardCopy>("/api/inventory/", {
        method: "POST",
        body: JSON.stringify({
          card_id: card.card_id,
          condition: "NM",
          quantity: 1,
          card_image_id: image?.id ?? null,
        }),
      });
      setCopies((prev) => [copy, ...prev]);
      setResults([]);
      setSearch("");
      setFilters({ card_type: "", rarity: "", color: "", set_name: "" });
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

  const displayImage = (copy: CardCopy) => copy.card_image?.url ?? copy.card.images[0]?.url ?? null;
  const hasFilters = search.trim().length >= 2 || Object.values(filters).some(Boolean);

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-2 font-display text-lg text-gold">Add a card to your collection</h2>

        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name or card ID (e.g. OP08-001)…"
          className="w-full rounded border border-gold-dim/40 bg-ink px-3 py-2 text-parchment focus:border-gold focus:outline-none"
        />

        <div className="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4">
          <select
            value={filters.set_name}
            onChange={(e) => setFilter("set_name", e.target.value)}
            className="rounded border border-gold-dim/40 bg-ink px-2 py-1.5 text-xs text-parchment focus:border-gold focus:outline-none"
          >
            <option value="">All sets</option>
            {sets.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>

          <select
            value={filters.card_type}
            onChange={(e) => setFilter("card_type", e.target.value)}
            className="rounded border border-gold-dim/40 bg-ink px-2 py-1.5 text-xs text-parchment focus:border-gold focus:outline-none"
          >
            <option value="">All types</option>
            {CARD_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>

          <select
            value={filters.color}
            onChange={(e) => setFilter("color", e.target.value)}
            className="rounded border border-gold-dim/40 bg-ink px-2 py-1.5 text-xs text-parchment focus:border-gold focus:outline-none"
          >
            <option value="">All colors</option>
            {COLORS.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>

          <select
            value={filters.rarity}
            onChange={(e) => setFilter("rarity", e.target.value)}
            className="rounded border border-gold-dim/40 bg-ink px-2 py-1.5 text-xs text-parchment focus:border-gold focus:outline-none"
          >
            <option value="">All rarities</option>
            {RARITIES.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>

        {searching && <p className="mt-2 text-sm text-parchment/50">Searching…</p>}

        {!searching && hasFilters && results.length === 0 && (
          <p className="mt-2 text-sm text-parchment/50">No cards found.</p>
        )}

        {results.length > 0 && (
          <ul className="mt-2 max-h-72 overflow-y-auto rounded border border-gold-dim/20">
            {results.map((card) => (
              <li
                key={card.id}
                className="flex items-center justify-between gap-3 border-b border-gold-dim/10 p-2 last:border-b-0"
              >
                <div className="flex items-center gap-2">
                  {card.images[0]?.url && (
                    <div className="relative h-12 w-9 flex-shrink-0">
                      <Image src={card.images[0].url} alt={card.name} fill className="object-contain" sizes="36px" />
                    </div>
                  )}
                  <div>
                    <p className="text-sm text-parchment">{card.name}</p>
                    <p className="text-xs text-parchment/50">
                      {card.card_id} · {card.rarity} · {card.color}
                      {card.images.length > 1 && (
                        <span className="ml-1 text-gold">· {card.images.length - 1} AA</span>
                      )}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => selectCard(card)}
                  className="rounded border border-gold-dim px-3 py-1 text-xs hover:border-gold hover:text-gold"
                >
                  Add
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Art picker modal */}
      {artPicker && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
          <div className="w-full max-w-md rounded-lg border border-gold-dim/30 bg-ink-light p-6">
            <h3 className="mb-4 font-display text-lg text-gold-bright">Choose art variant</h3>
            <p className="mb-4 text-sm text-parchment/60">{artPicker.card.name} · {artPicker.card.card_id}</p>
            <div className="mb-6 flex flex-wrap gap-3">
              {artPicker.card.images.map((img) => (
                <button
                  key={img.id}
                  onClick={() => setArtPicker((p) => p ? { ...p, selectedImage: img } : null)}
                  className={`relative h-32 w-24 overflow-hidden rounded border-2 transition ${
                    artPicker.selectedImage.id === img.id
                      ? "border-gold"
                      : "border-gold-dim/30 hover:border-gold-dim"
                  }`}
                >
                  <Image src={img.url} alt={img.is_alternate ? "Alternate Art" : "Standard"} fill className="object-contain p-1" sizes="96px" />
                  <span className="absolute bottom-0 left-0 right-0 bg-ink/80 py-0.5 text-center text-xs text-parchment">
                    {img.is_alternate ? `AA ${img.order}` : "Standard"}
                  </span>
                </button>
              ))}
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => addCard(artPicker.card, artPicker.selectedImage)}
                className="flex-1 rounded bg-gold py-2 font-medium text-ink hover:bg-gold-bright"
              >
                Add to collection
              </button>
              <button
                onClick={() => setArtPicker(null)}
                className="rounded border border-gold-dim/40 px-4 py-2 text-sm hover:border-gold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

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
                {displayImage(copy) && (
                  <div className="relative h-20 w-14 flex-shrink-0">
                    <Image src={displayImage(copy)!} alt={copy.card.name} fill className="object-contain" sizes="56px" />
                  </div>
                )}
                <div className="flex-1">
                  <p className="text-sm text-parchment">{copy.card.name}</p>
                  <p className="text-xs text-parchment/50">
                    {copy.card.card_id}
                    {copy.card_image?.is_alternate && (
                      <span className="ml-1 text-gold">AA</span>
                    )}
                  </p>
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
                        <option key={c} value={c}>{c}</option>
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
