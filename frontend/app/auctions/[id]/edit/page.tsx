import { notFound, redirect } from "next/navigation";

import type { CurrentUser } from "@/lib/auth";
import { serverFetch } from "@/lib/server-api";
import type { Auction } from "@/lib/types";

import { EditAuctionForm } from "./EditAuctionForm";

export default async function EditAuctionPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const [auction, me] = await Promise.all([
    serverFetch<Auction>(`/api/auctions/${id}/`),
    serverFetch<CurrentUser>("/api/auth/me/"),
  ]);

  if (!auction) notFound();
  if (!me || me.email !== auction.seller) redirect(`/auctions/${id}`);
  if (auction.highest_bid) redirect(`/auctions/${id}`);

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-6 font-display text-2xl text-gold-bright">Edit auction</h1>
      <EditAuctionForm auction={auction} />
    </div>
  );
}
