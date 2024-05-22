from django.contrib import admin

from .models import ContactForm, Contact

# Register your models here.


admin.site.register(ContactForm)
admin.site.register(Contact)
