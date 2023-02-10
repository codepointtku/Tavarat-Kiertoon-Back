"""Module for bike rental models."""
from django.db import models

from users.models import CustomUser


class BikeType(models.Model):
    """Model for all the types of bike, f.e. City or Electric."""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Bike type: {self.name}({self.id})"


class BikeBrand(models.Model):
    """Model for the bike brands, f.e. Woom or Cannondale."""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Bike brand: {self.name}({self.id})"


class BikeSize(models.Model):
    """Model for the size of the bike, f.e. 16 or 21."""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Bike size: {self.name}({self.id})"


class Bike(models.Model):
    """Model for the bike, which has bike stock which is the individual bikes of this model"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    type = models.ForeignKey(BikeType, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"Bike: {self.name}({self.id})"


class BikeRental(models.Model):
    """Model for the bike rentals, same as orders."""

    id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    # bikes: models.
    # start_date = models.DateField()
    # end_date = models.DateField()
    state = models.TextChoices(
        "state", "WAITING BEING_PROCESSED ACTIVE", default="WAITING"
    )
    delivery_address = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    rental_info = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Bike rental: {self.user.name}({self.id})"


class BikeStock(models.Model):
    """Model for the bike stock, which is each individual bike."""

    id: models.BigIntegerField(primary_key=True)
    barcode: models.CharField(max_length=255)
    created_at: models.DateTimeField(auto_now_add=True)
    state = models.TextChoices(
        "state", "AVAILABLE MAINTENANCE RENTED RETIRED", default="AVAILABLE"
    )
    bike: models.ForeignKey(Bike, on_delete=models.CASCADE)
    rent: models.ManyToManyField(BikeRental)

    def __str__(self) -> str:
        return f"Bike stock: {self.barcode}({self.id})"
