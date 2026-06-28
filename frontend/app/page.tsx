import { AuctionCard } from "@/components/AuctionCard";
import { serverFetch } from "@/lib/server-api";
import type { Auction, Paginated } from "@/lib/types";

export default async function HomePage() {
  const data = await serverFetch<Paginated<Auction>>("/api/auctions/?status=active&page_size=50");
  const auctions = data?.results ?? [];

  return (
    <div>
      <h1 className="mb-6 font-display text-3xl text-gold-bright">Live Auctions</h1>
      {auctions.length === 0 ? (
        <p className="text-parchment/60">No active auctions right now. Check back soon.</p>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {auctions.map((auction) => (
            <AuctionCard key={auction.id} auction={auction} />
          ))}
        </div>
      )}
    </div>
  );
}
