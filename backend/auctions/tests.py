from datetime import timedelta
from decimal import Decimal

from django.core.management import call_command
from django.utils import timezone
import pytest

from auctions.models import Auction, Bid

pytestmark = pytest.mark.django_db


def _future(**kwargs):
    return (timezone.now() + timedelta(**kwargs)).isoformat()


# ---- browsing -------------------------------------------------------------


def test_list_is_public(api_client, auction):
    response = api_client.get("/api/auctions/")
    assert response.status_code == 200
    assert response.data["count"] == 1


# ---- create -----------------------------------------------------------


def test_create_requires_authentication(api_client, card_copy):
    response = api_client.post(
        "/api/auctions/",
        {"card_copy_id": card_copy.id, "starting_price": "10.00", "end_time": _future(hours=2)},
    )
    assert response.status_code == 401


def test_seller_can_create_auction_for_own_copy(api_client, user, card_copy, login_as):
    csrftoken = login_as(user)

    response = api_client.post(
        "/api/auctions/",
        {"card_copy_id": card_copy.id, "starting_price": "10.00", "end_time": _future(hours=2)},
        HTTP_X_CSRFTOKEN=csrftoken,
    )

    assert response.status_code == 201, response.data
    assert response.data["status"] == "ACTIVE"
    assert Decimal(response.data["current_price"]) == Decimal("10.00")


def test_cannot_create_auction_for_someone_elses_copy(api_client, other_user, card_copy, login_as):
    csrftoken = login_as(other_user)  # card_copy belongs to `user`, not other_user

    response = api_client.post(
        "/api/auctions/",
        {"card_copy_id": card_copy.id, "starting_price": "10.00", "end_time": _future(hours=2)},
        HTTP_X_CSRFTOKEN=csrftoken,
    )

    assert response.status_code == 400


def test_cannot_list_an_already_listed_copy_twice(api_client, user, card_copy, auction, login_as):
    csrftoken = login_as(user)

    response = api_client.post(
        "/api/auctions/",
        {"card_copy_id": card_copy.id, "starting_price": "10.00", "end_time": _future(hours=2)},
        HTTP_X_CSRFTOKEN=csrftoken,
    )

    assert response.status_code == 400


# ---- edit ---------------------------------------------------------------


def test_seller_can_edit_before_any_bid(api_client, user, auction, login_as):
    csrftoken = login_as(user)

    response = api_client.patch(
        f"/api/auctions/{auction.id}/", {"starting_price": "20.00"}, HTTP_X_CSRFTOKEN=csrftoken
    )

    assert response.status_code == 200, response.data
    assert Decimal(response.data["starting_price"]) == Decimal("20.00")
    assert Decimal(response.data["current_price"]) == Decimal("20.00")


def test_non_seller_cannot_edit(api_client, other_user, auction, login_as):
    csrftoken = login_as(other_user)

    response = api_client.patch(
        f"/api/auctions/{auction.id}/", {"starting_price": "20.00"}, HTTP_X_CSRFTOKEN=csrftoken
    )

    assert response.status_code == 403


def test_cannot_edit_after_a_bid_has_been_placed(api_client, user, other_user, auction, login_as):
    bidder_csrf = login_as(other_user)
    api_client.post(f"/api/auctions/{auction.id}/bid/", {"amount": "15.00"}, HTTP_X_CSRFTOKEN=bidder_csrf)

    seller_csrf = login_as(user)
    response = api_client.patch(
        f"/api/auctions/{auction.id}/", {"starting_price": "5.00"}, HTTP_X_CSRFTOKEN=seller_csrf
    )

    assert response.status_code == 400


# ---- cancel ---------------------------------------------------------------


def test_seller_can_cancel_with_no_bids(api_client, user, auction, login_as):
    csrftoken = login_as(user)

    response = api_client.post(f"/api/auctions/{auction.id}/cancel/", HTTP_X_CSRFTOKEN=csrftoken)

    assert response.status_code == 200
    assert response.data["status"] == "CANCELLED"


def test_cannot_cancel_after_a_bid_has_been_placed(api_client, user, other_user, auction, login_as):
    bidder_csrf = login_as(other_user)
    api_client.post(f"/api/auctions/{auction.id}/bid/", {"amount": "15.00"}, HTTP_X_CSRFTOKEN=bidder_csrf)

    seller_csrf = login_as(user)
    response = api_client.post(f"/api/auctions/{auction.id}/cancel/", HTTP_X_CSRFTOKEN=seller_csrf)

    assert response.status_code == 400


def test_non_seller_cannot_cancel(api_client, other_user, auction, login_as):
    csrftoken = login_as(other_user)

    response = api_client.post(f"/api/auctions/{auction.id}/cancel/", HTTP_X_CSRFTOKEN=csrftoken)

    assert response.status_code == 403


# ---- bidding ---------------------------------------------------------------


def test_seller_cannot_bid_on_own_auction(api_client, user, auction, login_as):
    csrftoken = login_as(user)

    response = api_client.post(
        f"/api/auctions/{auction.id}/bid/", {"amount": "15.00"}, HTTP_X_CSRFTOKEN=csrftoken
    )

    assert response.status_code == 400


def test_bid_below_starting_price_is_rejected(api_client, other_user, auction, login_as):
    csrftoken = login_as(other_user)

    response = api_client.post(
        f"/api/auctions/{auction.id}/bid/", {"amount": "5.00"}, HTTP_X_CSRFTOKEN=csrftoken
    )

    assert response.status_code == 400


def test_bid_raises_the_current_price(api_client, other_user, auction, login_as):
    csrftoken = login_as(other_user)

    response = api_client.post(
        f"/api/auctions/{auction.id}/bid/", {"amount": "10.00"}, HTTP_X_CSRFTOKEN=csrftoken
    )

    assert response.status_code == 201, response.data
    assert Decimal(response.data["current_price"]) == Decimal("10.00")
    assert response.data["bid_count"] == 1


def test_next_bid_must_meet_minimum_increment(api_client, other_user, make_user, auction, login_as):
    second_bidder = make_user(email="carol@example.com")

    first_csrf = login_as(other_user)
    api_client.post(f"/api/auctions/{auction.id}/bid/", {"amount": "10.00"}, HTTP_X_CSRFTOKEN=first_csrf)

    second_csrf = login_as(second_bidder)
    response = api_client.post(
        f"/api/auctions/{auction.id}/bid/", {"amount": "10.50"}, HTTP_X_CSRFTOKEN=second_csrf
    )

    # top bid is 10.00, min_increment defaults to 1.00, so 11.00 is required
    assert response.status_code == 400


def test_bid_at_or_above_buy_now_price_closes_the_auction(
    api_client, card_copy, make_auction, other_user, login_as
):
    auction = make_auction(card_copy, buy_now_price=Decimal("50.00"))
    csrftoken = login_as(other_user)

    response = api_client.post(
        f"/api/auctions/{auction.id}/bid/", {"amount": "50.00"}, HTTP_X_CSRFTOKEN=csrftoken
    )

    assert response.status_code == 201, response.data
    assert response.data["status"] == "SOLD"
    assert response.data["winner"] == other_user.email
    assert Decimal(response.data["final_price"]) == Decimal("50.00")


def test_buy_now_action_closes_the_auction(api_client, card_copy, make_auction, other_user, login_as):
    auction = make_auction(card_copy, buy_now_price=Decimal("50.00"))
    csrftoken = login_as(other_user)

    response = api_client.post(f"/api/auctions/{auction.id}/buy-now/", HTTP_X_CSRFTOKEN=csrftoken)

    assert response.status_code == 200, response.data
    assert response.data["status"] == "SOLD"
    assert response.data["winner"] == other_user.email


def test_buy_now_action_requires_a_buy_now_price(api_client, other_user, auction, login_as):
    csrftoken = login_as(other_user)  # `auction` fixture has no buy_now_price

    response = api_client.post(f"/api/auctions/{auction.id}/buy-now/", HTTP_X_CSRFTOKEN=csrftoken)

    assert response.status_code == 400


def test_cannot_bid_on_an_auction_that_has_already_ended(
    api_client, card_copy, make_auction, other_user, login_as
):
    ended_auction = make_auction(card_copy, end_time=timezone.now() - timedelta(minutes=1))
    csrftoken = login_as(other_user)

    response = api_client.post(
        f"/api/auctions/{ended_auction.id}/bid/", {"amount": "100.00"}, HTTP_X_CSRFTOKEN=csrftoken
    )

    assert response.status_code == 400


# ---- close_expired_auctions management command -----------------------------


def test_close_expired_auctions_sells_to_the_highest_bidder(card_copy, make_auction, other_user):
    ended_auction = make_auction(card_copy, end_time=timezone.now() - timedelta(minutes=1))
    Bid.objects.create(auction=ended_auction, bidder=other_user, amount=Decimal("15.00"))

    call_command("close_expired_auctions")

    ended_auction.refresh_from_db()
    assert ended_auction.status == Auction.Status.SOLD
    assert ended_auction.winner == other_user
    assert ended_auction.final_price == Decimal("15.00")


def test_close_expired_auctions_expires_when_no_bids(card_copy, make_auction):
    ended_auction = make_auction(card_copy, end_time=timezone.now() - timedelta(minutes=1))

    call_command("close_expired_auctions")

    ended_auction.refresh_from_db()
    assert ended_auction.status == Auction.Status.EXPIRED
