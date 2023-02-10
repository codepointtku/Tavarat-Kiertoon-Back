from django.shortcuts import render
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)

from .models import ContactForm, Contacts
from .serializers import ContactFormSerializer, ContactsSerializer

# Create your views here.


class ContactFormListView(ListCreateAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer


class ContactFormDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer

class ContactsDetailView(ListCreateAPIView):
    queryset = Contacts.objects.all()
    serializer_class = ContactsSerializer