from rest_framework import serializers

from .models import CustomUser


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for users
    """
    class Meta:
        model = CustomUser
        fields = "__all__"