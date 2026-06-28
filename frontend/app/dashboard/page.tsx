import Link from "next/link";

import { AuctionCard } from "@/components/AuctionCard";
import { serverFetch } from "@/lib/server-api";
import type { Auction, Paginated } from "@/lib/types";

export default async function DashboardPage() {
  const data = await serverFetch<Paginated<Auction>>("/api/auctions/?mine=true&page_size=100");
  const auctions = data?.results ?? [];

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl text-gold-bright">My Auctions</h1>
        <Link
          href="/auctions/create"
          className="rounded bg-gold px-4 py-2 text-sm font-medium text-ink hover:bg-gold-bright"
        >
          + List a card
        </Link>
      </div>
      {auctions.length === 0 ? (
        <p className="text-parchment/60">
          You haven&apos;t listed anything yet. Add cards in{" "}
          <Link href="/dashboard/cards" className="text-gold hover:underline">
            My Cards
          </Link>{" "}
          then list one.
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
          {auctions.map((auction) => (
            <AuctionCard key={auction.id} auction={auction} />
          ))}
        </div>
      )}
    </div>
  );
}
