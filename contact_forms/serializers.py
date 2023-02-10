from rest_framework import serializers

from .models import Contact, ContactForm


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    phoneNumber = serializers.ReadOnlyField(source="phone_number")

    class Meta:
        model = Contact
        fields = "__all__"
