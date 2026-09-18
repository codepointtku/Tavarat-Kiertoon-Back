import datetime

from django.core.mail import message, send_mail

from django.conf import settings
from django.http import request
from django.utils import timezone
import holidays

from orders.models import ShoppingCart
from products.models import ProductItemLogEntry
from bikes.models import BikeRental, BikeStock
from django.core.management.base import BaseCommand


def _next_business_day():
    day = timezone.localdate() + datetime.timedelta(days=1)
    finnish_holidays = holidays.FI()
    while day.weekday() >= 5 or day in finnish_holidays:
        day += datetime.timedelta(days=1)
    return day


def _day_bounds(day):
    timezone_value = timezone.get_current_timezone()
    start = timezone.make_aware(
        datetime.datetime.combine(day, datetime.time.min), timezone_value
    )
    next_day = day + datetime.timedelta(days=1)
    end = timezone.make_aware(
        datetime.datetime.combine(next_day, datetime.time.min), timezone_value
    )
    return start, end


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
    tomorrow = _next_business_day()
    start, end = _day_bounds(tomorrow)
    queryset = BikeRental.objects.filter(
        start_date__lt=end,
        start_date__gte=start,
    )

    for rental in queryset:

        if (timezone.now() + datetime.timedelta(days=1)).weekday() >= 5:
            message = ["Pyörätilaus tuodaan maanantaina aamupäivällä"]
            subject = "Pyörätilaus tuodaan maanantaina aamupäivällä"
        elif timezone.now() + datetime.timedelta(days=1) in holidays.FI():
            message = ["Pyörätilaus tuodaan seuraavana arkipäivänä aamupäivällä"]
            subject = "Pyörätilaus tuodaan seuraavana arkipäivänä aamupäivällä"
        else:
            message = ["Pyörätilaus tuodaan huomenna aamupäivällä"]
            subject = "Pyörätilaus tuodaan huomenna aamupäivällä"
        bike_model_counts = {}
        for bike_stock in rental.bike_stock.all():
            model = bike_stock.bike.name
            bike_model_counts[model] = bike_model_counts.get(model, 0) + 1
        message = message + [
            f"{count}X {model}" for model, count in bike_model_counts.items()
        ]
        if rental.bike_trailer:
            message.append(f"Peräkärry: {rental.bike_trailer.register_number}")

        send_mail(
            subject,
            "\n".join(message),
            settings.EMAIL_HOST_USER,
            [rental.user.email],
            fail_silently=False,
        )
    return


def notify_user_of_bike_rental_end():
    tomorrow = _next_business_day()
    start, end = _day_bounds(tomorrow)

    queryset = BikeRental.objects.filter(
        end_date__lt=end,
        end_date__gte=start,
    )

    for rental in queryset:
        subject = "Pyörätilaus noudetaan huomenna aamupäivällä"
        message = []
        if (timezone.now() + datetime.timedelta(days=1)).weekday() >= 5:
            message = ["Pyörätilaus noudetaan maanantaina aamupäivällä"]
            subject = "Pyörätilaus noudetaan maanantaina aamupäivällä"
        elif timezone.now() + datetime.timedelta(days=1) in holidays.FI():
            message = ["Pyörätilaus noudetaan seuraavana arkipäivänä aamupäivällä"]
            subject = "Pyörätilaus noudetaan seuraavana arkipäivänä aamupäivällä"
        else:
            message = ["Pyörätilaus noudetaan huomenna aamupäivällä"]
            subject = "Pyörätilaus noudetaan huomenna aamupäivällä"
        start_date = rental.start_date.strftime("%Y-%m-%d")
        end_date = rental.end_date.strftime("%Y-%m-%d")
        if start_date == end_date:
            return
        bike_model_counts = {}
        for bike_stock in rental.bike_stock.all():
            model = bike_stock.bike.name
            bike_model_counts[model] = bike_model_counts.get(model, 0) + 1
        message = message + [
            f"{count}X {model}" for model, count in bike_model_counts.items()
        ]
        if rental.bike_trailer:
            message.append(f"Peräkärry: {rental.bike_trailer.register_number}")
        message.append(
            "\nMuistathan varmistaa, että kaikki pyörät ja kypärät ovat samassa paikassa noutoa varten."
        )
        message.append("\nNoutotiimi kiittää!")

        send_mail(
            subject,
            "\n".join(message),
            settings.EMAIL_HOST_USER,
            [rental.user.email],
            fail_silently=False,
        )
    return
