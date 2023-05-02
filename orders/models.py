from django.contrib.auth import get_user_model
from django.db import models

from products.models import Product
from users.models import CustomUser


# Create your models here.
class ShoppingCart(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    products = models.ManyToManyField(Product)
    date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user}'s ShoppingCart({self.id})"


class Order(models.Model):
    """class modeling Order table in database"""

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    products = models.ManyToManyField(Product, blank=True)
    status = models.CharField(max_length=255)
    delivery_address = models.CharField(
        max_length=255, null=True
    )
    contact = models.CharField(max_length=255, default="", blank=True)
    order_info = models.TextField(default="", blank=True)
    delivery_date = models.DateTimeField(null=True, default=None, blank=True)
    phone_number = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user}'s Order({self.id})"
