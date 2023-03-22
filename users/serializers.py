from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers, status

from .models import CustomUser, UserAddress

User = get_user_model()


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


class UserPasswordCheckEmailSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)

    def validate_username(self, value):
        """
        Check if username exists serializer
        """
        try:
            user = CustomUser.objects.get(username=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("User does not existss")

        return value


class UserPasswordChangeEmailValidationSerializer(serializers.Serializer):
    uid = serializers.CharField(max_length=255)
    token = serializers.CharField(max_length=255)
    new_password = serializers.CharField(max_length=255)
    new_password_again = serializers.CharField(max_length=255)

    def validate(self, data):
        """
        check the correctness  of token and same password, future password validation?
        """

        if data["new_password"] != data["new_password_again"]:
            msg = "the new password weren't same DANG"
            raise serializers.ValidationError(msg, code="authorization")

        # decoding uid and chekcing that token is valid
        token_generator = default_token_generator
        try:
            uid = urlsafe_base64_decode(data["uid"]).decode()
        except ValueError:
            msg = "stuff went wrong in decoding uid or something"
            raise serializers.ValidationError(msg)

        try:
            user = User.objects.get(id=uid)
        except (ValueError, ObjectDoesNotExist):
            msg = "something doesnt feel right about user"
            raise serializers.ValidationError(msg)

        if not token_generator.check_token(user=user, token=data["token"]):
            msg = "something went wrong confirming email link, get now one"
            raise serializers.ValidationError(msg)

        # print("jammign that decoded uid into data insted of coded one, old: ", data)
        data["uid"] = uid

        return data


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
        # fields = "__all__"
        exclude = ["password", "is_admin", "is_staff", "is_superuser"]
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


# class UserNamesSerializer(serializers.ModelSerializer):
#     """
#     Serializer for users, name and email
#     """

#     class Meta:
#         model = CustomUser
#         fields = ["name", "email"]


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
