from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.http import Http404
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import (
    GroupNameCheckSerializer,
    GroupNameSerializer,
    UserSerializer_create,
    UserSerializer_full,
    UserSerializer_limited,
    UserSerializer_names,
    UserSerializer_password,
    UserSerializer_password_2,
)

User = get_user_model()


def Validate_email_domain(email_domain):
    # print("email domain: ", email_domain, "valid email domains: " , settings.VALID_EMAIL_DOMAINS)
    if email_domain in settings.VALID_EMAIL_DOMAINS:
        return True
    return False


def is_in_group(user, group_name):
    """
    Takes a user and a group name, and returns `True` if the user is in that group.
    """
    try:
        return Group.objects.get(name=group_name).user_set.filter(id=user.id).exists()
    except Group.DoesNotExist:
        return None


# Create your views here.


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


class UserView_login(APIView):
    serializer_class = UserSerializer_password

    def get(self, request, format=None):
        if (request.user) == "AnonymousUser":
            content = {
                "user": str(request.user),  # `django.contrib.auth.User` instance.
                "auth": str(request.auth),  # None
            }
            return Response(content)
        else:
            authentication_classes = [SessionAuthentication, BasicAuthentication]
            permission_classes = [IsAuthenticated]
            content = {
                "user": str(request.user),  # `django.contrib.auth.User` instance.
                "auth": str(request.auth),  # None
            }
            print("current logged on user: ", request.user)
            return Response(content)

    def post(self, request, format=None):
        print(request)
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

        if check_password(pw_request, user.password):
            message = "Chuck norris kicked you in"
            serialized_response = UserSerializer_limited(user)
            # return Response(message)

            user_auth = authenticate(request, username=email_post, password=pw_request)
            print(user_auth)
            if user_auth is not None:
                print("logging in user")
                login(request, user_auth)
            else:
                print("something went wroooong")
                # cool bean chuck noirris there is is so much redaunant code here, suffer from spaghetti code
            current_user_serialized = UserSerializer_full(request.user)
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
    Logs out the user
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

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer_full


# should not be used as returns non-necessary things, use the limited views instead as they are used to return necessary things.
# leaving this here in the case of need
class UserSingleGetView(APIView):
    """
    Get single user with all database fields, no POST here
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

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

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Group.objects.all()
    serializer_class = GroupNameSerializer


# getting all groups and their names
class GroupNameView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get single group name and do magic
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Group.objects.all()
    serializer_class = GroupNameSerializer


class GroupPermissionCheck(APIView):
    """
    check the groups user belongs to
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GroupNameCheckSerializer

    def get(self, request, format=None):
        # queryset = Group.objects.all()
        # serializer_class = GroupNameCheckSerializer

        content = {
            "user": str(request.user),  # `django.contrib.auth.User` instance.
            "auth": str(request.auth),  # None
        }

        print("current user is  ---:     ", request.user)

        user_id_list = [1, 2, 3, 3, 4, 5]
        logged_in_users = User.objects.filter(id__in=user_id_list)
        list_of_logged_in_users = [
            {user.id: user.get_name()} for user in logged_in_users
        ]
        print(list_of_logged_in_users)
        return Response(content)

    def post(self, request, format=None):
        # queryset = Group.objects.all()
        # sample_data = {"test_boolean_check_email": True}
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


class UserDetailsListView_limited(APIView):
    """
    Get Users with revelant fields
    """

    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = UserSerializer_limited(users, many=True)
        print("test GET")
        print("current user is  ---:     ", request.user)
        # print(serializer.data)
        return Response(serializer.data)


class UserDetailsSingleView_limited(APIView):
    """
    Get single user with revelant fields
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer_limited(user)
        return Response(serializer.data)


class UserView_password(APIView):
    """
    Get single user, password
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

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
            print("STATUS: ", data_serializer["password_correct"])
        else:
            print(
                "salasana väärin, password_correct STATUS on: ",
                data_serializer["password_correct"],
            )
            data_serializer["password_correct"] = False
            print("STATUS: ", data_serializer["password_correct"])

        return Response(data_serializer)

    serializer_class = UserSerializer_password
