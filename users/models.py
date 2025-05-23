from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    PermissionsMixin,
)
from django.db import models

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        first_name,
        last_name,
        email,
        phone_number,
        password,
        address,
        zip_code,
        city,
        username,
        group="user_group",
    ):
        """function for creating a user"""
        if not first_name:
            raise ValueError("Users must have first name")
        if not last_name:
            raise ValueError("Users must have last name")
        if not email:
            raise ValueError("Users must have email")
        if not phone_number:
            raise ValueError("Users must have phone number")
        if not address:
            raise ValueError("Users must have address")
        if not zip_code:
            raise ValueError("Users must have zip_code")
        if not city:
            raise ValueError("Users must have city")
        if "@" in username:
            username = self.normalize_email(email=username)

        if not username:
            raise ValueError("Users must have user name")

        user = self.model(
            email=self.normalize_email(email=email),
            phone_number=phone_number,
            first_name=first_name.title(),
            last_name=last_name.title(),
            username=username,
            group=group,
        )

        user.set_password(raw_password=password)
        user.save(using=self._db)

        # creating the address for user
        UserAddress.objects.create(
            address=address, zip_code=zip_code, city=city, user=user
        )

        if not Group.objects.filter(name="user_group").exists():
            Group.objects.create(name="user_group")
        group = Group.objects.get(name="user_group")

        user.groups.add(group)

        return user

    def create_superuser(self, username, password):
        """function for creating a superuser"""
        user = self.model(username=username, email=username)
        user.set_password(raw_password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        user.save(using=self._db)

        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """class representing User in database"""

    class GroupChoices(models.Choices):
        ADMIN = "admin_group"
        STORAGE = "storage_group"
        USER = "user_group"
        DEACTIVE = "deactive"

    id = models.BigAutoField(primary_key=True)
    # name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=255, null=True)
    username = models.CharField(max_length=255, unique=True)
    group = models.CharField(
        max_length=255, choices=GroupChoices.choices, default="user_group"
    )
    is_active = models.BooleanField(
        default=False,
        help_text=(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    objects = CustomUserManager()

    REQUIRED_FIELDS = []

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    def __str__(self) -> str:
        return f"User: {self.username}({self.id})"


class UserAddress(models.Model):
    """class for making UserAddress table for database"""

    id = models.BigAutoField(primary_key=True)
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    user = models.ForeignKey(
        CustomUser, related_name="address_list", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"Address: {self.address} {self.zip_code} {self.city} ({self.id})"

    class Meta:
        verbose_name_plural = "User addresses"


class UserLogEntry(models.Model):
    """
    Model representing one log entry connected to Users
    saving what happened to User, when it happened and who did it.
    """

    class ActionChoices(models.Choices):
        """Choices for the log action."""

        CREATED = "User was created"
        ACTIVATED = "User was activated"
        PASSWORD = "Users password was changed"
        USER_INFO = "User info was changed"
        USER_ADDRESS_INFO = "User address info was changed"
        USER_ADDRESS_INFO_DELETE = "User address info was deleted"
        PERMISSIONS = "Users permissions were changed"
        EMAIL = "Users email was changed"
        WATCH = "Users search watch was edited"

    id = models.BigAutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    target = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="target_user"
    )
    user_who_did_this_action = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="source_user"
    )
    action = models.CharField(
        max_length=255, choices=ActionChoices.choices, default="Created"
    )


class SearchWatch(models.Model):
    """
    Model used for the search watch functionality for user
    """

    id = models.BigAutoField(primary_key=True)
    words = models.JSONField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Search watch for {self.user} , with words: {self.words}"
