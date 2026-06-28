from django.contrib import admin

from .models import Auction, Bid


class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    readonly_fields = ["bidder", "amount", "is_buy_now", "created_at"]


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ["id", "card_copy", "seller", "status", "current_price", "end_time"]
    list_filter = ["status"]
    search_fields = ["card_copy__card__card_id", "card_copy__card__name", "seller__email"]
    inlines = [BidInline]


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ["id", "auction", "bidder", "amount", "is_buy_now", "created_at"]
