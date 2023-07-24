from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import BadSignature, Signer
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers, status

from .custom_functions import custom_time_token_generator, validate_email_domain
from .models import CustomUser, UserAddress, UserLogEntry, UserSearchWatch

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
    remember_me = serializers.BooleanField(default=False)


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


class UserTokenValidationSerializer(serializers.Serializer):

    """
    Serializer for user activation validations.
    """

    uid = serializers.CharField(max_length=255)
    token = serializers.CharField(max_length=255)

    token_generator = custom_time_token_generator

    def validate(self, data):
        """
        check the correctness of token
        """
        # decoding uid and chekcing that token is valid
        token_generator = self.token_generator

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
            msg = "something went wrong confirming data in email link, get now one"
            raise serializers.ValidationError(msg)

        # print("putting decoded uid into data insted of encoded one, old: ", data)
        data["uid"] = uid

        return data


class UserPasswordChangeEmailValidationSerializer(UserTokenValidationSerializer):
    new_password = serializers.CharField(max_length=255)
    new_password_again = serializers.CharField(max_length=255)

    token_generator = default_token_generator

    def validate(self, data):
        """
        check the correctness  of token and same password, future password validation?
        """

        if data["new_password"] != data["new_password_again"]:
            msg = "the new password weren't same DANG"
            raise serializers.ValidationError(msg, code="authorization")

        # decoding uid and chekcing that token is valid
        data = super().validate(data)

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
        extra_kwargs = {
            "username": {"required": False},
        }

    def to_internal_value(self, data):
        mod_data = data.copy()
        if "username" not in data:
            mod_data["username"] = mod_data["email"]

        # in the case we want to accept empty username as no username passed
        # else:
        #     if data["username"] == "":
        #         mod_data["username"] = mod_data["email"]

        mod_data = super().to_internal_value(mod_data)
        return mod_data

    def validate(self, data):
        data = super().validate(data)

        # validating the email address so that its actually email address and is in valid domain
        if not validate_email_domain(data["email"]):
            msg = "not valid email address or domain"
            raise serializers.ValidationError(msg)

        return data


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
        validating the new email address
        """

        # validating the email and domain
        if not validate_email_domain(value):
            msg = "not valid email address or domain"
            raise serializers.ValidationError(msg)

        # checking that when normal user that there isnt already user with the email
        # this to prevent multiple same usernames
        user = self.context.get("request").user
        user_count = User.objects.filter(username=value).count()
        if (user_count >= 1) and ("@" in user.username):
            msg = f"normal user with email address of {value} already exists"
            raise serializers.ValidationError(msg)

        return value


class NewEmailFinishValidationSerializer(UserTokenValidationSerializer):
    """
    Serializer for inputting new email address
    """

    new_email = serializers.CharField(max_length=255)

    token_generator = default_token_generator

    def validate(self, data):
        data = super().validate(data)

        # decoding email
        # using the same time as passwrod reset for token lifetime
        token_generator = self.token_generator
        try:
            email = urlsafe_base64_decode(data["new_email"]).decode()
        except ValueError:
            msg = "stuff went wrong in decoding the new email adress"
            raise serializers.ValidationError(msg)

        # checking that the email hasnt been tampered with
        try:
            signer = Signer(key=data["token"])
            unsigned_email = signer.unsign(email)
        except BadSignature:
            msg = "email was most likely tampered with, try changing email again from start"
            raise serializers.ValidationError(msg)

        data["new_email"] = unsigned_email

        return data


class UserLogSerializer(serializers.ModelSerializer):
    """
    Serializer for user logs
    """

    class Meta:
        model = UserLogEntry
        fields = "__all__"


class SearchWatchSerializer(serializers.ModelSerializer):
    """
    Serializer for user search watchs for normal users
    """

    class Meta:
        model = UserSearchWatch
        fields = "__all__"


# -----------------------------------------------------------------------
# schema serializers
# -----------------------------------------------------------------------
@extend_schema_serializer(exclude_fields=["user", "id"])
class SearchWatchRequestSerializer(SearchWatchSerializer):
    """Serializer for SearchWatchListView post"""


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


class UserLogResponseSchemaSerializer(serializers.ModelSerializer):
    """
    Serializer for user logs
    FOR SCHEMA
    """

    class Meta:
        model = UserLogEntry
        fields = "__all__"
        extra_kwargs = {
            "action": {"required": True},
            "target": {"required": True},
            "user_who_did_this_action": {"required": True},
        }
