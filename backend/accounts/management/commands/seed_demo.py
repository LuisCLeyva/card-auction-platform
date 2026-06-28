import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from auctions.models import Auction, Bid
from cards.models import Card
from inventory.models import CardCopy

User = get_user_model()

DEMO_PASSWORD = "DemoPass123!"
DEMO_USERS = [
    ("alice@example.com", "Alice"),
    ("bob@example.com", "Bob"),
    ("carol@example.com", "Carol"),
    ("dave@example.com", "Dave"),
]


class Command(BaseCommand):
    help = "Create demo users, a personal card collection for each, and a mix of auctions/bids."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Remove existing demo users' auctions/collections before reseeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not Card.objects.exists():
            self.stderr.write(self.style.ERROR("No cards found — run `seed_cards` first."))
            return

        users = [self._get_or_create_user(email, name) for email, name in DEMO_USERS]

        if options["clear"]:
            Auction.objects.filter(seller__in=users).delete()
            CardCopy.objects.filter(owner__in=users).delete()

        rng = random.Random(42)
        cards = list(Card.objects.all())

        copies_by_user = {}
        for user in users:
            sample = rng.sample(cards, k=min(8, len(cards)))
            copies_by_user[user] = [
                CardCopy.objects.create(
                    owner=user,
                    card=card,
                    condition=rng.choice(CardCopy.Condition.values),
                    quantity=rng.choice([1, 1, 1, 2]),
                )
                for card in sample
            ]

        now = timezone.now()
        auctions_created = 0
        for user in users:
            for copy in copies_by_user[user][:3]:
                starting_price = rng.choice([5, 10, 15, 25, 50])
                buy_now = starting_price * 4 if rng.random() < 0.5 else None
                auction = Auction.objects.create(
                    card_copy=copy,
                    seller=user,
                    starting_price=starting_price,
                    current_price=starting_price,
                    buy_now_price=buy_now,
                    end_time=now + timedelta(hours=rng.choice([2, 12, 24, 72])),
                )
                auctions_created += 1

                other_bidders = [u for u in users if u != user]
                for amount_step in range(rng.choice([0, 1, 2])):
                    bidder = rng.choice(other_bidders)
                    top_bid = auction.bids.first()
                    amount = (top_bid.amount if top_bid else auction.starting_price) + auction.min_increment * (
                        amount_step + 1
                    )
                    Bid.objects.create(auction=auction, bidder=bidder, amount=amount)
                    auction.current_price = amount
                    auction.save(update_fields=["current_price"])

        self.stdout.write(self.style.SUCCESS(f"Demo users ready (password: {DEMO_PASSWORD})."))
        self.stdout.write(self.style.SUCCESS(f"Created {auctions_created} demo auctions."))

    @staticmethod
    def _get_or_create_user(email, name):
        user, created = User.objects.get_or_create(email=email, defaults={"display_name": name})
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
        return user
