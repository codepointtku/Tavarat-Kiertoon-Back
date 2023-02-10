"""Making bike models available to admin."""
from django.contrib import admin

from bikes.models import Bike, BikeBrand, BikeRental, BikeSize, BikeStock, BikeType

# Register your models here.

admin.site.register(Bike)
admin.site.register(BikeBrand)
admin.site.register(BikeType)
admin.site.register(BikeSize)
admin.site.register(BikeStock)
admin.site.register(BikeRental)
