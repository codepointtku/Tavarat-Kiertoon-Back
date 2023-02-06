from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import UserSerializer

User = get_user_model()


# Create your views here.

class UserDetailsListView(APIView):
    """
    List all users
    """
    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many = True)
        print("test GET")
        return Response(serializer.data)

    def post(self, request, format=None):
        print("test POST")
        print("test POST, Doont save")
        serialized_values = UserSerializer(data=request.data)
        if serialized_values.is_valid():
            print("Onko printissa ja sitten seriliasoidut data", serialized_values)
            print("vastauksen data:   ",serialized_values.initial_data )

            name_post = serialized_values.initial_data["name"]
            email_post = serialized_values.initial_data["email"]

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
    serializer_class = UserSerializer
    

class UserCreateListView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

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
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # queryset = CustomUser.objects.all()
    # serializer_class = UserSerializer