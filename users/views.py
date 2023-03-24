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
from rest_framework import generics, permissions, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
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
    UserAddressSerializer,
    UserCreateReturnSerializer,
    UserCreateSerializer,
    UserFullSerializer,
    UserLimitedSerializer,
    UserPasswordChangeEmailValidationSerializer,
    UserPasswordCheckEmailSerializer,
    UserPasswordSerializer,
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

    # def get(self, request, format=None):
    #     users = CustomUser.objects.all()
    #     serializer = UserNamesSerializer(users, many=True)
    #     return Response(serializer.data)

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

        # so that bool value can be read properly
        boolval = BooleanValidatorSerializer(data=request.data)
        copy_of_request = request.data.copy()
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
                if User.objects.filter(username=username_post).exists():
                    response_message = email_post + ". already exists"
                    return Response(
                        response_message, status=status.HTTP_400_BAD_REQUEST
                    )

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

        # print(serialized_values.errors)
        return Response(serialized_values.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    Login with jwt token and as http only cookie
    """

    serializer_class = UserPasswordSerializer

    def post(self, request, format=None):
        data = request.data
        response = Response()
        username = data.get("username", None)
        password = data.get("password", None)
        user = User.objects.get(username=username)

        print(
            "user name view: ", user.username, user.is_active, "<<----- PROBLEM PLACE"
        )
        user = authenticate(username=username, password=password)
        print("user printing in view: ", user)
        if user is not None:
            if user.is_active:
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

                serializer_group = UserLimitedSerializer(user)

                csrf.get_token(request)
                response.status_code = status.HTTP_200_OK
                response.data = {
                    "Success": "Login successfully",
                    "username": serializer_group.data["username"],
                    "groups": serializer_group.data["groups"],
                }
                return response
            else:
                print("print am I in in activyt!!!!!!!!!!!!!!!")
                return Response(
                    {"No active": "This account is not active!!"},
                    status=status.HTTP_204_NO_CONTENT,
                )
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

    def post(self, request, *args, **kwargs):
        if settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"] not in request.COOKIES:
            return Response(
                "refresh token not found", status=status.HTTP_204_NO_CONTENT
            )

        refresh_token = {}
        refresh_token["refresh"] = request.COOKIES["refresh_token"]
        serializer = self.get_serializer(data=refresh_token)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

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
    Logs out the user and flush session  (just in case, mainly for use in testing at back)
    """

    def jwt_logout(self, request):
        logout(request)
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


# should not be used as returns non-necessary things, use the limited views instead as they are used to return nexessary things.
# leaving this here in the case of need
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
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
    }

    queryset = CustomUser.objects.all()
    serializer_class = UserFullSerializer


# should not be used as returns non-necessary things, use the limited views instead as they are used to return necessary things.
# leaving this here in the case of need
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

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserFullSerializer(user)

        return Response(serializer.data)


class UserLoggedInDetailView(APIView):
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
        "GET": ["user_group"],
        "POST": ["user_group"],
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


# getting single  group name and update it
# class GroupNameView(generics.RetrieveUpdateAPIView):
#     # class GroupNameView(APIView):
#     """
#     THIS SHOULD NOT BE USED, DELETE NOT ALLOWED HERE
#     Get single group name and allow updating its name
#     could be dangerous for functionality refer to other ppl should this be done if really needed
#     """

#     authentication_classes = [
#         SessionAuthentication,
#         BasicAuthentication,
#         JWTAuthentication,
#         CustomJWTAuthentication,
#     ]
#     permission_classes = [IsAuthenticated, HasGroupPermission]
#     required_groups = {
#         "GET": ["admin_group"],
#         "POST": ["admin_group"],
#         "PUT": ["admin_group"],
#         "PATCH": ["admin_group"],
#     }

#     queryset = Group.objects.all()
#     serializer_class = GroupNameSerializer


# class GroupPermissionCheckView(APIView):
#     """
#     check the groups user belongs to and return them
#     kinda redutant? can be gotten from another views, users too
#     """

#     authentication_classes = [
#         JWTAuthentication,
#         BasicAuthentication,
#         SessionAuthentication,
#         CustomJWTAuthentication,
#     ]
#     serializer_class = GroupNameCheckSerializer
#     permission_classes = [HasGroupPermission]
#     required_groups = {
#         "GET": ["user_group"],
#         # "GET": ["__all__"],
#         "POST": ["user_group"],
#         "PUT": ["user_group"],
#     }

#     def get(self, request, format=None):
#         serializer = GroupPermissionsNamesSerializer(request.user)
#         return Response(serializer.data)

#     def post(self, request, format=None):
#         request_serializer = GroupNameCheckSerializer(data=request.data)
#         request_serializer.is_valid(raise_exception=True)

#         return Response(request_serializer.data)


class GroupPermissionUpdateView(generics.RetrieveUpdateAPIView):
    """
    Update users permissions, should be only allowed to admins, on testing phase allowing fo users
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]
    permission_classes = [IsAuthenticated, HasGroupPermission]
    # required_groups = {
    #     "GET": ["admin_group"],
    #     "POST": ["admin_group"],
    #     "PUT": ["admin_group"],
    #     "PATCH": ["admin_group"],
    # }
    # use adming_group later, for testing purpose this is on user_group
    required_groups = {
        "GET": ["user_group"],
        "POST": ["user_group"],
        "PUT": ["user_group"],
        "PATCH": ["user_group"],
    }

    queryset = User.objects.all()
    serializer_class = GroupPermissionsSerializer


# class UserDetailsListLimitedView(APIView):
#     """
#     Get Users with revelant fields
#     """

#     authentication_classes = [
#         SessionAuthentication,
#         BasicAuthentication,
#         JWTAuthentication,
#         CustomJWTAuthentication,
#     ]
#     permission_classes = [IsAuthenticated, HasGroupPermission]
#     required_groups = {
#         "GET": ["admin_group"],
#         "POST": ["admin_group"],
#         "PUT": ["admin_group"],
#         "PATCH": ["admin_group"],
#     }

#     def get(self, request, format=None):
#         users = CustomUser.objects.all()
#         serializer = UserLimitedSerializer(users, many=True)
#         return Response(serializer.data)


# class UserDetailLimitedView(APIView):
#     """
#     Get single user with revelant fields
#     """

#     authentication_classes = [
#         SessionAuthentication,
#         BasicAuthentication,
#         JWTAuthentication,
#         CustomJWTAuthentication,
#     ]

#     permission_classes = [IsAuthenticated, HasGroupPermission]
#     required_groups = {
#         "GET": ["admin_group"],
#         "POST": ["admin_group"],
#         "PUT": ["admin_group"],
#         "PATCH": ["admin_group"],
#     }

#     def get_object(self, pk):
#         try:
#             return CustomUser.objects.get(pk=pk)
#         except CustomUser.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         user = self.get_object(pk)
#         serializer = UserLimitedSerializer(user)
#         return Response(serializer.data)


class UserUpdateInfoView(APIView):
    """
    Get logged in users information and update it
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
        "POST": ["user_group"],
        "PUT": ["user_group"],
        "PATCH": ["user_group"],
    }

    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()

    def get(self, request, format=None):
        # redutant probably
        if str(request.user) == "AnonymousUser":
            message = "Please log in you are: " + str(request.user)
            print(message)

            return Response(message)
        else:
            queryset = User.objects.filter(id=request.user.id)
            serialized_data_full = UserFullSerializer(queryset, many=True)
            return Response(UserLimitedSerializer(request.user).data)

    def put(self, request, format=None):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserUpdateSingleView(generics.RetrieveUpdateAPIView):
    """
    Get specific users info for updating
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

    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()


class UserAddressListView(generics.ListAPIView):
    """
    Get list of all addresss users have
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

    serializer_class = UserAddressSerializer
    queryset = UserAddress.objects.all()


class UserAddressAddView(APIView):
    """
    Get list of all addresss logged in user has, and add new one
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
        "POST": ["user_group"],
        "PUT": ["user_group"],
        "PATCH": ["user_group"],
    }

    serializer_class = UserAddressSerializer
    queryset = UserAddress.objects.all()

    def get(self, request, format=None):
        qs = UserAddress.objects.filter(user=request.user.id)
        print(qs)
        serialized_info = UserAddressSerializer(qs, many=True)
        print(serialized_info.data)
        return Response(serialized_info.data)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.data["address"])
        UserAddress.objects.create(
            address=serializer.data["address"],
            zip_code=serializer.data["zip_code"],
            city=serializer.data["city"],
            user=request.user,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAddressEditView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get specific address by id and do update/destroy/ to it
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
        "DELETE": ["admin_group"],
    }

    serializer_class = UserAddressSerializer
    queryset = UserAddress.objects.all()


class UserPasswordResetMailView(APIView):
    serializer_class = UserPasswordCheckEmailSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}, partial=True
        )

        serializer.is_valid(raise_exception=True)
        # creating token for user for pw reset and encoding the uid
        user = User.objects.get(username=serializer.data["username"])
        token_generator = default_token_generator
        token_for_user = token_generator.make_token(user=user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"{settings.PASSWORD_RESET_URL_FRONT}{uid}/{token_for_user}/"
        message = "heres the password reset link you requested: " + reset_url

        send_mail(
            "password reset link",
            message,
            "tavaratkiertoon_backend@testi.fi",
            ["testi@turku.fi"],
            fail_silently=False,
        )

        response = Response()
        response.status_code = status.HTTP_200_OK
        # return the values for testing purpose, remove in deployment
        response.data = {
            "message": message,
            "crypt": uid,
            "token": token_for_user,
        }

        return response


class UserPasswordResetMailValidationView(APIView):
    serializer_class = UserPasswordChangeEmailValidationSerializer

    # @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(id=serializer.data["uid"])
        user.set_password(serializer.data["new_password"])
        user.save()

        response = Response()
        response.status_code = status.HTTP_200_OK
        response.data = {"data": serializer.data, "messsage": "pw updatred"}

        return Response(serializer.data, status=status.HTTP_200_OK)

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
