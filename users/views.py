from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import UserSerializer_full, UserSerializer_create, UserSerializer_limited, UserSerializer_password

User = get_user_model()

def Validate_email_domain(email_domain):
    #print("email domain: ", email_domain, "valid email domains: " , settings.VALID_EMAIL_DOMAINS)
    if email_domain in settings.VALID_EMAIL_DOMAINS :
        return True
    return False

# Create your views here.

class UserCreateListView(APIView):
    """
    List all users, and create with POST
    """
    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = UserSerializer_full(users, many = True)
        print("test GET")
        return Response(serializer.data)

    def post(self, request, format=None):
        print("test POST")
        serialized_values = UserSerializer_create(data=request.data)
        if serialized_values.is_valid():
            #getting the data form serializer for user creation
            print("Onko printissa ja sitten seriliasoidut data", serialized_values)
            print("vastauksen data:   ", serialized_values.initial_data )
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

            #checking that user doesnt exist already as email needs to be unique ? redudant due to validation?
            if User.objects.filter(email=email_post).exists() :
                print("found user with email of: ", email_post)
            else:
                print("no user with email of: ", email_post)
            #checking that email domain is valid ?
            email_split = email_post.split("@")
            if not Validate_email_domain(email_split[1]):
                print("uh duh??!?!?!")
                return Response("invalid email domain")
            
            print("creating user with: ", first_name_post, last_name_post, email_post, phone_number_post, password_post)
            #actually creating the user
            User.objects.create_user(first_name_post, last_name_post, email_post, phone_number_post, password_post)

            return Response(serialized_values.initial_data)

        return Response(serialized_values.errors, status=status.HTTP_400_BAD_REQUEST)

        #return Response(serialized_values.initial_data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        #User.objects.create_user("derp5", "derpingonton5", "derp5@depr5.derp5", "5555", "123456789")

        return Response("TEST")

    # queryset = CustomUser.objects.all()  
    serializer_class = UserSerializer_create
    

class UserDetailsListView(generics.ListCreateAPIView):
    """
    List all users
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer_full

class UserSingleGetView(APIView):
    """
    Get single user
    """
    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer_full(user)
        return Response(serializer.data)

    # queryset = CustomUser.objects.all()
    # serializer_class = UserSerializer_full


class UserDetailsListView_limited(APIView):
    """
    Get Users with revelant fields
    """
    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = UserSerializer_limited(users, many = True)
        print("test GET")
        return Response(serializer.data)

class UserView_password(APIView):
    """
    Get single user, password
    """
    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer_password(user)
        return Response(serializer.data)