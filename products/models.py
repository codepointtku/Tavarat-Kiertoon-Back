from django.db import models

from categories.models import Category


# Create your models here.
class Picture(models.Model):
    """class for making Picture table for database"""

    id = models.BigAutoField(primary_key=True)
    picture_address = models.ImageField(upload_to="pictures")

    def __str__(self) -> str:
        return f"Picture({self.id})"


class Storage(models.Model):
    """class for making Storage table for database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    in_use = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"Storage: {self.name}({self.id})"


class Product(models.Model):
    """class for making Product table for database"""

    id = models.BigAutoField(primary_key=True)
    available = models.BooleanField(default=False)
    barcode = models.CharField(max_length=255, blank=True, null=True)
    # Linked to category table
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    group_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    # estimate_price = models.FloatField(null=True, blank=True) #not needed
    price = models.FloatField(default=0.0)
    # table storages_id Id link field
    storages = models.ForeignKey(
        Storage, on_delete=models.SET_NULL, null=True, blank=True
    )
    shelf_id = models.IntegerField(blank=True, null=True)
    free_description = models.TextField(blank=True, null=True)
    # linked to pictures table
    pictures = models.ManyToManyField(Picture)
    # condition = models.CharField(max_length=50, blank=True, null=True) #condition is explained in description field
    date = models.DateTimeField(auto_now_add=True)
    measurements = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    weight = models.FloatField(default=0.0, blank=True, null=True)

    def __str__(self) -> str:
        return f"Product: {self.name}({self.id})"
