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
        joint_user,
        contact_person,
        address,
        user_name,
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
        if not phone_number and joint_user:
            raise ValueError("Users must have user name")

        if not contact_person:
            raise ValueError("Users must have contact person")

        if not joint_user:
            user_name = email

        if not user_name:
            raise ValueError("Users must have user name")

        if joint_user:
            user = self.model(
                email=self.normalize_email(email=email),
                phone_number=phone_number,
                name=(first_name + " " + last_name).title(),
                user_name=user_name,
                address=address,
                joint_user=joint_user,
                contact_person=contact_person,
            )
        else:
            user = self.model(
                email=self.normalize_email(email=email),
                phone_number=phone_number,
                name=(first_name + " " + last_name).title(),
                user_name=self.normalize_email(email=email),
                address=address,
            )

        user.set_password(raw_password=password)
        user.save(using=self._db)

        if not Group.objects.filter(name="user_group").exists():
            Group.objects.create(name="user_group")
        group = Group.objects.get(name="user_group")

        user.groups.add(group)

        return user

    def create_superuser(self, email, password):
        """function for creating a superuser"""
        user = self.model(email=email)
        user.set_password(raw_password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)

        return user


class UserAddress(models.Model):
    """class for making UserAddress table for database"""

    id = models.BigAutoField(primary_key=True)
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"Address: {self.address} {self.zip_code} {self.city} ({self.id})"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """class representing User in database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, unique=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=255, null=True)
    user_name = models.CharField(max_length=255, null=True, blank=True)
    joint_user = models.BooleanField(default=False)
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    address = models.ManyToManyField(UserAddress)

    objects = CustomUserManager()

    REQUIRED_FIELDS = []

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    def __str__(self) -> str:
        return f"User: {self.email}({self.id})"
