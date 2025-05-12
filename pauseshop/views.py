from django.shortcuts import render
from datetime import datetime
from .models import Pause
from .serializers import PauseSerializer
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.permissions import HasGroupPermission, is_in_group
from users.views import CustomJWTAuthentication
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist


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


class TodayPauseView(generics.ListAPIView):
    queryset = Pause.objects.all()
    serializer_class = PauseSerializer
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
        CustomJWTAuthentication,
    ]

    def get(self, request, *args, **kwargs):

        instance = Pause.objects.filter(
            start_date__lte=datetime.today(), end_date__gte=datetime.today()
        )
        serializer = PauseSerializer(instance, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PauseEditView(APIView):
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
        "PUT": ["admin_group", "user_group"],
        "DELETE": ["admin_group", "user_group"],
    }

    def put(self, request, pk):
        try:
            instance = Pause.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Pause not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = PauseSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            pause = Pause.objects.get(id=pk)
        except Pause.DoesNotExist:
            return Response(
                {"error": "Pause not found"}, status=status.HTTP_404_NOT_FOUND
            )

        pause.delete()
        return Response(
            {"message": "pause deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
