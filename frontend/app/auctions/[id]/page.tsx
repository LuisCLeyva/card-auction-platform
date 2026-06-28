import Image from "next/image";
import { notFound } from "next/navigation";

import { CountdownTimer } from "@/components/CountdownTimer";
import type { CurrentUser } from "@/lib/auth";
import { serverFetch } from "@/lib/server-api";
import type { Auction } from "@/lib/types";

import { AuctionActions } from "./AuctionActions";

export default async function AuctionDetailPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const [auction, me] = await Promise.all([
    serverFetch<Auction>(`/api/auctions/${id}/`),
    serverFetch<CurrentUser>("/api/auth/me/"),
  ]);

  if (!auction) notFound();

  const card = auction.card_copy.card;
  const isOwner = me?.email === auction.seller;

  return (
    <div className="grid gap-8 md:grid-cols-2">
      <div className="relative aspect-[5/7] overflow-hidden rounded-lg border border-gold-dim/30 bg-ink-light">
        {card.images[0]?.url && (
          <Image
            src={card.images[0].url}
            alt={card.name}
            fill
            className="object-contain p-4"
            sizes="(max-width: 768px) 100vw, 400px"
          />
        )}
      </div>
      <div className="space-y-4">
        <div>
          <h1 className="font-display text-2xl text-gold-bright">{card.name}</h1>
          <p className="text-sm text-parchment/60">
            {card.card_id} · {card.rarity} · {card.color}
          </p>
        </div>

        <dl className="grid grid-cols-2 gap-2 text-sm">
          <Stat label="Status" value={auction.status} />
          <Stat
            label="Ends in"
            value={auction.status === "ACTIVE" ? <CountdownTimer endTime={auction.end_time} /> : "—"}
          />
          <Stat label="Current price" value={`$${auction.current_price}`} />
          <Stat label="Bids" value={String(auction.bid_count)} />
          {auction.buy_now_price && <Stat label="Buy now" value={`$${auction.buy_now_price}`} />}
          <Stat label="Condition" value={auction.card_copy.condition} />
        </dl>

        {card.effect && (
          <p className="rounded border border-gold-dim/20 bg-ink-light p-3 text-sm text-parchment/80">
            {card.effect}
          </p>
        )}

        <AuctionActions auction={auction} isOwner={isOwner} isLoggedIn={!!me} />
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="rounded border border-gold-dim/20 bg-ink-light p-2">
      <dt className="text-xs uppercase tracking-wide text-parchment/50">{label}</dt>
      <dd className="text-gold">{value}</dd>
    </div>
  );
}
