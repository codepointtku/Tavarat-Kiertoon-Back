from django.contrib.auth import get_user_model
from django.db import models

from products.models import ProductItem
from users.models import CustomUser


# Create your models here.
class ShoppingCart(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    product_items = models.ManyToManyField(ProductItem)  # product_items?
    date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user}'s ShoppingCart({self.id})"


class Order(models.Model):
    """class modeling Order table in database"""

    class StatusChoices(models.Choices):
        """Choices for the state of order processing."""

        WAITING = "Waiting"
        PROCESSING = "Processing"
        FINISHED = "Finished"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    product_items = models.ManyToManyField(ProductItem, blank=True)
    status = models.CharField(
        max_length=255, choices=StatusChoices.choices, default="Order is waiting for processing"
    )
    delivery_address = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    order_info = models.TextField(default="", blank=True)
    delivery_date = models.DateTimeField(null=True, default=None, blank=True)
    phone_number = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user}'s Order({self.id})"
