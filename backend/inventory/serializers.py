from rest_framework import serializers

from cards.models import Card, CardImage
from cards.serializers import CardSerializer, CardImageSerializer

from .models import CardCopy


class CardCopySerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)
    card_id = serializers.SlugRelatedField(
        source="card",
        slug_field="card_id",
        queryset=Card.objects.all(),
        write_only=True,
    )
    card_image = CardImageSerializer(read_only=True)
    card_image_id = serializers.PrimaryKeyRelatedField(
        source="card_image",
        queryset=CardImage.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    is_listed = serializers.BooleanField(read_only=True)

    class Meta:
        model = CardCopy
        fields = [
            "id",
            "card",
            "card_id",
            "card_image",
            "card_image_id",
            "condition",
            "quantity",
            "notes",
            "is_listed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_listed", "created_at", "updated_at"]

    def validate(self, attrs):
        card = attrs.get("card") or (self.instance.card if self.instance else None)
        card_image = attrs.get("card_image")
        if card_image and card_image.card_id != card.id:
            raise serializers.ValidationError(
                {"card_image_id": "This image does not belong to the selected card."}
            )
        return attrs
