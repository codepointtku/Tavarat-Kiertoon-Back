from django.shortcuts import render
from .models import Pause
from .serializers import PauseSerializer
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.permissions import HasGroupPermission, is_in_group
from users.views import CustomJWTAuthentication
from rest_framework.response import Response
from rest_framework import generics, status


# Shows when store is on hiatus
class PauseView(generics.ListCreateAPIView):
    queryset = Pause.objects.all()
    serializer_class = PauseSerializer
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    permission_classes = [HasGroupPermission]
    required_groups = {
        "POST": ["admin_group", "user_group"],
    }
