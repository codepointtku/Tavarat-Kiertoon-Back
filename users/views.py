from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.signing import Signer
from django.middleware import csrf
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, serializers, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase

from orders.models import ShoppingCart

from .authenticate import CustomJWTAuthentication
from .custom_functions import validate_email_domain
from .models import CustomUser, UserAddress
from .permissions import HasGroupPermission
from .serializers import (
    GroupNameSerializer,
    GroupPermissionsResponseSchemaSerializer,
    GroupPermissionsSerializer,
    MessageSerializer,
    NewEmailFinishValidationSerializer,
    NewEmailSerializer,
    UserAddressPostRequestSerializer,
    UserAddressPutRequestSerializer,
    UserAddressSerializer,
    UserCreateReturnResponseSchemaSerializer,
    UserCreateReturnSerializer,
    UserCreateSerializer,
    UserFullResponseSchemaSerializer,
    UserFullSerializer,
    UserLoginPostSerializer,
    UserPasswordChangeEmailValidationSerializer,
    UserPasswordCheckEmailSerializer,
    UsersLoginRefreshResponseSchemaSerializer,
    UsersLoginRefreshResponseSerializer,
    UserTokenValidationSerializer,
    UserUpdateReturnSchemaSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


# def validate_email_domain(email_domain):
#     # print("email domain: ", email_domain, "valid email domains: " , settings.VALID_EMAIL_DOMAINS)
#     if email_domain in settings.VALID_EMAIL_DOMAINS:
#         return True
#     return False


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# Create your views here.


class UserCreateListView(APIView):
    """
    List all users, and create with POST
    """

    # queryset = CustomUser.objects.all()
    serializer_class = UserCreateSerializer

    @extend_schema(responses=UserCreateReturnResponseSchemaSerializer)
    def post(self, request, format=None):
        # if no username field comes in request = normal user and email will be copied to username
        # if username comes it means the user will be "joint_user" and user will use the transmitted username
        # this is performed in the serializer validations.

        serialized_values = UserCreateSerializer(data=request.data)

        if serialized_values.is_valid():
            # temporaty creating the user and admin groups here, for testing, this should be run first somewhere else
            if not Group.objects.filter(name="user_group").exists():
                Group.objects.create(name="user_group")
            if not Group.objects.filter(name="admin_group").exists():
                Group.objects.create(name="admin_group")
            if not Group.objects.filter(name="storage_group").exists():
                Group.objects.create(name="storage_group")
            if not Group.objects.filter(name="bicycle_group").exists():
                Group.objects.create(name="bicycle_group")
            # getting the data form serializer for user creation and necessary checks
            first_name_post = serialized_values["first_name"].value
            last_name_post = serialized_values["last_name"].value
            email_post = serialized_values["email"].value
            phone_number_post = serialized_values["phone_number"].value
            password_post = serialized_values["password"].value

            address_post = serialized_values["address"].value
            zip_code_post = serialized_values["zip_code"].value
            city_post = serialized_values["city"].value

            username_post = serialized_values["username"].value

            # checking that email domain is valid
            # checking email domain
            if "@" not in email_post:
                return Response(
                    "Not a valid email address",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            email_split = email_post.split("@")
            if not validate_email_domain(email_split[1]):
                return Response(
                    "invalid email domain", status=status.HTTP_400_BAD_REQUEST
                )

            # actually creating the user
            user = User.objects.create_user(
                first_name=first_name_post,
                last_name=last_name_post,
                email=email_post,
                phone_number=phone_number_post,
                password=password_post,
                address=address_post,
                zip_code=zip_code_post,
                city=city_post,
                username=username_post,
            )
            cart_obj = ShoppingCart(user=user)
            cart_obj.save()

            # create email verification for user creation
            if settings.TEST_DEBUG:  # settings.DEBUG:
                # print("debug päällä, activating user without email")
                activate_url_back = (
                    "debug on, user auto activated no need to visit activation place"
                )
                user.is_active = True
                user.save()
            else:
                token_generator = default_token_generator
                token_for_user = token_generator.make_token(user=user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # back urls are only for testing purposes and to ease development to quickly access right urls
                # should be removed when in deplayment stage from response
                back_activate_url = "http://127.0.0.1:8000/users/activate/"
                activate_url_back = f"back: {back_activate_url}     front: {settings.USER_ACTIVATION_URL_FRONT}{uid}/{token_for_user}/"  # {uid}/{token_for_user}/"
                activate_url = (
                    f"{settings.USER_ACTIVATION_URL_FRONT}{uid}/{token_for_user}/"
                )
                message = (
                    "heres the activation link for tavarat kiertoon: " + activate_url
                )

                # sending activation email
                subject = "welcome to use Tavarat Kiertoon"
                message = (
                    "Hi you have created account for tavarat kiertoon.\n\n"
                    f"Please click the following link to activate your account: {activate_url} \n\n"
                    "If you did not request account creation to tavarat kiertoon, ignore this mail."
                )

                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )

            return_serializer = UserCreateReturnSerializer(
                data=serialized_values.data, context={"message": activate_url_back}
            )
            return_serializer.is_valid()

            return Response(return_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serialized_values.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(responses=MessageSerializer)
class UserActivationView(APIView):
    """
    view for user activation. front passess the uid and token that gets validated and then user gets activated.
    """

    serializer_class = UserTokenValidationSerializer

    def post(self, request, format=None, *args, **kwargs):
        # serializer is used to validate the data send, matching passwords and uid decode and token check
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            # activating the user
            user = User.objects.get(id=serializer.data["uid"])
            user.is_active = True
            user.save()

            return Response("user activated", status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_204_NO_CONTENT)


class UserLoginView(APIView):
    """
    Login with jwt token and as http only cookie
    """

    serializer_class = UserLoginPostSerializer

    @extend_schema(
        responses=UsersLoginRefreshResponseSchemaSerializer,
    )
    def post(self, request, format=None):
        pw_data = self.serializer_class(data=request.data)
        pw_data.is_valid()

        user = authenticate(
            username=pw_data.data["username"], password=pw_data.data["password"]
        )
        if user is not None:
            response = Response()
            # setting the jwt tokens as http only cookie to "login" the user
            data = get_tokens_for_user(user)
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=data["access"],
                expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            )
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                value=data["refresh"],
                expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
                max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            )

            msg = "Login successfully"
            response_data = UsersLoginRefreshResponseSerializer(
                user, context={"message": msg}
            )
            csrf.get_token(request)
            response.status_code = status.HTTP_200_OK
            response.data = response_data.data
            return response

        else:
            return Response(
                {"Invalid": "Invalid username or password!!"},
                status=status.HTTP_204_NO_CONTENT,
            )


class UserTokenRefreshView(TokenViewBase):
    """
    Takes refresh token from cookies and if its valid sets new access token to cookies
    """

    _serializer_class = api_settings.TOKEN_REFRESH_SERIALIZER

    @extend_schema(request=None, responses=UsersLoginRefreshResponseSchemaSerializer)
    def post(self, request, *args, **kwargs):
        # check that refresh cookie is found
        if settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"] not in request.COOKIES:
            return Response(
                "refresh token not found", status=status.HTTP_204_NO_CONTENT
            )

        # serializer imported from the jwt token package performs the token validation
        refresh_token = {}
        refresh_token["refresh"] = request.COOKIES["refresh_token"]
        serializer = self.get_serializer(data=refresh_token)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # setting the access token jwt cookie
        response = Response()
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=serializer.validated_data["access"],
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
        )

        # put here what other information front needs from refresh. like users groups need be in list form
        refresh_token_obj = RefreshToken(refresh_token["refresh"])
        user_id = refresh_token_obj["user_id"]
        user = User.objects.get(id=user_id)
        msg = "Refresh succeess"
        response_data = UsersLoginRefreshResponseSerializer(
            user, context={"message": msg}
        )
        response.status_code = status.HTTP_200_OK
        response.data = response_data.data

        return response


class UserLogoutView(APIView):
    """
    Logs out the user and (flush session just in case, mainly for use in testing at back)
    """

    serializer_class = None

    def jwt_logout(self, request):
        logout(request)
        # deleting the http only jwt cookies that are used as login session
        response = Response()
        if settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"] in request.COOKIES:
            response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])

        if settings.SIMPLE_JWT["AUTH_COOKIE"] in request.COOKIES:
            response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])

        response.status_code = status.HTTP_200_OK
        response.data = {
            "Success": "log out done here, do the front stuff",
        }
        return response

    def post(self, request):
        response = self.jwt_logout(request)
        return response


class UserListPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"


# class UserFilter(filters.FilterSet):
#     class Meta:
#         model = CustomUser
#         fields = [
#             "name",
#             "email",
#             "phone_number",
#             "username",
#         ]


@extend_schema(responses=UserFullResponseSchemaSerializer)
class UserDetailsListView(generics.ListAPIView):
    """
    List all users with all database fields, no POST here
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]
    permission_classes = [IsAuthenticated, HasGroupPermission]

    pagination_class = UserListPagination
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]

    ordering_fields = ["id", "is_active", "creation_date", "last_login"]
    ordering = ["id"]
    # filterset_class = UserFilter

    required_groups = {
        "GET": ["admin_group"],
        # "POST": ["admin_group"],
        "PUT": ["admin_group"],
    }

    queryset = CustomUser.objects.all()
    serializer_class = UserFullSerializer


@extend_schema_view(
    patch=extend_schema(exclude=True),
    get=extend_schema(responses=UserFullResponseSchemaSerializer),
)
@extend_schema(responses=UserUpdateReturnSchemaSerializer)
class UserUpdateSingleView(generics.RetrieveUpdateAPIView):
    """
    Get specific users info,
    only some field can be updated
    """

    authentication_classes = [
        # SessionAuthentication,
        # BasicAuthentication,
        # JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["admin_group"],
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
        "PATCH": ["admin_group"],
    }

    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()

    def get(self, request, pk, format=None):
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response("no such user", status=status.HTTP_204_NO_CONTENT)

        serializer = UserFullSerializer(user)

        return Response(serializer.data)


# getting all groups and their names
class GroupListView(generics.ListAPIView):
    """
    Get group names in list
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["__all__"],
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
    }

    queryset = Group.objects.all()
    serializer_class = GroupNameSerializer


@extend_schema_view(patch=extend_schema(exclude=True))
@extend_schema(responses=GroupPermissionsResponseSchemaSerializer)
class GroupPermissionUpdateView(generics.RetrieveUpdateAPIView):
    """
    Update users permissions, should be only allowed to admins, on testing phase allowing fo users
    id = user id whose permission will be updated as id/pk parameter in url
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["admin_group"],
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
        "PATCH": ["admin_group"],
    }

    queryset = User.objects.all()
    serializer_class = GroupPermissionsSerializer


@extend_schema_view(
    get=extend_schema(responses=UserFullResponseSchemaSerializer),
    put=extend_schema(responses=UserUpdateReturnSchemaSerializer),
)
class UserUpdateInfoView(APIView):
    """
    Get logged in users information and update it.
    only some fields can be changed.
    """

    authentication_classes = [
        # SessionAuthentication,
        # BasicAuthentication,
        # JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["user_group"],
        "POST": ["user_group"],
        "PUT": ["user_group"],
    }

    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()

    def get(self, request, format=None):
        serializer = UserFullSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, format=None):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAddressEditView(APIView, ListModelMixin):
    """
    Get list of all addresss logged in user has, and edit them
    """

    authentication_classes = [
        # SessionAuthentication,
        # BasicAuthentication,
        # JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["user_group"],
        "POST": ["user_group"],
        "PUT": ["user_group"],
        "PATCH": ["user_group"],
    }

    serializer_class = UserAddressSerializer
    queryset = UserAddress.objects.all()

    def get(self, request, format=None):
        qs = UserAddress.objects.filter(user=request.user.id)
        serialized_info = UserAddressSerializer(qs, many=True)
        return Response(serialized_info.data)

    # used for adding new address to user
    @extend_schema(request=UserAddressPostRequestSerializer)
    def post(self, request, format=None):
        copy_of_request_data = request.data.copy()
        copy_of_request_data["user"] = request.user.id
        serializer = self.serializer_class(data=copy_of_request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # used for updating existing address user has
    @extend_schema(request=UserAddressPutRequestSerializer)
    def put(self, request, format=None):
        if "id" not in request.data:
            msg = "no address id for adress updating"
            return Response(msg, status=status.HTTP_204_NO_CONTENT)

        copy_of_request = request.data.copy()
        address1 = UserAddress.objects.get(id=copy_of_request["id"])

        # checking that only users themselves can change their own adressess
        if address1.user.id != request.user.id:
            msg = "address owner and loggerdin user need to match"
            return Response(msg, status=status.HTTP_204_NO_CONTENT)

        copy_of_request["user"] = str(request.user.id)

        serializer = self.serializer_class(address1, data=copy_of_request, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAddressEditDeleteView(APIView):
    """
    Delete the specific address given in kwargs. address needs to match logged in user id as owner
    """

    authentication_classes = [
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "DELETE": ["user_group"],
    }

    serializer_class = None

    def delete(self, request, *args, **kwargs):
        to_be_deleted_id = kwargs["pk"]

        address = UserAddress.objects.get(id=to_be_deleted_id)

        if request.user.id == address.user.id:
            address_msg = address.address + " " + address.zip_code + " " + address.city
            address.delete()

            return Response(
                f"Successfully deleted: {address_msg}", status=status.HTTP_200_OK
            )

        else:
            # print("user didnt match the  owner of address")
            return Response("Not Done", status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(patch=extend_schema(exclude=True))
class UserAddressAdminEditView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get specific address by id and do update/destroy/ to it
    For use of admins only
    """

    authentication_classes = [
        # SessionAuthentication,
        # BasicAuthentication,
        # JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["admin_group"],
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
        "PATCH": ["admin_group"],
        "DELETE": ["admin_group"],
    }

    serializer_class = UserAddressSerializer
    queryset = UserAddress.objects.all()


class UserPasswordResetMailView(APIView):
    """
    View used to send the reset email to users email address when requested.
    """

    serializer_class = UserPasswordCheckEmailSerializer

    @extend_schema(responses=None)
    def post(self, request, format=None):
        # using serializewr to check that user exists that the pw reset mail is sent to
        serializer = self.serializer_class(
            data=request.data, context={"request": request}, partial=True
        )

        if serializer.is_valid():
            # creating token for user for pw reset and encoding the uid
            user = User.objects.get(username=serializer.data["username"])
            token_generator = default_token_generator
            token_for_user = token_generator.make_token(user=user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # back urls are only for testing purposes and to ease development to quickly access right urls
            # should be removed when in deplayment stage from response
            back_reset_url = "http://127.0.0.1:8000/users/password/reset/"
            reset_url_back = f"{back_reset_url}"  # {uid}/{token_for_user}/"
            reset_url = f"{settings.PASSWORD_RESET_URL_FRONT}{uid}/{token_for_user}/"
            message = "heres the password reset link you requested: " + reset_url

            # sending the email
            subject = "Reset password to Tavarat Kiertoon"
            message = (
                "Hi you are trying to reset your Tavarat kiertoon password.\n\n"
                f"Please click the following link to reset your user accounts password: {reset_url} \n\n"
                "If you did not request this password reset ignore this mail."
            )

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            response = Response()
            response.status_code = status.HTTP_200_OK
            # return the values for testing purpose, remove in deployment as these should go only to users email address
            response.data = {
                "message": message,
                "url": reset_url,
                "back_reset": reset_url_back,
                "crypt": uid,
                "token": token_for_user,
            }

            return response

        return Response(
            "password was send to your user accounts email address",
            status=status.HTTP_200_OK,
        )


class UserPasswordResetMailValidationView(APIView):
    """
    View that handless the password reset producre and updates the pw.
    needs the uid and user token created in UserPasswordResetMailView.
    Also activates the user if for some reason its been activated or needs to be reactivated.
    """

    serializer_class = UserPasswordChangeEmailValidationSerializer

    # @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @extend_schema(responses=MessageSerializer)
    def post(self, request, format=None, *args, **kwargs):
        # serializer is used to validate the data send, matching passwords and uid decode and token check
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        # serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            # updating the users pw in database
            user = User.objects.get(id=serializer.data["uid"])
            user.set_password(serializer.data["new_password"])
            user.is_active = True
            user.save()

            response = Response()
            response.status_code = status.HTTP_200_OK
            response.data = {"data": serializer.data, "messsage": "pw updated"}

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_204_NO_CONTENT)


class UserEmailChangeView(APIView):
    authentication_classes = [
        # SessionAuthentication,
        # BasicAuthentication,
        # JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "POST": ["user_group"],
    }

    serializer_class = NewEmailSerializer

    def post(self, request, format=None):
        # checkign that the new email adress is in allowed range before sending the change email itself
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            print(request.user.id)

            # building the link for changing hte email address
            # Token for user and decoding the uid
            token_generator = default_token_generator
            token_for_user = token_generator.make_token(user=request.user)
            uid = urlsafe_base64_encode(force_bytes(request.user.id))

            # Signing the new email address so that we can check in the change part that it hasnt been tampered.
            # using the token that needs also to be valited and transfered as key
            signer = Signer(key=token_for_user)
            signed_email = signer.sign(serializer.data["new_email"])
            print(signed_email)
            new_email = urlsafe_base64_encode(force_bytes(signed_email))
            # new_email = urlsafe_base64_encode(force_bytes(serializer.data["new_email"]))

            email_unique_portion = f"{uid}/{token_for_user}/{new_email}/"

            email_change_url_front = (
                f"{settings.EMAIL_CHANGE_URL_FRONT}{email_unique_portion}"
            )
            email_change_url_back = "http://127.0.0.1:8000/users/emailchange/finish/"

            all_taht_crap = {
                "uid": uid,
                "token": token_for_user,
                "new_email": new_email,
                "link": email_unique_portion,
                "front": email_change_url_front,
                "back": email_change_url_back,
            }

            print(new_email)

            # sending the email
            subject = "new email address for your Tavarat Kiertoon"
            message = (
                "This email address has been designed as the new contact email address for an account in Tavarat Kiertoon.\n\n"
                f"Please click the following link to finalize this email address change: {email_change_url_front} \n\n"
                "If you did not request this password reset ignore this mail."
            )

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [serializer.data["new_email"]],
                fail_silently=False,
            )

            return Response(
                all_taht_crap,
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                f"non valid email: {serializer.errors}",
                status=status.HTTP_204_NO_CONTENT,
            )


class UserEmailChangeFinishView(APIView):
    serializer_class = NewEmailFinishValidationSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            print("serializer data: ", serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                f"somethign went wrong: {serializer.errors}",
                status=status.HTTP_204_NO_CONTENT,
            )
