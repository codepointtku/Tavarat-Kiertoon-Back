from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Contact, ContactForm
from .serializers import (
    ContactFormSerializer,
    ContactSerializer,
    ContactSerializer_for_front,
)

# Create your views here.


class ContactFormListView(ListCreateAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer


class ContactFormDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer


class ContactListView(ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer_for_front


class ContactDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer_for_front
