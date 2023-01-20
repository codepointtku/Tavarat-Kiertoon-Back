from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    PermissionsMixin,
)
from django.db import models

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, phone_number, password):
        """function for creating a user"""
        if not first_name:
            raise ValueError("Users must have first name")
        if not last_name:
            raise ValueError("Users must have last name")
        if not email:
            raise ValueError("Users must have email")
        if not phone_number:
            raise ValueError("Users must have phone number")
        user = self.model(
            email=self.normalize_email(email=email),
            phone_number=phone_number,
            name=(first_name + " " + last_name).title(),
        )
        user.set_password(raw_password=password)
        user.save(using=self._db)
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


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """class representing User in database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, unique=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=255, null=True)

    objects = CustomUserManager()

    REQUIRED_FIELDS = []

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
