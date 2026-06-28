from django.urls import path

from .views import CardDetailView, CardListView

urlpatterns = [
    path("", CardListView.as_view(), name="card-list"),
    path("<str:card_id>/", CardDetailView.as_view(), name="card-detail"),
]
