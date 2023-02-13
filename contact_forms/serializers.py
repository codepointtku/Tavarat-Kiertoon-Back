from rest_framework import serializers

from .models import Contact, ContactForm


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    # phone_number in the form that front wants
    phoneNumber = serializers.ReadOnlyField(source="phone_number")

    class Meta:
        model = Contact
        fields = ["name", "address", "email", "phoneNumber"]
