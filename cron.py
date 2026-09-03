import datetime

from django.core.mail import send_mail

from django.conf import settings
from django.utils import timezone

from orders.models import ShoppingCart
from products.models import ProductItemLogEntry
from bikes.models import BikeRental


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


def notify_user_of_bike_rental_start():
    queryset = BikeRental.objects.filter(
        start_date__lte=(timezone.now() + datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d 23:59:59"
        ),
        start_date__gte=(timezone.now() + datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d 00:00:00"
        ),
    )
    for rental in queryset:
        send_mail(
            f"Pyörä tilaus toimitetaan huomenna",
            "Pyörä tilaus toimitetaan huomenna",
            settings.EMAIL_HOST_USER,
            [rental.user.email],
        )
    return


def notify_user_of_bike_rental_end():
    queryset = BikeRental.objects.filter(
        end_date=(timezone.now() + datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d 00:00:00"
        ),
    )
    for rental in queryset.select_related("user"):
        send_mail(
            f"Pyörä tilaus noudetaan huomenna",
            "Pyörä tilaus noudetaan huomenna",
            settings.EMAIL_HOST_USER,
            [rental.user.email],
        )
    return
