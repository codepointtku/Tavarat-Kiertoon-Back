from django.contrib import admin

from .models import Color, Picture, Product, ProductItem, ProductItemLogEntry, Storage

# Register your models here.
admin.site.register(Color)
admin.site.register(Picture)
admin.site.register(Product)
admin.site.register(Storage)
admin.site.register(ProductItem)
admin.site.register(ProductItemLogEntry)
