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

        PREFIX_ORDER = {"OP": 0, "ST": 1, "EB": 2}

        def sort_key(row):
            code = row["first_card_id"][:4]  # e.g. "OP01"
            prefix = code[:2]
            number = int(code[2:]) if code[2:].isdigit() else 0
            return (PREFIX_ORDER.get(prefix, 99), -number)

        rows = (
            Card.objects.exclude(set_name="")
            .values("set_name")
            .annotate(first_card_id=Min("card_id"))
        )
        return Response([r["set_name"] for r in sorted(rows, key=sort_key)])


class CardDetailView(generics.RetrieveAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "card_id"
