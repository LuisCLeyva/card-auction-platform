from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Auction, Bid
from .serializers import AuctionSerializer


class IsSellerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller_id == request.user.id


class AuctionViewSet(viewsets.ModelViewSet):
    """create/edit/cancel auctions, plus bid/buy-now actions.

    Browsing (list/retrieve) is public; everything else requires auth.
    Editing and cancelling are seller-only and only while no bids exist —
    once someone has bid, the terms can no longer change underneath them.
    There is no hard delete: a cancelled auction is kept for history.
    """

    queryset = Auction.objects.select_related(
        "card_copy__card", "seller", "winner"
    ).prefetch_related("bids")
    serializer_class = AuctionSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_permissions(self):
        if self.action in ("update", "partial_update", "cancel"):
            return [permissions.IsAuthenticated(), IsSellerOrReadOnly()]
        if self.action in ("bid", "buy_now"):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        status_param = params.get("status")
        if status_param:
            qs = qs.filter(status=status_param.upper())

        if params.get("mine") and self.request.user.is_authenticated:
            qs = qs.filter(seller=self.request.user)

        return qs

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        auction = self.get_object()
        if auction.status != Auction.Status.ACTIVE:
            raise ValidationError("Only active auctions can be cancelled.")
        if auction.bids.exists():
            raise ValidationError("Cannot cancel an auction once bids have been placed.")

        auction.status = Auction.Status.CANCELLED
        auction.save(update_fields=["status", "updated_at"])
        return Response(AuctionSerializer(auction, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"])
    def bid(self, request, pk=None):
        amount = self._parse_amount(request.data.get("amount"))

        with transaction.atomic():
            auction = Auction.objects.select_for_update().get(pk=self.get_object().pk)
            self._validate_biddable(auction, request.user)

            top_bid = auction.bids.first()
            min_required = (top_bid.amount + auction.min_increment) if top_bid else auction.starting_price
            if amount < min_required:
                raise ValidationError({"amount": f"Bid must be at least {min_required}."})

            if auction.buy_now_price and amount >= auction.buy_now_price:
                auction = self._close_with_winner(
                    auction, request.user, auction.buy_now_price, is_buy_now=True
                )
            else:
                Bid.objects.create(auction=auction, bidder=request.user, amount=amount)
                auction.current_price = amount
                auction.save(update_fields=["current_price", "updated_at"])

        return Response(
            AuctionSerializer(auction, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="buy-now")
    def buy_now(self, request, pk=None):
        with transaction.atomic():
            auction = Auction.objects.select_for_update().get(pk=self.get_object().pk)
            self._validate_biddable(auction, request.user)
            if not auction.buy_now_price:
                raise ValidationError("This auction does not support Buy Now.")
            auction = self._close_with_winner(
                auction, request.user, auction.buy_now_price, is_buy_now=True
            )

        return Response(AuctionSerializer(auction, context=self.get_serializer_context()).data)

    @staticmethod
    def _parse_amount(raw):
        if raw is None:
            raise ValidationError({"amount": "This field is required."})
        try:
            return Decimal(str(raw))
        except InvalidOperation:
            raise ValidationError({"amount": "Must be a number."})

    @staticmethod
    def _validate_biddable(auction, user):
        if auction.seller_id == user.id:
            raise ValidationError("Sellers cannot bid on their own auction.")
        if auction.status != Auction.Status.ACTIVE:
            raise ValidationError("This auction is not active.")
        if timezone.now() >= auction.end_time:
            raise ValidationError("This auction has already ended.")

    @staticmethod
    def _close_with_winner(auction, user, amount, is_buy_now):
        Bid.objects.create(auction=auction, bidder=user, amount=amount, is_buy_now=is_buy_now)
        auction.current_price = amount
        auction.final_price = amount
        auction.winner = user
        auction.status = Auction.Status.SOLD
        auction.end_time = timezone.now()
        auction.save(
            update_fields=[
                "current_price",
                "final_price",
                "winner",
                "status",
                "end_time",
                "updated_at",
            ]
        )
        return auction
