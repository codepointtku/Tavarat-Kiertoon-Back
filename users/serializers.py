from rest_framework import serializers

from .models import CustomUser


class UserSerializer_full(serializers.ModelSerializer):
    """
    Serializer for users, all database fields
    """
    class Meta:
        model = CustomUser
        fields = "__all__"
        depth = 1

class UserSerializer_password(serializers.ModelSerializer):
    """
    Serializer for users, checking password fields
    """
    class Meta:
        model = CustomUser
        fields = "email","password"

class UserSerializer_create(serializers.ModelSerializer):
    """
    Serializer for users, in specific format for user creation
    """
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=155)

    class Meta:
        model = CustomUser
        fields = "first_name","last_name","email","phone_number", "password"

class UserSerializer_limited(serializers.ModelSerializer):
    """
    Serializer for users, getting the revelant fields
    """

    class Meta:
        model = CustomUser
        fields = "id","last_login","name", "email","phone_number", "creation_date", "phone_number", "groups"
        depth = 1