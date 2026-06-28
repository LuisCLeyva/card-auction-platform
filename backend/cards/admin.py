from django.contrib import admin

from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ["card_id", "name", "card_type", "rarity", "color", "set_name"]
    list_filter = ["card_type", "rarity", "color"]
    search_fields = ["card_id", "name"]
