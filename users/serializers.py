from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers, status

from .custom_functions import custom_time_token_generator, validate_email_domain
from .models import CustomUser, UserAddress

User = get_user_model()


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


class UserLoginPostSerializer(serializers.Serializer):
    """
    needed login information
    """

    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128)


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


class UserTokenValidationSerializer(serializers.Serializer):

    """
    Serializer for user activation validations.
    """

    uid = serializers.CharField(max_length=255)
    token = serializers.CharField(max_length=255)

    def validate(self, data):
        """
        check the correctness of token
        """
        # decoding uid and chekcing that token is valid
        # token_generator = default_token_generator
        token_generator = custom_time_token_generator
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

    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
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
            "username",
            "address",
            "zip_code",
            "city",
        ]

    def to_internal_value(self, data):
        mod_data = data.copy()
        if "username" not in data:
            mod_data["username"] = mod_data["email"]
        mod_data = super().to_internal_value(mod_data)
        return mod_data


class UserCreateReturnSerializer(serializers.ModelSerializer):
    """
    Serializer for users, in specific format for user creation
    """

    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=50)

    message = serializers.CharField(default="Some message", max_length=255)

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "message",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "message" in self.context:
            representation["message"] = self.context["message"]

        return representation


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for users, for updating user information
    """

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone_number"]


class SubSerializerForGroups(serializers.ModelSerializer):
    """
    Serializer for getting group names from users
    """

    class Meta:
        model = Group
        fields = ["name"]


class SubSerializerForGroupsSchema(serializers.ModelSerializer):
    """
    Serializer for getting group names from users
    """

    class Meta:
        model = Group
        # fields = "__all__"
        exclude = ["permissions"]


class UserFullSerializer(serializers.ModelSerializer):
    """
    Serializer for users, all database fields
    """

    address_list = UserAddressSerializer(many=True, read_only=True)
    groups = SubSerializerForGroupsSchema(many=True, read_only=True)

    class Meta:
        model = CustomUser
        # fields = "__all__"
        exclude = [
            "password",
            "is_admin",
            "is_staff",
            "is_superuser",
            "user_permissions",
        ]


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
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "phone_number",
            "groups",
            "address_list",
            "username",
        ]


class GroupNameSerializer(serializers.ModelSerializer):
    """
    Serializer for Groups
    """

    class Meta:
        model = Group
        fields = ["id", "name"]


class GroupPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "groups",
        ]


class UsersLoginRefreshResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for return data when logging in and refreshing.
    pass message in context.
    """

    message = serializers.CharField(default="Some message", max_length=255)

    groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )  # comes out in list

    class Meta:
        model = CustomUser
        fields = [
            "message",
            "username",
            "groups",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "message" in self.context:
            representation["message"] = self.context["message"]

        return representation


class NewEmailSerializer(serializers.Serializer):
    """
    Serializer for inputting new email address
    """

    new_email = serializers.CharField(max_length=255)

    def validate_new_email(self, value):
        """
        validating the new amil address
        """
        if "@" not in value:
            msg = "not an email address (no @)"
            raise serializers.ValidationError(msg)

        email_split = value.split("@")
        if not validate_email_domain(email_split[1]):
            msg = "not valid domain for email"
            raise serializers.ValidationError(msg)

        return value
    
class NewEmailFinishValidationSerializer(UserTokenValidationSerializer):
    """
    Serializer for inputting new email address
    """

    new_email = serializers.CharField(max_length=255)


# -----------------------------------------------------------------------
# schema serializers
# -----------------------------------------------------------------------


@extend_schema_serializer(exclude_fields=["user"])
class UserAddressPostRequestSerializer(UserAddressSerializer):
    """
    Serializer mainly for schema purpose, fields required for creating address for user
    """


@extend_schema_serializer(exclude_fields=["user"])
class UserAddressPutRequestSerializer(UserAddressSerializer):
    """
    Serializer mainly for schema purpose, removing the required tag and adding id
    id = the id number of address being changed
    """

    id = serializers.IntegerField(required=True)
    address = serializers.CharField(max_length=255, required=False)
    zip_code = serializers.CharField(max_length=10, required=False)
    city = serializers.CharField(max_length=100, required=False)


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=255)


class UserFullResponseSchemaSerializer(serializers.ModelSerializer):
    """
    FOR SCHEMA, Serializer for users, all database fields
    """

    address_list = UserAddressSerializer(many=True, read_only=True)
    groups = SubSerializerForGroupsSchema(many=True, read_only=True)

    class Meta:
        model = CustomUser
        exclude = [
            "password",
            "is_admin",
            "is_staff",
            "is_superuser",
            "user_permissions",
        ]
        extra_kwargs = {
            "last_login": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone_number": {"required": True},
            "is_active": {"required": True},
        }


class UserUpdateReturnSchemaSerializer(serializers.ModelSerializer):
    """
    FOR SCHEMA, Serializer for users, for updating user information
    """

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone_number"]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone_number": {"required": True},
        }


class GroupPermissionsResponseSchemaSerializer(serializers.ModelSerializer):
    """
    FOR SCHEMA
    """

    class Meta:
        model = CustomUser
        fields = [
            "groups",
        ]
        extra_kwargs = {
            "groups": {"required": True},
        }


class UserCreateReturnResponseSchemaSerializer(serializers.ModelSerializer):
    """
    FOR SCHEMA, Serializer for users, in specific format for user creation
    """

    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=50)

    message = serializers.CharField(max_length=255, required=True)

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "message",
        ]


class UsersLoginRefreshResponseSchemaSerializer(serializers.ModelSerializer):
    """
    FOR SCHEMA
    Serializer for return data when logging in and refreshing.
    pass message in context.
    """

    message = serializers.CharField(required=True, max_length=255)

    groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )  # comes out in list

    class Meta:
        model = CustomUser
        fields = [
            "message",
            "username",
            "groups",
        ]
