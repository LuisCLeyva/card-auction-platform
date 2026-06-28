from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Auction(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        SOLD = "SOLD", "Sold"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"

    card_copy = models.ForeignKey(
        "inventory.CardCopy", on_delete=models.PROTECT, related_name="auctions"
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="auctions_selling"
    )
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    buy_now_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_increment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1.00"))
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auctions_won",
    )
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Auction#{self.pk} {self.card_copy_id} ({self.status})"

    def clean(self):
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError("end_time must be after start_time.")
        if self.buy_now_price is not None and self.buy_now_price <= self.starting_price:
            raise ValidationError("buy_now_price must be greater than starting_price.")

    @property
    def is_open(self):
        return self.status == self.Status.ACTIVE and timezone.now() < self.end_time

    @property
    def has_bids(self):
        return self.bids.exists()


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bids"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_buy_now = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-amount", "created_at"]

    def __str__(self):
        return f"Bid#{self.pk} {self.amount} on Auction#{self.auction_id}"
