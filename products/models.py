from os.path import basename, isfile
from os import remove

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver

from categories.models import Category

CustomUser = get_user_model()


# Create your models here.
class Color(models.Model):
    """class for making Color table for database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Color: {self.name}({self.id})"


class Picture(models.Model):
    """class for making Picture table for database"""

    id = models.BigAutoField(primary_key=True)
    picture_address = models.ImageField(upload_to="pictures")

    def __str__(self) -> str:
        return f"Picture: {basename(self.picture_address.name)}({self.id})"


@receiver(post_delete, sender=Picture)
def delete_orphan_picture(sender, instance, using, **kwargs):
    if isfile(instance.picture_address.path):
        remove(instance.picture_address.path)


class Storage(models.Model):
    """class for making Storage table for database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    in_use = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"Storage: {self.name}({self.id})"


class Product(models.Model):
    """class representing Product with shared attributes"""

    id = models.BigAutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0.0)
    free_description = models.TextField(default="", blank=True)
    pictures = models.ManyToManyField(Picture, blank=True)
    measurements = models.CharField(max_length=50, default="", blank=True)
    colors = models.ManyToManyField(Color, blank=True)
    weight = models.FloatField(default=0.0)

    def __str__(self) -> str:
        return f"Product: {self.name}({self.id})"

    @property
    def category_name(self):
        return self.category.name

    @property
    def color_name(self):
        return self.colors.name


class ProductItemLogEntry(models.Model):
    """Model representing one log entry connected to ProductItem
    saving what happened to ProductItem, when it happened and who did it."""

    class ActionChoices(models.Choices):
        CREATE = "Created"  # Done
        CART_ADD = "Added to shopping cart"  # Done
        CART_REMOVE = "Removed from shopping cart"  # Done
        CART_TIMEOUT = "Timed out from shopping cart"
        ORDER = "Ordered"  # Done
        ORDER_ADD = "Added to order"  # Done
        ORDER_REMOVE = "Removed from order"  # Done
        CIRCULATION = "Came back to circulation"  # Done
        MODIFY = "Modified at storage"  # Done
        GIFT = "Gifted away"

    id = models.BigAutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(
        max_length=255, choices=ActionChoices.choices, default="Created"
    )


class ProductItem(models.Model):
    """Class representing single item that refers to Product"""

    class ItemStatusChoices(models.Choices):
        AVAILABLE = "Available"
        IN_CART = "In cart"
        UNAVAILABLE = "Unavailable"
        RETIRED = "Retired"

    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    available = models.BooleanField(default=True)
    modified_date = models.DateTimeField(default=timezone.now)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    shelf_id = models.CharField(max_length=255, default="", null=True, blank=True)
    barcode = models.CharField(max_length=255, default="")
    log_entries = models.ManyToManyField(ProductItemLogEntry, blank=True)
    status = models.CharField(
        max_length=255, choices=ItemStatusChoices.choices, default="Available"
    )
