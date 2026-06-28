import pytest

from inventory.models import CardCopy

pytestmark = pytest.mark.django_db


def test_list_requires_authentication(api_client):
    response = api_client.get("/api/inventory/")
    assert response.status_code == 401


def test_user_can_add_a_card_to_their_collection(api_client, user, card, login_as):
    csrftoken = login_as(user)

    response = api_client.post(
        "/api/inventory/",
        {"card_id": card.card_id, "condition": "NM", "quantity": 2},
        HTTP_X_CSRFTOKEN=csrftoken,
    )

    assert response.status_code == 201, response.data
    copy = CardCopy.objects.get()
    assert copy.owner == user
    assert copy.card == card
    assert copy.quantity == 2


def test_user_only_sees_their_own_collection(api_client, user, other_user, card, login_as, make_card_copy):
    make_card_copy(owner=user, card=card)
    make_card_copy(owner=other_user, card=card)
    login_as(user)

    response = api_client.get("/api/inventory/")

    assert response.status_code == 200
    assert response.data["count"] == 1


def test_cannot_remove_a_copy_with_an_active_auction(
    api_client, user, card_copy, make_auction, login_as
):
    make_auction(card_copy)
    csrftoken = login_as(user)

    response = api_client.delete(f"/api/inventory/{card_copy.id}/", HTTP_X_CSRFTOKEN=csrftoken)

    assert response.status_code == 400
    assert CardCopy.objects.filter(id=card_copy.id).exists()


def test_cannot_edit_a_copy_with_an_active_auction(
    api_client, user, card_copy, make_auction, login_as
):
    make_auction(card_copy)
    csrftoken = login_as(user)

    response = api_client.patch(
        f"/api/inventory/{card_copy.id}/", {"quantity": 5}, HTTP_X_CSRFTOKEN=csrftoken
    )

    assert response.status_code == 400


def test_can_remove_an_unlisted_copy(api_client, user, card_copy, login_as):
    csrftoken = login_as(user)

    response = api_client.delete(f"/api/inventory/{card_copy.id}/", HTTP_X_CSRFTOKEN=csrftoken)

    assert response.status_code == 204
    assert not CardCopy.objects.filter(id=card_copy.id).exists()
