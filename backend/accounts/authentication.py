from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck
from rest_framework_simplejwt.authentication import JWTAuthentication


def enforce_csrf(request):
    """Run the same CSRF check DRF's SessionAuthentication runs.

    httpOnly cookies stop JavaScript from reading the JWT (mitigating XSS
    token theft) but the browser still attaches the cookie automatically on
    cross-site requests, so CSRF protection is still required for any
    state-changing request authenticated via cookie.
    """

    def dummy_get_response(request):  # pragma: no cover
        return None

    check = CSRFCheck(dummy_get_response)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")


class CookieJWTAuthentication(JWTAuthentication):
    """Reads the SimpleJWT access token from an httpOnly cookie instead of
    the Authorization header, and CSRF-protects unsafe methods."""

    def authenticate(self, request):
        raw_token = request.COOKIES.get(settings.JWT_AUTH_COOKIE)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        if request.method not in ("GET", "HEAD", "OPTIONS"):
            enforce_csrf(request)

        return self.get_user(validated_token), validated_token
