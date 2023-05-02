from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Contact, ContactForm
from .serializers import (
    ContactFormResponseSerializer,
    ContactFormSerializer,
    ContactSerializer,
)

# Create your views here.


class ContactFormListView(ListCreateAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer

    @extend_schema(responses=ContactFormResponseSerializer)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(responses=ContactFormResponseSerializer)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ContactFormDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer

    @extend_schema(responses=ContactFormResponseSerializer)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(responses=ContactFormResponseSerializer)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(methods=["PATCH"], exclude=True)
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(responses=ContactFormResponseSerializer)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ContactListView(ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class ContactDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    @extend_schema(methods=["PATCH"], exclude=True)
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
