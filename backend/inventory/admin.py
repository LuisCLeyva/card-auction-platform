from django.contrib import admin

from .models import CardCopy


@admin.register(CardCopy)
class CardCopyAdmin(admin.ModelAdmin):
    list_display = ["id", "owner", "card", "condition", "quantity", "created_at"]
    list_filter = ["condition"]
    search_fields = ["card__card_id", "card__name", "owner__email"]
