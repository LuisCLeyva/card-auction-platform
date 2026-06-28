from django.conf import settings
from django.middleware.csrf import get_token
from rest_framework import generics, permissions, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer


def set_auth_cookies(response, access, refresh=None):
    access_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
    response.set_cookie(
        settings.JWT_AUTH_COOKIE,
        str(access),
        max_age=int(access_lifetime.total_seconds()),
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path=settings.JWT_COOKIE_PATH,
    )
    if refresh is not None:
        refresh_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
        response.set_cookie(
            settings.JWT_REFRESH_COOKIE,
            str(refresh),
            max_age=int(refresh_lifetime.total_seconds()),
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            path=settings.JWT_COOKIE_PATH,
        )


def clear_auth_cookies(response):
    response.delete_cookie(settings.JWT_AUTH_COOKIE, path=settings.JWT_COOKIE_PATH)
    response.delete_cookie(settings.JWT_REFRESH_COOKIE, path=settings.JWT_COOKIE_PATH)


class CsrfView(APIView):
    """Frontend calls this once on load so the browser receives a readable
    `csrftoken` cookie; it must echo the value back as `X-CSRFToken` on any
    POST/PUT/PATCH/DELETE request."""

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"detail": get_token(request)})


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        response = Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        set_auth_cookies(response, refresh.access_token, refresh)
        return response


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            # With no authenticator configured on this view, DRF would
            # otherwise coerce this to 403 (it only emits 401 when an
            # authenticator can supply a WWW-Authenticate header).
            return Response({"detail": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

        access = serializer.validated_data["access"]
        refresh = serializer.validated_data["refresh"]
        response = Response(UserSerializer(serializer.user).data, status=status.HTTP_200_OK)
        set_auth_cookies(response, access, refresh)
        return response


class RefreshView(APIView):
    """Deliberately skips CookieJWTAuthentication: this endpoint exists to
    issue a new access token precisely when the old one is expired, so it
    must not require a *valid* access token (or its CSRF check) to run."""

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        if not raw_refresh:
            return Response(
                {"detail": "Refresh cookie missing."}, status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = TokenRefreshSerializer(data={"refresh": raw_refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            response = Response(
                {"detail": "Refresh token invalid or expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            clear_auth_cookies(response)
            return response

        access = serializer.validated_data["access"]
        new_refresh = serializer.validated_data.get("refresh")
        response = Response({"detail": "refreshed"}, status=status.HTTP_200_OK)
        set_auth_cookies(response, access, new_refresh)
        return response


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        if raw_refresh:
            try:
                RefreshToken(raw_refresh).blacklist()
            except TokenError:
                pass

        response = Response({"detail": "logged out"}, status=status.HTTP_200_OK)
        clear_auth_cookies(response)
        return response


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
