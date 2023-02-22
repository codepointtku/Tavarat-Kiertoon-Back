from django.contrib.auth.models import Group
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

    password_correct = serializers.BooleanField(default=False)
    message_for_user = serializers.CharField(
        default="Your password was wrong/no entered"
    )

    class Meta:
        model = CustomUser
        fields = ["email", "password", "password_correct", "message_for_user"]


class UserSerializer_password_2(serializers.ModelSerializer):
    """
    Serializer for users, checking password fields
    """

    class Meta:
        model = CustomUser
        fields = ["email", "password"]


class UserSerializer_create(serializers.ModelSerializer):
    """
    Serializer for users, in specific format for user creation
    """

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=155)
    toimipaikka = serializers.BooleanField(default=False)
    vastuuhenkilo = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "phone_number", "password", "toimipaikka", "vastuuhenkilo"]


class UserSerializer_update(serializers.ModelSerializer):
    """
    Serializer for users, for updating user information
    """

    class Meta:
        model = CustomUser
        fields = ["name", "phone_number"]


class SubSerializerForGroups(serializers.ModelSerializer):
    """
    Serializer for getting group names from users
    """

    class Meta:
        model = Group
        fields = ["name"]


class UserSerializer_limited(serializers.ModelSerializer):
    """
    Serializer for users, getting the revelant fields
    """

    # groups = SubSerializerForGroups(many=True, read_only=True) #comes out in dict
    groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )  # comes out in list

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "last_login",
            "name",
            "email",
            "phone_number",
            "phone_number",
            "groups",
        ]


class UserSerializer_names(serializers.ModelSerializer):
    """
    Serializer for users, name and email
    """

    class Meta:
        model = CustomUser
        fields = ["name", "email"]


class GroupNameSerializer(serializers.ModelSerializer):
    """
    Serializer for Groups
    """

    class Meta:
        model = Group
        fields = ["id", "name"]


class GroupNameCheckSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(max_length=150)
    test_message = serializers.CharField(max_length=150)
    test_boolean_check_email = serializers.BooleanField(default=False)

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "groups",
            "group_name",
            "test_message",
            "test_boolean_check_email",
        ]


class GroupPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "name",
            "email",
            "groups",
        ]


class GroupPermissionsSerializerNames(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "name",
            "email",
            "groups",
        ]
