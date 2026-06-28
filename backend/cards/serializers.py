from django.conf import settings
from rest_framework import serializers

from .models import Card


class CardSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    alt_image_url = serializers.SerializerMethodField()

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
            "image_url",
            "alt_image_url",
        ]

    def _absolute_url(self, field):
        if not field:
            return None
        # Not request.build_absolute_uri(): that would vary with whichever
        # Host header the caller used (browser vs. Next.js's server-side
        # fetch), but next/image always re-fetches this URL server-side
        # from inside the frontend container — so it must always resolve
        # from there. See MEDIA_BASE_URL's docstring in settings.py.
        return f"{settings.MEDIA_BASE_URL}{field.url}"

    def get_image_url(self, obj):
        return self._absolute_url(obj.image)

    def get_alt_image_url(self, obj):
        return self._absolute_url(obj.alt_image)
