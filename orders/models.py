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


class Order(models.Model):

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def product_availibility_check(user: object):
        user = user.objects.get(id=user.id)
        shopping_cart = ShoppingCart.objects.get(user_id=user.id)
        product_list = shopping_cart.products.all()
        available_products = []
        for product in product_list:
            if product.available == True:
                available_products.append(product.id)
        # make check that looks for non available objects at same group id
        return available_products

    # products = product_avaibility_check(user)
    products = models.ForeignKey(ShoppingCart, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=255)

    delivery_address = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    order_info = models.TextField()
    delivery_date = models.DateTimeField()
