from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Contact, ContactForm
from .serializers import (
    ContactFormResponseSerializer,
    ContactFormSerializer,
    ContactSerializer,
)


# Create your views here.
@extend_schema_view(
    get=extend_schema(responses=ContactFormResponseSerializer),
    post=extend_schema(responses=ContactFormResponseSerializer),
)
class ContactFormListView(ListCreateAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["id"]
    ordering = ["-id"]


@extend_schema_view(
    get=extend_schema(responses=ContactFormResponseSerializer),
    put=extend_schema(responses=ContactFormResponseSerializer),
    patch=extend_schema(exclude=True),
)
class ContactFormDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer


class ContactListView(ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["id"]
    ordering = ["-id"]


@extend_schema_view(patch=extend_schema(exclude=True))
class ContactDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
