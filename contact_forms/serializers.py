from rest_framework import serializers

from .models import Contact, ContactForm


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = "__all__"


class ContactFormResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = "__all__"
        extra_kwargs = {"order_id": {"required": True}, "status": {"required": True}}


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"
