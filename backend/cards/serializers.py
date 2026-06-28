from django.conf import settings
from rest_framework import serializers

from .models import Card, CardImage


class CardImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = CardImage
        fields = ["id", "url", "is_alternate", "order"]

    def get_url(self, obj):
        if not obj.image:
            return None
        return f"{settings.MEDIA_BASE_URL}{obj.image.url}"


class CardSerializer(serializers.ModelSerializer):
    images = CardImageSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = [
            "id",
            "card_id",
            "name",
            "card_type",
            "rarity",
            "cost",
            "life",
            "attribute",
            "power",
            "counter",
            "color",
            "block",
            "feature",
            "effect",
            "set_name",
            "images",
        ]
