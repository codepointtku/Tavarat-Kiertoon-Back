from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Bulletin, BulletinSubject
from .serializers import BulletinSerializer, BulletinSubjectSerializer


# Create your views here.
class BulletinListView(ListCreateAPIView):
    queryset = Bulletin.objects.all()
    serializer_class = BulletinSerializer


class BulletinDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Bulletin.objects.all()
    serializer_class = BulletinSerializer


class BulletinSubjectListView(ListCreateAPIView):
    queryset = BulletinSubject.objects.all()
    serializer_class = BulletinSubjectSerializer


class BulletinSubjectDetailView(RetrieveUpdateDestroyAPIView):
    queryset = BulletinSubject.objects.all()
    serializer_class = BulletinSubjectSerializer
