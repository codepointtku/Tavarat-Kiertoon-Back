"""The bike rental model."""

from django.db import models

from products.models import Color, Storage, Picture
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
    picture = models.ForeignKey(Picture, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"Bike: {self.name}({self.id})"


class BikePackage(models.Model):
    """Model for the bike packages, which has the bikes that are part of this package."""

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Bike package: {self.name}({self.id})"


class BikeAmount(models.Model):
    """Model for the bike amount, which is used in the bike package."""

    bike = models.ForeignKey(Bike, on_delete=models.CASCADE)
    amount = models.IntegerField()
    package = models.ForeignKey(
        BikePackage, related_name="bikes", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"Bike amount: {self.amount}x{self.bike}({self.id})"


class BikeStock(models.Model):
    """Model for the bike stock, which is each individual bike."""

    class StateChoices(models.TextChoices):
        """Choices for the state of the bike."""

        AVAILABLE = "AVAILABLE"
        MAINTENANCE = "MAINTENANCE"
        RETIRED = "RETIRED"

    package_only = models.BooleanField(default=False)
    number = models.CharField(max_length=255)
    frame_number = models.CharField(max_length=255)
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(
        max_length=255,
        choices=StateChoices.choices,
        default="AVAILABLE",
    )
    bike = models.ForeignKey(Bike, related_name="stock", on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    package = models.ForeignKey(BikePackage, related_name="bike_stock", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"Bike stock: {self.number}({self.id})"


class BikeRental(models.Model):
    """Model for the bike rentals, same as orders."""

    class StateChoices(models.TextChoices):
        """Choices for the state of the rental."""

        WAITING = "WAITING"
        ACTIVE = "ACTIVE"
        FINISHED = "FINISHED"

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    bike_stock = models.ManyToManyField(BikeStock, related_name="rental", blank=True)
    packages = models.ManyToManyField(BikePackage, related_name="packagerental", blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    state = models.CharField(
        max_length=255,
        choices=StateChoices.choices,
        default="WAITING",
    )
    delivery_address = models.CharField(max_length=255)
    pickup = models.BooleanField(default=False)
    contact_name = models.CharField(max_length=255)
    contact_phone_number = models.CharField(max_length=255)
    extra_info = models.CharField(max_length=255, default="", blank=True)

    def __str__(self) -> str:
        return f"Bike rental: {self.user}({self.id})"
