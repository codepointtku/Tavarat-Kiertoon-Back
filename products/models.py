from os.path import basename

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from categories.models import Category

CustomUser = get_user_model()


# Create your models here.
class Color(models.Model):
    """class for making Color table for database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Color: {self.name}({self.id})"


class Picture(models.Model):
    """class for making Picture table for database"""

    id = models.BigAutoField(primary_key=True)
    picture_address = models.ImageField(upload_to="pictures")

    def __str__(self) -> str:
        return f"Picture: {basename(self.picture_address.name)}({self.id})"


class Storage(models.Model):
    """class for making Storage table for database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    in_use = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"Storage: {self.name}({self.id})"


class ModifyProduct(models.Model):
    """class for tracking when Product was modified and why"""

    class CircumstanceChoices(models.TextChoices):
        """Choices for the state of the bike."""

        ADDTOCART = "Added to shopping cart"
        REMOVEFROMCART = "Removed from shopping cart"
        TIMEOUTFROMCART = "Timed out from shopping cart"
        ORDER = "Ordered"
        STORAGE = "Modified in storage"
        CREATION = "Creation"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    circumstance = models.CharField(max_length=255, choices=CircumstanceChoices.choices)


class Product(models.Model):
    """class for making Product table for database"""

    id = models.BigAutoField(primary_key=True)
    available = models.BooleanField(default=False)
    barcode = models.CharField(max_length=255, default="")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    group_id = models.CharField(max_length=255, default="")
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0.0)
    storages = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    shelf_id = models.IntegerField(blank=True, null=True)
    free_description = models.TextField(default="", blank=True)
    pictures = models.ManyToManyField(Picture, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(default=timezone.now)
    measurements = models.CharField(max_length=50, default="", blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    weight = models.FloatField(default=0.0)
    modified = models.ManyToManyField(ModifyProduct, blank=True)

    def __str__(self) -> str:
        return f"Product: {self.name}({self.id})"
