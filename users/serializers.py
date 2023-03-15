from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import CustomUser, UserAddress


class BooleanValidatorSerializer(serializers.ModelSerializer):
    joint_user = serializers.BooleanField(default=False)

    class Meta:
        model = CustomUser
        fields = ["joint_user"]


class UserPasswordSerializer(serializers.ModelSerializer):
    """
    Serializer for users, checking password fields
    """

    password_correct = serializers.BooleanField(default=False)
    message_for_user = serializers.CharField(
        default="Your password was wrong/no entered"
    )

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "password",
            "username",
            "password_correct",
            "message_for_user",
        ]

class UserPasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for users, checking password fields
    """
    username = serializers.CharField(max_length=255)
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    new_password_again = serializers.CharField(max_length=128)

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        # Get authenticated user for raise hit limit validation
        user = self.context['request'].user
        print(user)
        # do something with the user here

    class Meta:
        fields = [
            "username",
            "old_password",
            "new_password",
            "new_password_again"
        ]


class UserAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for user address
    """

    class Meta:
        model = UserAddress
        fields = "__all__"


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for users, in specific format for user creation
    """

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     print("testi data: ", data)
    #     if not data["joint_user"] :
    #         data["username"] = data["email"]

    #     print("test data 2: ", data)
    #     return data

    # def validate(self, attrs):
    #     print("testing stuff in serialzier:", attrs)
    #     if not attrs["joint_user"]:
    #         print("joint user IS NOT this guy")
    #         attrs["username"] = attrs["email"]
    #         print("after swap: ", attrs)
    #     return attrs

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=155)
    joint_user = serializers.BooleanField(default=False)
    phone_number = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=255)
    zip_code = serializers.CharField(max_length=10)
    city = serializers.CharField(max_length=100)

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password",
            "joint_user",
            "username",
            "address",
            "zip_code",
            "city",
        ]


class UserCreateReturnSerializer(serializers.ModelSerializer):
    """
    Serializer for users, in specific format for user creation
    """

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=155)
    phone_number = serializers.CharField(max_length=50)

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
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


class UserFullSerializer(serializers.ModelSerializer):
    """
    Serializer for users, all database fields
    """

    address_list = UserAddressSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = "__all__"
        depth = 1


class UserLimitedSerializer(serializers.ModelSerializer):
    """
    Serializer for users, getting the revelant fields
    """

    # groups = SubSerializerForGroups(many=True, read_only=True) #comes out in dict
    groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )  # comes out in list

    address_list = UserAddressSerializer(many=True, read_only=True)

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
            "address_list",
            "username",
        ]


class UserNamesSerializer(serializers.ModelSerializer):
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


class GroupPermissionsNamesSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "name",
            "email",
            "groups",
        ]
