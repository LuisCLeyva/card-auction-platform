from django.db import models


class Card(models.Model):
    """Read-only reference data for a physical trading card, e.g. seeded
    from the One Piece TCG catalog. Users don't edit these directly — they
    add copies of a Card to their personal collection (see inventory.CardCopy)
    and auction those copies."""

    class CardType(models.TextChoices):
        LEADER = "LEADER", "Leader"
        CHARACTER = "CHARACTER", "Character"
        EVENT = "EVENT", "Event"
        STAGE = "STAGE", "Stage"

    class Rarity(models.TextChoices):
        COMMON = "C", "Common"
        UNCOMMON = "UC", "Uncommon"
        RARE = "R", "Rare"
        SUPER_RARE = "SR", "Super Rare"
        SECRET_RARE = "SEC", "Secret Rare"
        LEADER_RARITY = "L", "Leader"
        PROMO = "P", "Promo"
        TREASURY_RARE = "TR", "Treasury Rare"
        SPECIAL_CARD = "SP CARD", "Special Card"

    card_id = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=120, db_index=True)
    card_type = models.CharField(max_length=12, choices=CardType.choices)
    rarity = models.CharField(max_length=10, choices=Rarity.choices)

    # CHARACTER/EVENT/STAGE cards have a numeric `cost`; LEADER cards have a
    # `life` total instead (sourced from the catalog's "LifeN" cost string).
    cost = models.PositiveSmallIntegerField(null=True, blank=True)
    life = models.PositiveSmallIntegerField(null=True, blank=True)

    attribute = models.CharField(max_length=20, blank=True)
    power = models.PositiveIntegerField(null=True, blank=True)
    counter = models.PositiveIntegerField(null=True, blank=True)
    color = models.CharField(max_length=30, blank=True, db_index=True)
    block = models.CharField(max_length=10, blank=True)
    feature = models.CharField(max_length=255, blank=True)
    effect = models.TextField(blank=True)
    set_name = models.CharField(max_length=120, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["card_id"]

    def __str__(self):
        return f"{self.card_id} {self.name}"


class CardImage(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="cards/")
    is_alternate = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = [["card", "order"]]

    def __str__(self):
        kind = "AA" if self.is_alternate else "Standard"
        return f"{self.card.card_id} {kind} (order={self.order})"
