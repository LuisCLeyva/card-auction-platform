from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Card
from .serializers import CardSerializer


class CardListView(generics.ListAPIView):
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Card.objects.all()
        params = self.request.query_params

        search = params.get("search")
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(card_id__icontains=search)

        card_type = params.get("card_type")
        if card_type:
            qs = qs.filter(card_type=card_type.upper())

        color = params.get("color")
        if color:
            qs = qs.filter(color__icontains=color)

        rarity = params.get("rarity")
        if rarity:
            qs = qs.filter(rarity=rarity.upper())

        set_name = params.get("set_name")
        if set_name:
            qs = qs.filter(set_name=set_name)

        return qs


class CardSetsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.db.models import Min
        # Sort by the earliest card_id in each set (EB01-xxx < OP01-xxx < ST01-xxx)
        # which gives the natural set-code order the user expects.
        sets = (
            Card.objects.exclude(set_name="")
            .values("set_name")
            .annotate(first_card_id=Min("card_id"))
            .order_by("-first_card_id")
            .values_list("set_name", flat=True)
        )
        return Response(list(sets))


class CardDetailView(generics.RetrieveAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "card_id"
