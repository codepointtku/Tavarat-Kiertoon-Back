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

from .authenticate import CustomAuthenticationJWT, enforce_csrf
from .models import CustomUser
from .permissions import HasGroupPermission, is_in_group
from .serializers import (
    GroupNameCheckSerializer,
    GroupNameSerializer,
    GroupPermissionsSerializer,
    GroupPermissionsSerializerNames,
    UserSerializer_create,
    UserSerializer_full,
    UserSerializer_limited,
    UserSerializer_names,
    UserSerializer_password,
    UserSerializer_password_2,
    UserSerializer_update,
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


class ExampleAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Get the username and password
        username = request.data.get("email", None)
        password = request.data.get("password", None)
        print("TEST print from example authentication, request is:   ", request.data)

        if not username or not password:
            raise AuthenticationFailed(("No credentials provided."))
            # raise AuthenticationFailed(_('No credentials provided.'))

        credentials = {get_user_model().USERNAME_FIELD: username, "password": password}

        user = authenticate(**credentials)

        if user is None:
            raise AuthenticationFailed(("Invalid username/password."))
            # raise AuthenticationFailed(_('Invalid username/password.'))

        if not user.is_active:
            raise AuthenticationFailed(("User inactive or deleted."))
            # raise AuthenticationFailed(_('User inactive or deleted.'))

        return (user, None)  # authentication successful


class UserCreateListView(APIView):
    """
    List all users, and create with POST
    """

    # need to make this so that only ppl inside turku/customers intra can access this, cehcks?

    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = UserSerializer_names(users, many=True)
        print("test GET")
        return Response(serializer.data)

    def post(self, request, format=None):
        print("test POST")
        serialized_values = UserSerializer_create(data=request.data)
        if serialized_values.is_valid():
            # getting the data form serializer for user creation
            print("Onko printissa ja sitten seriliasoidut data", serialized_values)
            print("vastauksen data:   ", serialized_values.initial_data)
            first_name_post = serialized_values["first_name"].value
            last_name_post = serialized_values["last_name"].value
            name_post = first_name_post + " " + last_name_post
            email_post = serialized_values["email"].value
            phone_number_post = serialized_values["phone_number"].value
            password_post = serialized_values["password"].value

            print("nimi: ", name_post)
            print("email: ", email_post)
            print("phone: ", phone_number_post)
            print("password: ", password_post)

            # checking that user doesnt exist already as email needs to be unique ? redudant due to validation?
            if User.objects.filter(email=email_post).exists():
                print("found user with email of: ", email_post)
            else:
                print("no user with email of: ", email_post)
            # checking that email domain is valid ?
            if "@" not in email_post:
                # could this check be doen in validator along while keeping the other validaitons for the field. - ----- --
                # return Response("invalid email address, has no @", status=status.HTTP_400_BAD_REQUEST)
                pass
            else:
                # no @ in email so creating non email based user I guess???? so no nee to check domain?, should check if location based account is check for security?
                email_split = email_post.split("@")
                if not Validate_email_domain(email_split[1]):
                    print("uh duh??!?!?!")
                    return Response("invalid email domain")

            print(
                "creating user with: ",
                first_name_post,
                last_name_post,
                email_post,
                phone_number_post,
                password_post,
            )
            # actually creating the user
            User.objects.create_user(
                first_name_post,
                last_name_post,
                email_post,
                phone_number_post,
                password_post,
            )

            return Response(serialized_values.initial_data)

        return Response(serialized_values.errors, status=status.HTTP_400_BAD_REQUEST)

        # return Response(serialized_values.initial_data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # User.objects.create_user("derp5", "derpingonton5", "derp5@depr5.derp5", "5555", "123456789")

        return Response("TEST")

    # queryset = CustomUser.objects.all()
    serializer_class = UserSerializer_create


# leaving session and basic auth for easing testing purposes, remove them once deplayed to use only JWT?


class UserView_login(APIView):
    """
    GET the current logged in user and returns it.
    POST to login user manually, access token to http only cookie to user also.
    """

    serializer_class = UserSerializer_password
    authentication_classes = [
        SessionAuthentication,
        # ExampleAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]
    # authentication_classes = [ExampleAuthentication]
    # permission_classes = [IsAuthenticated]

    # permission_classes = [HasGroupPermission]
    # required_groups = {
    #     # "GET": ["user_group", "bicycle_group"],
    #     "GET": ["__all__"],
    #     "POST": ["moderators", "someMadeUpGroup"],
    #     "PUT": ["__all__"],
    # }

    def get(self, request, format=None):
        print("GET request is:  ", request.user)
        if (request.user) == "AnonymousUser":
            content = {
                "user": str(request.user),  # `django.contrib.auth.User` instance.
                "auth": str(request.auth),  # None
            }
            return Response(content)
        else:
            # authentication_classes = [SessionAuthentication, BasicAuthentication]
            # permission_classes = [IsAuthenticated]

            # permission_classes = [HasGroupPermission]
            # required_groups = {
            #     "GET": ["user_group", "bicycle_group"],
            #     # "GET": ["__all__"],
            #     "POST": ["moderators", "someMadeUpGroup"],
            #     "PUT": ["__all__"],
            # }

            content = {
                "user": str(request.user),  # `django.contrib.auth.User` instance.
                "auth": str(request.auth),  # None
            }
            print("current logged on user: ", request.user)
            print("current logged on user that is returned: ", content)
            return Response(content)

    def post(self, request, format=None):
        print("POST request is:   ", request)
        content = {
            "user": str(request.user),  # `django.contrib.auth.User` instance.
            "auth": str(request.auth),  # None
        }

        print("CONNNNNNTEEEENNNTTTT_ _------:", content)
        # test = {"password" : "1234" , "email" : "spsantam"}
        # testing_serial_stuff = UserSerializer_password(data=test)
        # print("TEST seria STUF:      ", testing_serial_stuff)
        # serialized_values_request = UserSerializer_password(data=test)
        serialized_values_request = UserSerializer_password(data=request.data)
        print(
            "test POST",
            serialized_values_request.is_valid(),
            serialized_values_request.errors,
        )
        print(serialized_values_request)
        # if serialized_values_request.is_valid() :

        try:
            email_post = serialized_values_request.initial_data["email"]
            pw_request = serialized_values_request.initial_data["password"]
            print("password: ", pw_request)
        except KeyError:
            # serializer_class = UserSerializer_password
            return Response("no password passed or no email passed")

        print(email_post)
        if User.objects.filter(email=email_post).exists():
            print("found user with email of: ", email_post)
            user = User.objects.get(email=email_post)
            print(user, "\n ------------")
            print("Email: ", user.email, "   and password: ", user.password)

        else:
            print("no user with email of: ", email_post)
            response_message = "no user with email of: " + email_post
            return Response(response_message)

        # if check_password(pw_request,user.password) :
        #     print("fffffffffffffffff")

        data = request.data
        response = Response()

        if check_password(pw_request, user.password):
            message = "Chuck norris kicked you in"
            print(message)
            serialized_response = UserSerializer_limited(user)
            # return Response(message)
            print("request user is:   ", request.user)
            # user_auth = authenticate(request, username=email_post, password=pw_request)
            user_auth = authenticate(username=email_post, password=pw_request)
            print(user_auth)
            if user_auth is not None:
                print("logging in user:   ", user_auth)
                print(
                    "actually lets do the token stuff and active check first----- :  "
                )

                if user_auth.is_active:
                    data = get_tokens_for_user(user_auth)
                    response.set_cookie(
                        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                        value=data["access"],
                        expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                    )
                    csrf.get_token(request)
                    response.data = {"Success": "Login successfully", "data": data}
                    print(
                        "printing the response data with token stuff for example--------:   ",
                        response.data,
                    )
                    login(request, user_auth)
                    return response
                else:
                    return Response(
                        {"No active": "This account is not active!!"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                login(request, user_auth)
            else:
                print("something went wroooong")
                # cool bean chuck noirris there is is so much redaunant code here, suffer from spaghetti code

            current_user_serialized = UserSerializer_full(user_auth)
            return Response(current_user_serialized.data)
            return Response(serialized_response.data)
        else:
            print("Failty password try again")
            return Response("Failty password try again")
        # return Response(serialized_values_request.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("bogos pinted with CHUK NORRIS")
        # return Response(serialized_values_request.initial_data)


class UserView_logout(APIView):
    """
    Logs out the user and flush sessioin
    """

    # should this be used here ? just incase bugs so user can logout
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        print("current user is  ---:     ", request.user)
        logout(request)

        return Response("Logged Out")


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
    serializer_class = UserSerializer_full


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
    serializer_class = UserSerializer_full

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer_full(user)

        # willl be removed alter/moved
        print("testin single user stuff")
        group_name_check = "bicycle_group"
        user_permission_ok = is_in_group(user, group_name_check)
        print(
            "permission to group: ", group_name_check, " ---is--: ", user_permission_ok
        )

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

    # def post(self, request, format=None):
    #     print("test")

    #     Response("test")


class GroupPermissionCheck(APIView):
    """
    check the groups user belongs to and return them
    """

    # authenticaction confirms that the user nad that he was logged in, not permissions. PERSMISSIONs are well permissions if the user has rights to them
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    authentication_classes = [
        JWTAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    ]
    # permission_classes = [IsAuthenticated]
    serializer_class = GroupNameCheckSerializer
    test_message = "this is test amessage does it come out"
    permission_classes = [HasGroupPermission]
    required_groups = {
        "GET": ["user_group"],
        # "GET": ["__all__"],
        "POST": ["user_group"],
        "PUT": ["user_group"],
    }

    def get(self, request, format=None):
        # queryset = Group.objects.all()
        # serializer_class = GroupNameCheckSerializer
        print("permission classes----: ", self.permission_classes)
        content = {
            "user": str(request.user),  # `django.contrib.auth.User` instance.
            "auth": str(request.auth),  # None
        }
        print(self.test_message)
        print("current user is  ---:     ", request.user)
        print("REQUEST headers ---:     ", request.headers)

        # user = User.objects.get(id=request.user.id)
        # print(user)
        serializer = GroupPermissionsSerializerNames(request.user)
        print(serializer.data)
        # print(serializer.data)
        # request_serializer = GroupNameCheckSerializer(data=request.data)

        # print("request users group are ---:   ", request.user)
        # user_id_list = [1, 2, 3, 3, 4, 5]
        # logged_in_users = User.objects.filter(id__in=user_id_list)
        # list_of_logged_in_users = [
        #     {user.id: user.get_name()} for user in logged_in_users
        # ]
        # print(list_of_logged_in_users)
        return Response(serializer.data)
        return Response(content)

    def post(self, request, format=None):
        # queryset = Group.objects.all()
        # sample_data = {"test_boolean_check_email": True}
        print(self.test_message)
        print("user: ", request.user)
        request_serializer = GroupNameCheckSerializer(data=request.data)
        # request_serializer = GroupNameCheckSerializer(sample_data)
        # if request.data["test_boolean_check_email"] or None :
        print(request.data)
        # if request.data["test_boolean_check_email"] == None:
        #     print("request eamil check is false:   -->: ")
        request_serializer.is_valid(raise_exception=True)
        # print(
        #     "test boolean value:   ",
        #     request_serializer,
        # )
        # print(
        #     "test boolean value:   ",
        #     request.data,
        # )
        # if request_serializer.initial_data["test_boolean_check_email"].value:
        #     print("using email from post, not loggd in user")
        # # user = User.objects.get(email=email_post)
        # print(request_serializer.initial_data["group_name"])
        # if request_serializer.is_valid():
        #     print("was valid")
        return Response(request_serializer.data)

        # print("was not valid")
        # return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupPermissionUpdate(generics.RetrieveUpdateAPIView):
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

    queryset = User.objects.all()
    serializer_class = GroupPermissionsSerializer


class UserDetailsListView_limited(APIView):
    """
    Get Users with revelant fields
    """

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]
    # authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        "GET": ["admin_group"],
        "POST": ["admin_group"],
        "PUT": ["admin_group"],
        "PATCH": ["admin_group"],
    }

    def get(self, request, format=None):
        print("REQUEST data:     ", request.data)
        print("REQUEST:     ", request)
        # print("REQUEST header:     ", request)
        users = CustomUser.objects.all()
        serializer = UserSerializer_limited(users, many=True)
        print("test GET")
        print("current user is  ---:     ", request.user)
        print("data in request: ", request.data)
        # print(serializer.data)
        return Response(serializer.data)


class UserDetailsSingleView_limited(APIView):
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
        serializer = UserSerializer_limited(user)
        return Response(serializer.data)


class UserView_update_info(APIView):
    """
    Get logged in users information and update it
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = UserSerializer_update
    queryset = User.objects.all()

    def get(self, request, format=None):
        # print(request.user)
        if str(request.user) == "AnonymousUser":
            message = "PLease log in you are: " + str(request.user)
            print(message)

            return Response(message)
        else:
            print(request.user)
            queryset = User.objects.filter(id=request.user.id)
            print(queryset)
            serialized_data_full = UserSerializer_full(queryset, many=True)
            print(serialized_data_full.data)
            return Response(self.serializer_class(request.user).data)

    def put(self, request, format=None):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserView_password(APIView):
    """
    DO NOT USE RIGHT NOW
    Get single user, and try to check password
    also used for resetting password, but this functionality still no done
    needs more resarching so ignore this spaghetti for now
    currently this was just made to test/practise things
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
        serializer = UserSerializer_password(user)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        print("test POST")
        user = self.get_object(pk)
        serializer = UserSerializer_password(user)
        serialized_values_request = UserSerializer_password(data=request.data)
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

    serializer_class = UserSerializer_password
