from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError

from .models import CardCopy
from .serializers import CardCopySerializer


class CardCopyViewSet(viewsets.ModelViewSet):
    """A user's personal card collection — 'manage cards'. Scoped to the
    authenticated user; a copy can't be edited or removed while it has an
    active auction."""

    serializer_class = CardCopySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return CardCopy.objects.filter(owner=self.request.user).select_related("card")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.is_listed:
            raise ValidationError("Cannot edit a card copy that has an active auction.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_listed:
            raise ValidationError("Cannot remove a card copy that has an active auction.")
        instance.delete()
