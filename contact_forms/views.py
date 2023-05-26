from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination

from .models import Contact, ContactForm
from .serializers import (
    ContactFormResponseSerializer,
    ContactFormSerializer,
    ContactSerializer,
)

# Create your views here.


class ContactFormListPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"


class ContactFormFilter(filters.FilterSet):
    class Meta:
        model = ContactForm
        fields = ["status"]


@extend_schema_view(
    get=extend_schema(responses=ContactFormResponseSerializer),
    post=extend_schema(responses=ContactFormResponseSerializer),
)
class ContactFormListView(ListCreateAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer
    filter_backends = [OrderingFilter, filters.DjangoFilterBackend]
    ordering_fields = ["id"]
    ordering = ["-id"]
    filterset_class = ContactFormFilter
    pagination_class = ContactFormListPagination


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
