from django.contrib import admin

from .models import CustomUser, UserAddress, UserLogEntry, UserSearchWatch

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserAddress)
admin.site.register(UserLogEntry)
admin.site.register(UserSearchWatch)
