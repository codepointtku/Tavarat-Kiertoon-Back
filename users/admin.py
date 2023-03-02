from django.contrib import admin

from .models import CustomUser, UserAddress

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserAddress)
