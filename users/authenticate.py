from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions

def enforce_csrf(request):
    check = CSRFCheck()
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        
        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        enforce_csrf(request)
        return self.get_user(validated_token), validated_token

# class ExampleAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         # Get the username and password
#         username = request.data.get("email", None)
#         password = request.data.get("password", None)
#         print("TEST print from example authentication, request is:   ", request.data)

#         if not username or not password:
#             raise AuthenticationFailed(("No credentials provided."))
#             # raise AuthenticationFailed(_('No credentials provided.'))

#         credentials = {get_user_model().USERNAME_FIELD: username, "password": password}

#         user = authenticate(**credentials)

#         if user is None:
#             raise AuthenticationFailed(("Invalid username/password."))
#             # raise AuthenticationFailed(_('Invalid username/password.'))

#         if not user.is_active:
#             raise AuthenticationFailed(("User inactive or deleted."))
#             # raise AuthenticationFailed(_('User inactive or deleted.'))

#         return (user, None)  # authentication successful
