from django.conf import settings
from django.contrib.auth import authenticate, forms, get_user_model, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import Http404
from django.middleware import csrf
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, permissions, serializers, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.mixins import ListModelMixin
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
from .models import CustomUser, UserAddress
from .permissions import HasGroupPermission
from .serializers import (  # GroupNameCheckSerializer,; GroupPermissionsNamesSerializer,; UserNamesSerializer,
    BooleanValidatorSerializer,
    GroupNameSerializer,
    GroupPermissionsSerializer,
    MessageSerializer,
    UserAddressPostRequestSerializer,
    UserAddressPutRequestSerializer,
    UserAddressSerializer,
    UserCreateReturnSerializer,
    UserCreateSerializer,
    UserFullSerializer,
    UserLimitedSerializer,
    UserLoginPostSerializer,
    UserPasswordChangeEmailValidationSerializer,
    UserPasswordCheckEmailSerializer,
    UserPasswordSerializer,
    UsersLoginResponseSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


def validate_email_domain(email_domain):
    # print("email domain: ", email_domain, "valid email domains: " , settings.VALID_EMAIL_DOMAINS)
    if email_domain in settings.VALID_EMAIL_DOMAINS:
        return True
    return False


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

    @extend_schema(responses=UserCreateReturnSerializer)
    def post(self, request, format=None):
        # extremely uglu validation stuff
        # if some one can make this better it would be good
        # problem is username validation so it passes the real validator (allowed to be empty for normal users)
        # need to swap the email addreess to username before validator for normal users
        # the joint user bool field isnt properly converted to values before its run thoough serialzier
        # if its done in same validator it fucks up the username = email change
        # this works buit is uugly as is this poem too
        # if you want to see the probelm jsut throw request data straight to serializer and validate
        # when creating normal user and have empty user name field

        # so that bool value can be read properly before  actually going into creation checks
        copy_of_request = request.data.copy()
        if "joint_user" in request.data:
            if not request.data["joint_user"]:
                copy_of_request["username"] = request.data["email"]
        else: 
            copy_of_request["username"] = request.data["email"]

        boolval = BooleanValidatorSerializer(data=request.data)
        if boolval.is_valid():
            if not boolval.data["joint_user"]:
                copy_of_request["username"] = request.data["email"]

        serialized_values = UserCreateSerializer(data=copy_of_request)
        # serialized_values = UserCreateSerializer(data=request.data)

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
            joint_user_post = serialized_values["joint_user"].value

            address_post = serialized_values["address"].value
            zip_code_post = serialized_values["zip_code"].value
            city_post = serialized_values["city"].value

            username_post = serialized_values["username"].value

            if not joint_user_post:
                username_post = email_post

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

            return_serializer = UserCreateReturnSerializer(data=serialized_values.data)
            return_serializer.is_valid()

            # create email verification for user creation  /// FOR LATER WHO EVER DOES IT

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
                joint_user=joint_user_post,
            )
            cart_obj = ShoppingCart(user=user)
            cart_obj.save()
            return Response(return_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serialized_values.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    Login with jwt token and as http only cookie
    """

    #serializer_class = UserPasswordSerializer
    serializer_class = UserLoginPostSerializer

    @extend_schema(
        responses=UsersLoginResponseSerializer,
    )
    def post(self, request, format=None):

        pw_data = self.serializer_class(data=request.data)
        pw_data.is_valid()

        user = authenticate(username=pw_data.data["username"], password=pw_data.data["password"])
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
            response_data = UsersLoginResponseSerializer(user, context={'message': msg})
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

    @extend_schema(request=None, responses=UsersLoginResponseSerializer)
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
        serializer_group = UserLimitedSerializer(user)
        response.status_code = status.HTTP_200_OK
        response.data = {
            "username": user.get_username(),
            "Success": "refresh success",
            "groups": serializer_group.data["groups"],
        }

        return response


@extend_schema(exclude=True)
class UserLoginTestView(APIView):
    """
    this view is mainly used for testing purposes
    will be removed later.
    """

    authentication_classes = [
        #     #SessionAuthentication,
        #     #BasicAuthentication,
        #     #JWTAuthentication,
        CustomJWTAuthentication,
    ]
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["user_group"],
        "POST": ["user_group"],
        "PUT": ["user_group"],
        "PATCH": ["user_group"],
    }

    queryset = CustomUser.objects.all()
    serializer_class = UserPasswordSerializer

    def get(self, request):
        print("testing things, on the page now GET")
        print(request.COOKIES)
        content = {
            "user": str(request.user),  # `django.contrib.auth.User` instance.
            "auth": str(request.auth),  # None
        }
        print(content)
        serializer_group = UserLimitedSerializer(request.user)

        return Response(
            {
                "cookies": request.COOKIES,
                "user": content,
                "groups": serializer_group.data["groups"],
            }
        )

    def post(self, request):
        print("testing things POST")
        print(request.COOKIES)
        content = {
            "user": str(request.user),  # `django.contrib.auth.User` instance.
            "auth": str(request.auth),  # None
        }
        print(content)
        serializer_class = UserPasswordSerializer

        return Response(request.COOKIES)


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

    def get(self, request):
        response = self.jwt_logout(request)
        return response

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

    required_groups = {
        "GET": ["admin_group"],
        # "POST": ["admin_group"],
        "PUT": ["admin_group"],
    }

    queryset = CustomUser.objects.all()
    serializer_class = UserFullSerializer


class UserSingleGetView(APIView):
    """
    Get single user with all database fields, no POST here
    """

    # authentication_classes = [SessionAuthentication, BasicAuthentication]
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
    }

    queryset = CustomUser.objects.all()
    serializer_class = UserFullSerializer

    def get(self, request, pk, format=None):
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response("no such user", status=status.HTTP_204_NO_CONTENT)

        serializer = UserFullSerializer(user)

        return Response(serializer.data)

class UserLoggedInDetailView(APIView):
    """
    Get logged in users info
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]
    permission_classes = [IsAuthenticated, HasGroupPermission]

    required_groups = {
        "GET": ["user_group"],
        # "POST": ["user_group"],
        "PUT": ["user_group"],
    }
    queryset = CustomUser.objects.all()
    serializer_class = UserFullSerializer

    def get(self, request, format=None):
        serializer = self.serializer_class(request.user)
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


class UserUpdateInfoView(APIView):
    """
    Get logged in users information and update it.
    only fields that can be changed.
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

    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()

    def get(self, request, format=None):
        user = User.objects.get(id=request.user.id)
        serialized_data = self.serializer_class(user)
        return Response(serialized_data.data)

    def put(self, request, format=None):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserUpdateSingleView(generics.RetrieveUpdateAPIView):
    """
    Get specific users info for updating, field that can be updated
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

            back_reset_url = "http://127.0.0.1:8000/users/password/reset/"
            reset_url_back = f"{back_reset_url}{uid}/{token_for_user}/"
            reset_url = f"{settings.PASSWORD_RESET_URL_FRONT}{uid}/{token_for_user}/"
            message = "heres the password reset link you requested: " + reset_url

            # sending the email
            subject = "Reset password to Tavarat Kiertoon"
            message = "Hi you are trying to reset your Tavarat kiertoon password.\n\n"
            message += f"Please click the following link to reset your user accounts password: {reset_url} \n\n"
            message += "If you did not request this password reset ignore this mail."

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
    the 'uidb64'/'token' variant and GET method is only for testing and should not be used in deployment so DO NOT USE
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
            user.save()

            response = Response()
            response.status_code = status.HTTP_200_OK
            response.data = {"data": serializer.data, "messsage": "pw updated"}

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_204_NO_CONTENT)

    # get is used in testing should not be needed in deployment, will be removed later?
    @extend_schema(
        responses=inline_serializer(
            name="test returns",
            fields={
                "msg": serializers.CharField(),
                "uid": serializers.CharField(),
                "token": serializers.CharField(),
            },
        )
    )
    def get(self, request, *args, **kwargs):
        if "uidb64" not in kwargs or "token" not in kwargs:
            return Response(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        response = Response()
        response.data = {
            "msg: ": "MAGICC!!!!",
            "uid": kwargs["uidb64"],
            "token": kwargs["token"],
        }
        response.status_code = status.HTTP_200_OK

        return response
