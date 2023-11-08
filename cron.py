import datetime

from django.utils import timezone

from orders.models import ShoppingCart
from products.models import ProductItemLogEntry


def clear_shopping_carts():
    queryset = ShoppingCart.objects.exclude(product_items=None).filter(
        date__lte=timezone.now() - datetime.timedelta(hours=2)
    )
    for cart in queryset:
        log_entry = ProductItemLogEntry.objects.create(
            action=ProductItemLogEntry.ActionChoices.CART_TIMEOUT
        )
        for product_item in cart.product_items.all():
            product_item.log_entries.add(log_entry)
            product_item.available = True
            product_item.status = "Available"
            product_item.save()
        cart.product_items.clear()
        cart.save()
    return
