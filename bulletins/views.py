from django.shortcuts import render
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Bulletin
from .serializers import BulletinSerializer


# Create your views here.
class BulletinListView(ListCreateAPIView):
    queryset = Bulletin.objects.all()
    serializer_class = BulletinSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["id"]
    ordering = ["-id"]


class BulletinDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Bulletin.objects.all()
    serializer_class = BulletinSerializer
