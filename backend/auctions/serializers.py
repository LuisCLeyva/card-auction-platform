from django.utils import timezone
from rest_framework import serializers

from inventory.models import CardCopy
from inventory.serializers import CardCopySerializer

from .models import Auction, Bid


class BidSerializer(serializers.ModelSerializer):
    bidder = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Bid
        fields = ["id", "auction", "bidder", "amount", "is_buy_now", "created_at"]
        read_only_fields = ["id", "bidder", "is_buy_now", "created_at"]


class AuctionSerializer(serializers.ModelSerializer):
    card_copy = CardCopySerializer(read_only=True)
    card_copy_id = serializers.PrimaryKeyRelatedField(
        source="card_copy", queryset=CardCopy.objects.all(), write_only=True
    )
    seller = serializers.StringRelatedField(read_only=True)
    winner = serializers.StringRelatedField(read_only=True)
    highest_bid = serializers.SerializerMethodField()
    bid_count = serializers.SerializerMethodField()
    is_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = Auction
        fields = [
            "id",
            "card_copy",
            "card_copy_id",
            "seller",
            "starting_price",
            "buy_now_price",
            "current_price",
            "min_increment",
            "status",
            "start_time",
            "end_time",
            "winner",
            "final_price",
            "highest_bid",
            "bid_count",
            "is_open",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "seller",
            "current_price",
            "status",
            "winner",
            "final_price",
            "is_open",
            "created_at",
            "updated_at",
        ]

    def get_highest_bid(self, obj):
        bid = obj.bids.first()  # Bid.Meta.ordering already puts the highest first
        return BidSerializer(bid).data if bid else None

    def get_bid_count(self, obj):
        return obj.bids.count()

    def validate(self, attrs):
        request = self.context["request"]

        if self.instance is None:
            card_copy = attrs.get("card_copy")
            if card_copy.owner_id != request.user.id:
                raise serializers.ValidationError("You can only auction your own card copies.")
            if card_copy.is_listed:
                raise serializers.ValidationError(
                    "This card copy already has an active auction."
                )
        else:
            if self.instance.bids.exists():
                raise serializers.ValidationError(
                    "Cannot edit an auction once bids have been placed."
                )
            if self.instance.status != Auction.Status.ACTIVE:
                raise serializers.ValidationError("Only active auctions can be edited.")

        start_time = (
            attrs.get("start_time") or getattr(self.instance, "start_time", None) or timezone.now()
        )
        end_time = attrs.get("end_time") or getattr(self.instance, "end_time", None)
        if end_time and end_time <= start_time:
            raise serializers.ValidationError("end_time must be after start_time.")
        if end_time and end_time <= timezone.now():
            raise serializers.ValidationError("end_time must be in the future.")

        starting_price = attrs.get("starting_price", getattr(self.instance, "starting_price", None))
        buy_now_price = attrs.get("buy_now_price", getattr(self.instance, "buy_now_price", None))
        if buy_now_price is not None and starting_price is not None and buy_now_price <= starting_price:
            raise serializers.ValidationError("buy_now_price must be greater than starting_price.")

        return attrs

    def create(self, validated_data):
        validated_data["seller"] = self.context["request"].user
        validated_data["current_price"] = validated_data["starting_price"]
        validated_data.setdefault("start_time", timezone.now())
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # validate() already guarantees no bids exist whenever an edit is
        # allowed, so the "current" price is still just the starting price.
        if "starting_price" in validated_data:
            validated_data["current_price"] = validated_data["starting_price"]
        return super().update(instance, validated_data)
