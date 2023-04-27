from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication


def enforce_csrf(request):
    # all examples show that CSRFCheck should not require parameters to work but it doesnt work and igves error
    check = CSRFCheck(
        request
    )  # <-- this line is said problem, someone could look and understand it. but it works with this parameter right
    check.process_request(request)

    reason = check.process_view(request, None, (), {})
    if reason:
        raise PermissionDenied("CSRF Failed: %s" % reason)


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"]) or None
        else:
            raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        enforce_csrf(request)
        return self.get_user(validated_token), validated_token


class ourJWTauth(OpenApiAuthenticationExtension):
    # target_class = "tavarat_kiertoon.users.authenticate.CustomJWTAuthentication"
    target_class = CustomJWTAuthentication
    name = "CustomJWTAuthentication"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": settings.SIMPLE_JWT["AUTH_COOKIE"],
        }
