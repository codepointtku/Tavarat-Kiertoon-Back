from django.contrib import admin

from .models import Order, OrderEmailRecipient, ShoppingCart

# Register your models here.
admin.site.register(Order)
admin.site.register(ShoppingCart)
admin.site.register(OrderEmailRecipient)
