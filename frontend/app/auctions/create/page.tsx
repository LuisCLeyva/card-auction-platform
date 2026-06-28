import { serverFetch } from "@/lib/server-api";
import type { CardCopy, Paginated } from "@/lib/types";

import { CreateAuctionForm } from "./CreateAuctionForm";

export default async function CreateAuctionPage() {
  const data = await serverFetch<Paginated<CardCopy>>("/api/inventory/?page_size=100");
  const copies = (data?.results ?? []).filter((copy) => !copy.is_listed);

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-6 font-display text-2xl text-gold-bright">List a card for auction</h1>
      <CreateAuctionForm copies={copies} />
    </div>
  );
}
