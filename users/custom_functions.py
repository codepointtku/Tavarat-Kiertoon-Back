from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int
from django.core.mail import send_mail

from .models import UserSearchWatch

from products.models import Product as ProductModel


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

def check_whole_product(product : ProductModel):

    # from products.models import Product as ProductModel
    # from users.custom_functions import check_whole_product
    # check_whole_product(ProductModel.objects.get(id=66))

    if check_product_watch(product.name):
        print("match found in name")
    else :
        print("no match found in name")
        print("lets check the colors:", product.colors.all())
        
        # print("product.colors", product.colors)

        for color in product.colors.all():
            if check_product_watch(color.name):
                print("colro match found in:", color.name)
                break
        # for color in product.colors :
        #     if check_product_watch(color):
        #         print("found color match")
        #         break

def check_product_watch(product_name):
    """
    Function to check if value is is the watch list
    """


    print("does it come here and delivered value: ", product_name)
    # results = UserSearchWatch.objects.filter(word__contains=product_name)
    # print("results: ", results)
    # print("count: ", results.count())
    any_match_found = False
    # count_matches = 0

    for search in UserSearchWatch.objects.all():
        if search.word in product_name :
            # count_matches += 1
            print("match found in: ", search)
            any_match_found = True
            print("match was: ", search.word, "comapred to ", product_name)
            print("sending mail to adress: ", search.user.email)

            # sending the email
            subject = f"New item available you have set watch for: {product_name}"
            message = (
                f"There was new item for watch word {search.word} you have set.\n\n"
                f"Its name is: {product_name} and can be found int tavarat kiertoon system now \n\n"
            )

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [search.user.email],
                fail_silently=False,
            )

    # print("count of matches found: ", count_matches)
    return any_match_found
    # if results.count() == 0:
    #     return False
    
    # for result in results:
    #     print("iterating thorugh results: ", result)
    #     print("results word: ", result.word, "user: ", result.user)
    #     print("users email: ", result.user.email)

    #     # sending the email
    #     subject = f"New item available you have set watch for: {product_name}"
    #     message = (
    #         f"There was new item for watch word {result.word} you have set.\n\n"
    #         f"Its name is: {product_name} and can be found int tavarat kiertoon systme now \n\n"
    #     )

    #     # send_mail(
    #     #     subject,
    #     #     message,
    #     #     settings.EMAIL_HOST_USER,
    #     #     [user.email],
    #     #     fail_silently=False,
    #     # )

    # return True

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
