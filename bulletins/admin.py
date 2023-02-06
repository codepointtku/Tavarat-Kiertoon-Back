from django.contrib import admin

from .models import Bulletin, BulletinSubject

# Register your models here.

admin.site.register(Bulletin)
admin.site.register(BulletinSubject)
