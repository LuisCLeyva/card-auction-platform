from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from auctions.models import Auction
from cards.models import Card
from inventory.models import CardCopy

DEFAULT_PASSWORD = "TestPass123!"


@pytest.fixture
def api_client():
    # DRF's test client skips CSRF checks by default; turn enforcement on
    # so these tests exercise the real cookie+header double-submit flow.
    return APIClient(enforce_csrf_checks=True)


@pytest.fixture
def make_user(db):
    counter = {"n": 0}

    def _make_user(email=None, password=DEFAULT_PASSWORD, display_name="Tester"):
        counter["n"] += 1
        email = email or f"user{counter['n']}@example.com"
        return User.objects.create_user(email=email, password=password, display_name=display_name)

    return _make_user


@pytest.fixture
def user(make_user):
    return make_user(email="seller@example.com", display_name="Seller")


@pytest.fixture
def other_user(make_user):
    return make_user(email="bidder@example.com", display_name="Bidder")


@pytest.fixture
def make_card(db):
    counter = {"n": 0}

    def _make_card(**kwargs):
        counter["n"] += 1
        defaults = {
            "card_id": f"OP01-{counter['n']:03d}",
            "name": f"Test Card {counter['n']}",
            "card_type": Card.CardType.CHARACTER,
            "rarity": Card.Rarity.COMMON,
            "cost": 3,
            "power": 3000,
            "color": "Red",
            "set_name": "-ROMANCE DAWN- [OP01]",
        }
        defaults.update(kwargs)
        return Card.objects.create(**defaults)

    return _make_card


@pytest.fixture
def card(make_card):
    return make_card()


@pytest.fixture
def make_card_copy(db):
    def _make_card_copy(owner, card, **kwargs):
        return CardCopy.objects.create(owner=owner, card=card, **kwargs)

    return _make_card_copy


@pytest.fixture
def card_copy(user, card, make_card_copy):
    return make_card_copy(owner=user, card=card)


@pytest.fixture
def make_auction(db):
    def _make_auction(card_copy, **kwargs):
        defaults = {
            "seller": card_copy.owner,
            "starting_price": 10,
            "current_price": 10,
            "end_time": timezone.now() + timedelta(hours=1),
        }
        defaults.update(kwargs)
        return Auction.objects.create(card_copy=card_copy, **defaults)

    return _make_auction


@pytest.fixture
def auction(card_copy, make_auction):
    return make_auction(card_copy)


@pytest.fixture
def login_as(api_client):
    """Log `api_client` in as `user` through the real endpoints, exactly
    like a browser would, and return the csrftoken to echo back as
    X-CSRFToken on subsequent unsafe requests."""

    def _login(user, password=DEFAULT_PASSWORD):
        api_client.get("/api/auth/csrf/")
        csrftoken = api_client.cookies["csrftoken"].value
        response = api_client.post(
            "/api/auth/login/",
            {"email": user.email, "password": password},
            HTTP_X_CSRFTOKEN=csrftoken,
        )
        assert response.status_code == 200, response.data
        return csrftoken

    return _login
