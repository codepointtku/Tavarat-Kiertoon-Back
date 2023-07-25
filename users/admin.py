from django.contrib import admin

from .models import CustomUser, SearchWatch, UserAddress, UserLogEntry

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserAddress)
admin.site.register(UserLogEntry)
admin.site.register(SearchWatch)
