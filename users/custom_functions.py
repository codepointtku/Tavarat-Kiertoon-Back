from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int

from products.models import Product as ProductModel

from .models import UserSearchWatch


def validate_email_domain(email):
    if "@" in email:
        email_split = email.split("@", 1)
        return email_split[1] in settings.VALID_EMAIL_DOMAINS
    return False


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


def check_whole_product(product: ProductModel, color_search=False) -> bool:
    """
    Takes product and performs the product watch search for it.
    Currently searches match in product.name
    giving color_search true also causes search in product.colors
    """

    # for use of shell quick copepaste for testing
    # from products.models import Product as ProductModel
    # from users.custom_functions import check_whole_product
    # check_whole_product(ProductModel.objects.get(id=66))

    match_found = False

    if check_product_watch(product.name):
        match_found = True

    if color_search:
        for color in product.colors.all():
            if check_product_watch(
                color.name, additional_info=f"Color match in {product.name}: "
            ):
                match_found = True
                break

    return match_found


def check_product_watch(product_name, additional_info="") -> bool:
    """
    Function to check if value is is the watch list and sends email to person with match.
    returns True if match is found, False if no match
    """

    any_match_found = False

    for search in UserSearchWatch.objects.all():
        if search.word in product_name:
            any_match_found = True

            subject = f"New item available you have set watch for: {product_name}"
            message = (
                f"There was new item for watch word: {search.word}, you have set.\n\n"
                f"Its name is: {additional_info}{product_name} and can be found in tavarat kiertoon system now \n\n"
            )

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [search.user.email],
                fail_silently=False,
            )

    return any_match_found


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
