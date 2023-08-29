from orders.models import ShoppingCart
import datetime
from django.utils import timezone


def clear_shopping_carts():
    queryset = ShoppingCart.objects.exclude(product_items=None).filter(date__lte=timezone.now() - datetime.timedelta(minutes=5))
    for cart in queryset:
        cart.product_items.clear()
        cart.save()
    return
