from rest_framework import serializers

from cards.models import Card
from cards.serializers import CardSerializer

from .models import CardCopy


class CardCopySerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)
    card_id = serializers.SlugRelatedField(
        source="card",
        slug_field="card_id",
        queryset=Card.objects.all(),
        write_only=True,
    )
    is_listed = serializers.BooleanField(read_only=True)

    class Meta:
        model = CardCopy
        fields = [
            "id",
            "card",
            "card_id",
            "condition",
            "quantity",
            "notes",
            "is_listed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_listed", "created_at", "updated_at"]
