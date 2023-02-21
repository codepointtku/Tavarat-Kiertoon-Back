"""Module for bike rental models."""

from django.db import models

from products.models import Color, Storage
from users.models import CustomUser


class BikeType(models.Model):
    """Model for all the types of bike, f.e. City or Electric."""

    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Bike type: {self.name}({self.id})"


class BikeBrand(models.Model):
    """Model for the bike brands, f.e. Woom or Cannondale."""

    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Bike brand: {self.name}({self.id})"


class BikeSize(models.Model):
    """Model for the size of the bike, f.e. 16 or 21."""

    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Bike size: {self.name}({self.id})"


class Bike(models.Model):
    """Model for the bike, which has bike stock which is the individual bikes of this model."""

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    type = models.ForeignKey(BikeType, null=True, blank=True, on_delete=models.SET_NULL)
    brand = models.ForeignKey(
        BikeBrand, null=True, blank=True, on_delete=models.SET_NULL
    )
    size = models.ForeignKey(BikeSize, null=True, blank=True, on_delete=models.SET_NULL)
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"Bike: {self.name}({self.id})"


class BikeStock(models.Model):
    """Model for the bike stock, which is each individual bike."""

    class StateChoices(models.TextChoices):
        AVAILABLE = "AVAILABLE"
        MAINTENANCE = "MAINTENANCE"
        RENTED = "RENTED"
        RETIRED = "RETIRED"

    barcode = models.CharField(max_length=255)
    # ? Can barcode be trusted to be unique?
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(
        max_length=255,
        choices=StateChoices.choices,
        default="AVAILABLE",
    )
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Bike stock: {self.barcode}({self.id})"


class BikeRental(models.Model):
    """Model for the bike rentals, same as orders."""

    class StateChoices(models.TextChoices):
        WAITING = "WAITING"
        BEING_PROCESSED = "BEING_PROCESSED "
        ACTIVE = "ACTIVE"

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    bike_stock = models.ManyToManyField(BikeStock)
    start_date = models.DateField()
    end_date = models.DateField()
    state = models.CharField(
        max_length=255,
        choices=StateChoices.choices,
        default="WAITING",
    )
    delivery_address = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    rental_info = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Bike rental: {self.user.name}({self.id})"
