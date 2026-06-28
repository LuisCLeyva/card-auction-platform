from django.urls import path

from .views import CardDetailView, CardListView, CardSetsView

urlpatterns = [
    path("", CardListView.as_view(), name="card-list"),
    path("sets/", CardSetsView.as_view(), name="card-sets"),
    path("<str:card_id>/", CardDetailView.as_view(), name="card-detail"),
]
