from django.core.management.base import BaseCommand
from django.utils import timezone

from auctions.models import Auction


class Command(BaseCommand):
    help = (
        "Close auctions whose end_time has passed: SOLD (to the highest "
        "bidder) if any bids exist, otherwise EXPIRED. Run this on a "
        "schedule (cron / Celery beat) in production; for local dev, run "
        "it manually or via `make close-auctions`."
    )

    def handle(self, *args, **options):
        expired = Auction.objects.filter(
            status=Auction.Status.ACTIVE, end_time__lte=timezone.now()
        )
        closed = 0
        for auction in expired:
            top_bid = auction.bids.first()
            if top_bid:
                auction.status = Auction.Status.SOLD
                auction.winner = top_bid.bidder
                auction.final_price = top_bid.amount
            else:
                auction.status = Auction.Status.EXPIRED
            auction.save(update_fields=["status", "winner", "final_price", "updated_at"])
            closed += 1

        self.stdout.write(self.style.SUCCESS(f"Closed {closed} auction(s)."))
