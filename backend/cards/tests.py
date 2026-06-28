import pytest

from cards.models import Card

pytestmark = pytest.mark.django_db


def test_list_cards_is_public(api_client, make_card):
    make_card(card_id="OP01-101", name="Zoro")
    make_card(card_id="OP01-102", name="Luffy")

    response = api_client.get("/api/cards/")

    assert response.status_code == 200
    assert response.data["count"] == 2


def test_filter_by_card_type(api_client, make_card):
    make_card(card_id="OP01-103", card_type=Card.CardType.LEADER)
    make_card(card_id="OP01-104", card_type=Card.CardType.CHARACTER)

    response = api_client.get("/api/cards/?card_type=leader")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["card_id"] == "OP01-103"


def test_search_by_name(api_client, make_card):
    make_card(card_id="OP01-105", name="Roronoa Zoro")
    make_card(card_id="OP01-106", name="Monkey D. Luffy")

    response = api_client.get("/api/cards/?search=zoro")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == "Roronoa Zoro"


def test_retrieve_by_card_id(api_client, card):
    response = api_client.get(f"/api/cards/{card.card_id}/")

    assert response.status_code == 200
    assert response.data["card_id"] == card.card_id


def test_cards_catalog_is_read_only(api_client):
    response = api_client.post("/api/cards/", {"card_id": "OP01-999", "name": "Hack"})

    assert response.status_code == 405
