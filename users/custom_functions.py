from datetime import datetime

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36


def validate_email_domain(email_domain):
    return email_domain in settings.VALID_EMAIL_DOMAINS


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
