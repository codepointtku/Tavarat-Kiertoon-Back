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
    """class modeling Order table in database"""

    def product_availibility_check(user_id):
        # not in use yet, needs to get user from frontend before creating Order instance
        shopping_cart = ShoppingCart.objects.get(user_id=user_id)
        product_list = shopping_cart.products.all()
        available_products = []
        for product in product_list:
            if product.available == True:
                available_products.append(product)
            else:
                for same_product in Product.objects.filter(group_id=product.group_id):
                    if (
                        same_product.available == True
                        and same_product.id not in available_products
                    ):
                        available_products.append(same_product)
                        break
        return available_products

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    products = models.ManyToManyField(Product, blank=True)
    status = models.CharField(max_length=255)
    delivery_address = models.CharField(
        max_length=255, null=True, default=None, blank=True
    )
    contact = models.CharField(max_length=255, null=True, default=None, blank=True)
    order_info = models.TextField(null=True, default=None, blank=True)
    delivery_date = models.DateTimeField(null=True, default=None, blank=True)
