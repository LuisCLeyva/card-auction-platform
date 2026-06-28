from rest_framework import generics, permissions

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
            qs = qs.filter(name__icontains=search)

        card_type = params.get("card_type")
        if card_type:
            qs = qs.filter(card_type=card_type.upper())

        color = params.get("color")
        if color:
            qs = qs.filter(color__icontains=color)

        rarity = params.get("rarity")
        if rarity:
            qs = qs.filter(rarity=rarity.upper())

        return qs


class CardDetailView(generics.RetrieveAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "card_id"
