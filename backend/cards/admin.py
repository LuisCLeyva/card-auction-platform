from django.contrib import admin

from .models import Card, CardImage


class CardImageInline(admin.TabularInline):
    model = CardImage
    extra = 0
    readonly_fields = ["order", "is_alternate"]


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ["card_id", "name", "card_type", "rarity", "color", "set_name"]
    list_filter = ["card_type", "rarity", "color"]
    search_fields = ["card_id", "name"]
    inlines = [CardImageInline]
