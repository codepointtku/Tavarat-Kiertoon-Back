from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.filters import OrderingFilter

from .models import Bulletin, BulletinSubject
from .serializers import BulletinSerializer, BulletinSubjectSerializer


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


class BulletinSubjectListView(ListCreateAPIView):
    queryset = BulletinSubject.objects.all()
    serializer_class = BulletinSubjectSerializer


class BulletinSubjectDetailView(RetrieveUpdateDestroyAPIView):
    queryset = BulletinSubject.objects.all()
    serializer_class = BulletinSubjectSerializer
