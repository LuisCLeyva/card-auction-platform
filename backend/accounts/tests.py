import pytest

from accounts.models import User

pytestmark = pytest.mark.django_db


def test_register_creates_user_and_sets_httponly_cookies(api_client):
    response = api_client.post(
        "/api/auth/register/",
        {"email": "new@example.com", "display_name": "New", "password": "StrongPass123!"},
    )

    assert response.status_code == 201
    assert User.objects.filter(email="new@example.com").exists()
    access_cookie = response.cookies["access_token"]
    assert access_cookie["httponly"]
    assert response.cookies["refresh_token"]["httponly"]


def test_register_rejects_weak_password(api_client):
    response = api_client.post(
        "/api/auth/register/",
        {"email": "weak@example.com", "display_name": "Weak", "password": "password"},
    )

    assert response.status_code == 400
    assert not User.objects.filter(email="weak@example.com").exists()


def test_login_with_valid_credentials_returns_user_and_cookies(api_client, user):
    response = api_client.post(
        "/api/auth/login/", {"email": user.email, "password": "TestPass123!"}
    )

    assert response.status_code == 200
    assert response.data["email"] == user.email
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


def test_login_with_wrong_password_fails(api_client, user):
    response = api_client.post(
        "/api/auth/login/", {"email": user.email, "password": "wrong-password"}
    )

    assert response.status_code == 401


def test_me_requires_authentication(api_client):
    response = api_client.get("/api/auth/me/")
    assert response.status_code == 401


def test_me_returns_current_user_once_logged_in(api_client, user, login_as):
    login_as(user)
    response = api_client.get("/api/auth/me/")
    assert response.status_code == 200
    assert response.data["email"] == user.email


def test_logout_clears_auth_cookies(api_client, user, login_as):
    login_as(user)
    response = api_client.post("/api/auth/logout/")
    assert response.status_code == 200
    assert response.cookies["access_token"].value == ""
    assert response.cookies["refresh_token"].value == ""


def test_refresh_issues_a_new_access_token(api_client, user, login_as):
    login_as(user)
    old_access = api_client.cookies["access_token"].value

    response = api_client.post("/api/auth/refresh/")

    assert response.status_code == 200
    assert api_client.cookies["access_token"].value != old_access


def test_mutating_request_without_csrf_header_is_rejected(api_client, user, login_as):
    login_as(user)
    # The browser still attaches the csrftoken cookie automatically (that's
    # the whole CSRF problem), but a cross-site attacker can't read its
    # value to echo it back as the X-CSRFToken header — so omitting the
    # header here simulates a forged cross-site request.
    response = api_client.post("/api/inventory/", {})

    assert response.status_code == 403
