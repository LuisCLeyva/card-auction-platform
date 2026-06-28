export interface CardImage {
  id: number;
  url: string;
  is_alternate: boolean;
  order: number;
}

export interface Card {
  id: number;
  card_id: string;
  name: string;
  card_type: "LEADER" | "CHARACTER" | "EVENT" | "STAGE";
  rarity: string;
  cost: number | null;
  life: number | null;
  attribute: string;
  power: number | null;
  counter: number | null;
  color: string;
  block: string;
  feature: string;
  effect: string;
  set_name: string;
  images: CardImage[];
}

export interface CardCopy {
  id: number;
  card: Card;
  condition: "NM" | "LP" | "MP" | "HP" | "DMG";
  quantity: number;
  notes: string;
  is_listed: boolean;
  created_at: string;
  updated_at: string;
}

export const CONDITION_LABELS: Record<CardCopy["condition"], string> = {
  NM: "Near Mint",
  LP: "Lightly Played",
  MP: "Moderately Played",
  HP: "Heavily Played",
  DMG: "Damaged",
};

export interface Bid {
  id: number;
  auction: number;
  bidder: string;
  amount: string;
  is_buy_now: boolean;
  created_at: string;
}

export type AuctionStatus = "ACTIVE" | "SOLD" | "CANCELLED" | "EXPIRED";

export interface Auction {
  id: number;
  card_copy: CardCopy;
  seller: string;
  starting_price: string;
  buy_now_price: string | null;
  current_price: string;
  min_increment: string;
  status: AuctionStatus;
  start_time: string;
  end_time: string;
  winner: string | null;
  final_price: string | null;
  highest_bid: Bid | null;
  bid_count: number;
  is_open: boolean;
  created_at: string;
  updated_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
