import Image from "next/image";
import Link from "next/link";

import type { Auction } from "@/lib/types";

import { CountdownTimer } from "./CountdownTimer";

export function AuctionCard({ auction }: { auction: Auction }) {
  const card = auction.card_copy.card;

  return (
    <Link
      href={`/auctions/${auction.id}`}
      className="group block overflow-hidden rounded-lg border border-gold-dim/30 bg-ink-light shadow-card transition hover:border-gold hover:shadow-glow"
    >
      <div className="relative aspect-[5/7] bg-ink">
        {card.images[0]?.url ? (
          <Image
            src={card.images[0].url}
            alt={card.name}
            fill
            className="object-contain p-2 transition group-hover:scale-105"
            sizes="(max-width: 768px) 50vw, 220px"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-parchment/40">No image</div>
        )}
        <span className="absolute left-2 top-2 rounded bg-ink/80 px-2 py-0.5 text-xs uppercase tracking-wide text-gold">
          {auction.status}
        </span>
      </div>
      <div className="space-y-1 p-3">
        <h3 className="truncate font-display text-sm text-parchment">{card.name}</h3>
        <p className="text-xs text-parchment/60">
          {card.card_id} · {card.rarity}
        </p>
        <div className="flex items-center justify-between pt-1">
          <span className="text-lg font-semibold text-gold-bright">${auction.current_price}</span>
          {auction.status === "ACTIVE" ? (
            <CountdownTimer endTime={auction.end_time} />
          ) : (
            <span className="text-xs text-parchment/50">{auction.bid_count} bids</span>
          )}
        </div>
      </div>
    </Link>
  );
}
