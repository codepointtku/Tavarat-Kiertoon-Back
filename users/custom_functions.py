from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Color, Product

from .models import SearchWatch


def validate_email_domain(email):
    if "@" in email:
        email_split = email.split("@", 1)
        return email_split[1] in settings.VALID_EMAIL_DOMAINS
    return False


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def cookie_setter(key, value, remember_me, response):
    if remember_me:
        expires = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME_REMEMBER_ME"]
        max_age = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME_REMEMBER_ME"]
    elif key == "refresh_token":
        expires = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
        max_age = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
    else:
        expires = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        max_age = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]

    response.set_cookie(
        key=key,
        value=value,
        expires=expires,
        max_age=max_age,
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
    )


def check_product_watch(product: Product, additional_info="") -> bool:
    """
    Function to check if all search words and colors of the watch list is found in product and sends email to person with match.
    """

    colors = [color.name.lower() for color in Color.objects.all()]
    product_colors = [color.name.lower() for color in product.colors.all()]
    for search in SearchWatch.objects.all():
        match = True
        for word in search.words:
            if word.lower() in colors:
                if word.lower() not in product_colors:
                    match = False
                    break
            elif word not in product.name.lower():
                match = False
                break
        if match:
            subject = f"New item available you have set watch for: {product.name}"
            message = (
                f"There was new item for watch words: {', '.join(search.words)} you have set.\n\n"
                f"Its name is: {additional_info}{product.name} and can be found in tavarat kiertoon system now."
                f"\n\nDirect link to product: {settings.URL_FRONT}tuotteet/{product.id}"
                f"\n\nIf you want to remove this search watch visit: [FRONTIN OSOTE TÄHÄN KUN VALMIS]"
            )

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [search.user.email],
                fail_silently=False,
            )


class CustomTimeTokenGenerator(PasswordResetTokenGenerator):
    """
    copy of PasswordResetTokenGenerator,
    with just the settings.PASSWORD_RESET_TIMEOUT changed so that we can use different time for activation email time out.
    """

    def check_token(self, user, token):
        """
        Check that a password reset token is correct for a given user.
        """
        if not (user and token):
            return False
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(
                self._make_token_with_timestamp(user, ts, secret),
                token,
            ):
                break
        else:
            return False

        # Check the timestamp is within limit.
        if (self._num_seconds(self._now()) - ts) > settings.USER_CREATION_TIMEOUT:
            return False

        return True


custom_time_token_generator = CustomTimeTokenGenerator()
