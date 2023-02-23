from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.http import Http404
from django.middleware import csrf
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.authentication import (
    BaseAuthentication,
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .authenticate import CustomAuthenticationJWT, ExampleAuthentication, enforce_csrf
from .models import CustomUser
from .permissions import HasGroupPermission, is_in_group
from .serializers import (
    GroupNameCheckSerializer,
    GroupNameSerializer,
    GroupPermissionsSerializer,
    GroupPermissionsSerializerNames,
    UserSerializerCreate,
    UserSerializerCreateReturn,
    UserSerializerFull,
    UserSerializerLimited,
    UserSerializerNames,
    UserSerializerPassword,
    UserSerializerPassword2,
    UserSerializerUpdate,
)

User = get_user_model()


def Validate_email_domain(email_domain):
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
    !!!!HUOM !!!! ENNEN KUIN USERMIODELIA PÄIVITETÄÄN EI VOIDA TEHDÄ YHTEISKÄYTTÖTILIÄ KUNNOLLA JOTEN TESTAUS MUUTTUJIA
    TL;DR noormi käyttäjät toimivat, yhteiskäyttäjät puoliksi yhteiskäyttäjä EI LUO VIELÄ MITÄÄN
    WIll be cleaned later, ask spsantam for more info
    """

    # queryset = CustomUser.objects.all()
    serializer_class = UserSerializerCreate

    # need to make this so that only ppl inside turku/customers intra can access this, cehcks?,  only admins?

    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = UserSerializerNames(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serialized_values = UserSerializerCreate(data=request.data)

        # temporaty creating the user and amdin groups here, for testing, this should be run first somewhere else
        if not Group.objects.filter(name="user_group").exists():
            Group.objects.create(name="user_group")
        if not Group.objects.filter(name="admin_group").exists():
            Group.objects.create(name="admin_group")
        if not Group.objects.filter(name="storage_group").exists():
            Group.objects.create(name="storage_group")
        if not Group.objects.filter(name="bicycle_group").exists():
            Group.objects.create(name="bicycle_group")

        if serialized_values.is_valid():
            # getting the data form serializer for user creation
            print("vastauksen data:   ", serialized_values.data)
            first_name_post = serialized_values["first_name"].value
            last_name_post = serialized_values["last_name"].value
            name_post = first_name_post + " " + last_name_post
            email_post = serialized_values["email"].value
            phone_number_post = serialized_values["phone_number"].value
            password_post = serialized_values["password"].value
            toimipaikka_post = serialized_values["toimipaikka"].value

            print("nimi: ", name_post)
            print("email: ", email_post)
            print("phone: ", phone_number_post)
            print("password: ", password_post)
            print("toimipaikka: ", toimipaikka_post)

            if not toimipaikka_post:
                print("luodaan normi käyttäjä: ")

                # checking that user doesnt exist already as email needs to be unique ? redudant due to validation from serializer
                if User.objects.filter(email=email_post).exists():
                    print("found user with email of: ", email_post)
                else:
                    print("no user with email of: ", email_post)
                # checking that email domain is valid ? for testing purposes pass with invalid emila addresses, in production always return invalid user name if not email address
                if "@" not in email_post:
                    # could this check be doen in validator along while keeping the other validaitons for the field. - ----- --
                    # return Response("invalid email address, has no @", status=status.HTTP_400_BAD_REQUEST)
                    pass
                else:
                    # no @ in email so creating non email based user I guess???? so no need to check domain?, should check if location based account is check for security?
                    email_split = email_post.split("@")
                    if not Validate_email_domain(email_split[1]):
                        print("uh duh??!?!?!")
                        return Response(
                            "invalid email domain", status=status.HTTP_400_BAD_REQUEST
                        )

                print(
                    "creating user with: ",
                    first_name_post,
                    last_name_post,
                    email_post,
                    phone_number_post,
                    # password_post,
                )
                return_serializer = UserSerializerCreateReturn(
                    data=serialized_values.data
                )
                return_serializer.is_valid()
                # actually creating the user
                User.objects.create_user(
                    first_name_post,
                    last_name_post,
                    email_post,
                    phone_number_post,
                    password_post,
                )

                return Response(return_serializer.data, status=status.HTTP_201_CREATED)
            else:
                # -----------------------------------------------------
                # UNFINISHED STUFF WILLL BE CHANGED
                # -----------------------------------------------------
                print("luoddaan toimipaikka tili: ")
                if serialized_values.data.get("vastuuhenkilo", None) is None:
                    print("must have vastuuhenkilö if crreating toimipaikak tili")

                    return Response(
                        "must have vastuuhenkilö if crreating toimipaikak tili",
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                vastuuhenkilo = serialized_values.data.get("vastuuhenkilo")
                print("vasstuu henkilo on-----: ", vastuuhenkilo)
                if User.objects.filter(email=vastuuhenkilo).exists():
                    print("found user with email of: ", vastuuhenkilo)
                    user = User.objects.get(email=vastuuhenkilo)
                    print(user, "\n ------------")
                    print("Email: ", user.email, "   and password: ", user.password)

                else:
                    print("no user with email of: ", vastuuhenkilo)
                    response_message = "no user with email of: " + vastuuhenkilo
                    return Response(
                        response_message, status=status.HTTP_400_BAD_REQUEST
                    )

                return Response(
                    "DERP Create a creation funktion and then we think, yes user was not created yet",
                    status=status.HTTP_201_CREATED,
                )
        print(serialized_values.errors)
        return Response(serialized_values.errors, status=status.HTTP_400_BAD_REQUEST)


# leaving session and basic auth for easing testing purposes, remove them once deplayed to use only JWT?


class UserViewLogin(APIView):
    """
    GET the current logged in user and returns it. used for checking logged in user
    use jwt-api for actuaal login

    """

    serializer_class = UserSerializerPassword

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]

    def get(self, request, format=None):
        content = {
            "user": str(request.user),  # `django.contrib.auth.User` instance.
            "auth": str(request.auth),  # None
        }
        return Response(content)


class UserViewLogout(APIView):
    """
    Logs out the user and flush session
    """

    def get(self, request):
        logout(request)
        return Response(
            "Logged Out, remember to clear stuff(JWT-token (access_token and refresh_token)) at the front ends local storage.",
            status=status.HTTP_200_OK,
        )


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
    ]
    permission_classes = [IsAuthenticated, HasGroupPermission]

    required_groups = {
        "GET": ["admin_group"],
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
    }

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializerFull


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
    ]
    permission_classes = [IsAuthenticated, HasGroupPermission]

    required_groups = {
        "GET": ["admin_group"],
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
    }

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializerFull

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializerFull(user)

        return Response(serializer.data)


# getting all groups and their names
class GroupListView(generics.ListCreateAPIView):
    """
    Get group names in list
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
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
class GroupNameView(generics.RetrieveUpdateAPIView):
    # class GroupNameView(APIView):
    """
    THIS SHOULD NOT BE USED, DELETE NOT ALLOWED HERE
    Get single group name and allow updating its name
    could be dangerous for functionality refer to other ppl should this be done if really needed
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["admin_group"],
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
        "PATCH": ["admin_group"],
    }

    queryset = Group.objects.all()
    serializer_class = GroupNameSerializer


class GroupPermissionCheck(APIView):
    """
    check the groups user belongs to and return them
    kinda redutant? can be gotten from another views, users too
    """

    authentication_classes = [
        JWTAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    ]
    serializer_class = GroupNameCheckSerializer
    permission_classes = [HasGroupPermission]
    required_groups = {
        "GET": ["user_group"],
        # "GET": ["__all__"],
        "POST": ["user_group"],
        "PUT": ["user_group"],
    }

    def get(self, request, format=None):
        serializer = GroupPermissionsSerializerNames(request.user)
        return Response(serializer.data)

    def post(self, request, format=None):
        request_serializer = GroupNameCheckSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        return Response(request_serializer.data)


class GroupPermissionUpdate(generics.RetrieveUpdateAPIView):
    """
    Update users permissions, should be only allowed to admins, on testing phase allowing fo users
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
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


class UserDetailsListViewLimited(APIView):
    """
    Get Users with revelant fields
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["admin_group"],
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
        "PATCH": ["admin_group"],
    }

    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = UserSerializerLimited(users, many=True)
        return Response(serializer.data)


class UserDetailsSingleViewLimited(APIView):
    """
    Get single user with revelant fields
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["admin_group"],
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
        "PATCH": ["admin_group"],
    }

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializerLimited(user)
        return Response(serializer.data)


class UserViewUpdateInfo(APIView):
    """
    Get logged in users information and update it
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["user_group"],
        "POST": ["user_group"],
        "PUT": ["user_group"],
        "PATCH": ["user_group"],
    }

    serializer_class = UserSerializerUpdate
    queryset = User.objects.all()

    def get(self, request, format=None):
        # redutant probably
        if str(request.user) == "AnonymousUser":
            message = "Please log in you are: " + str(request.user)
            print(message)

            return Response(message)
        else:
            queryset = User.objects.filter(id=request.user.id)
            serialized_data_full = UserSerializerFull(queryset, many=True)
            return Response(UserSerializerLimited(request.user).data)

    def put(self, request, format=None):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewUpdateSingle(generics.RetrieveUpdateAPIView):
    """
    Get specific users info for updating
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["admin_group"],
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
        "PATCH": ["admin_group"],
    }

    serializer_class = UserSerializerUpdate
    queryset = User.objects.all()


class UserViewPassword(APIView):
    """
    DO NOT USE RIGHT NOW
    Get single user, and try to check password (OLD tests)
    also used for resetting password, but this functionality still not done
    needs more resarching so ignore this spaghetti for now
    currently this was just made to test/practise things WILL BE CHANGED
    more info from spsantam
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["admin_group"],
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
        "PATCH": ["admin_group"],
    }

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializerPassword(user)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        print("test POST")
        user = self.get_object(pk)
        serializer = UserSerializerPassword(user)
        serialized_values_request = UserSerializerPassword(data=request.data)
        print(serialized_values_request)
        print("-------------------------------------------")
        print(serializer, "\n -------------------")

        pw_request = serialized_values_request.initial_data["password"]
        pw_database = serializer.data["password"]
        data_serializer = serializer.data

        check_word_for_hash = "pbkdf2_sha256"  # remove once in deplayment??

        print(
            "values to be checked: ENTERERD password:",
            pw_request,
            "DATABASE password: ",
            pw_database,
        )
        password_checked = False
        if check_word_for_hash in pw_database:
            password_checked = check_password(pw_request, pw_database)
        else:
            print("stored password is faulty but chekcing anyway without hashing")
            if pw_request == pw_database:
                print("correct pasword without hashing")
                password_checked = True

        if password_checked:
            print(
                "salasana oikein, password_correct STATUS on: ",
                data_serializer["password_correct"],
            )
            data_serializer["password_correct"] = True
            data_serializer["message_for_user"] = "Your password was CORRECT"
            print("STATUS: ", data_serializer["password_correct"])
        else:
            print(
                "salasana väärin, password_correct STATUS on: ",
                data_serializer["password_correct"],
            )
            data_serializer["password_correct"] = False
            data_serializer["message_for_user"] = "Your password was WRONG"
            print("STATUS: ", data_serializer["password_correct"])

        return Response(data_serializer)

    serializer_class = UserSerializerPassword
