from django.conf import settings
from django.db import models


class CardCopy(models.Model):
    """A specific physical copy of a catalog Card owned by a user. This is
    the unit of 'manage your cards' — and the thing an Auction sells."""

    class Condition(models.TextChoices):
        NEAR_MINT = "NM", "Near Mint"
        LIGHTLY_PLAYED = "LP", "Lightly Played"
        MODERATELY_PLAYED = "MP", "Moderately Played"
        HEAVILY_PLAYED = "HP", "Heavily Played"
        DAMAGED = "DMG", "Damaged"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="card_copies"
    )
    card = models.ForeignKey("cards.Card", on_delete=models.PROTECT, related_name="copies")
    condition = models.CharField(
        max_length=3, choices=Condition.choices, default=Condition.NEAR_MINT
    )
    quantity = models.PositiveIntegerField(default=1)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "card copies"

    def __str__(self):
        return f"{self.owner} x{self.quantity} {self.card.card_id} ({self.condition})"

    @property
    def is_listed(self):
        """Whether this copy currently has an active auction."""
        return self.auctions.filter(status="ACTIVE").exists()
