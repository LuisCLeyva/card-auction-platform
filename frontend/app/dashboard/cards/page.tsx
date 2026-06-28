import { serverFetch } from "@/lib/server-api";
import type { CardCopy, Paginated } from "@/lib/types";

import { ManageCardsClient } from "./ManageCardsClient";

export default async function ManageCardsPage() {
  const data = await serverFetch<Paginated<CardCopy>>("/api/inventory/?page_size=100");

  return (
    <div>
      <h1 className="mb-6 font-display text-2xl text-gold-bright">My Cards</h1>
      <ManageCardsClient initialCopies={data?.results ?? []} />
    </div>
  );
}
