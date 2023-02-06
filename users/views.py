from django.shortcuts import render
from rest_framework import generics

from .models import CustomUser
from .serializers import UserSerializer

# Create your views here.

class UserDetailsListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class UserCreateListView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class UserSingleGetView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer