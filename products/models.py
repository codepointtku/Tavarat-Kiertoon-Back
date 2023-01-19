from django.db import models


# Create your models here.
class Picture(models.Model):
    """class for making Picture table for database"""
    id = models.BigAutoField(primary_key=True)
    picture_address = models.ImageField(upload_to="pictures")

class Storage(models.Model):
    """class for making Storage table for database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

class Product(models.Model):
    """class for making Product table for database"""
    id = models.BigAutoField(primary_key=True)
    available = models.BooleanField(default=False)
    barcode = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255)
    group_id = models.IntegerField(blank=True,null=True)
    name = models.CharField(max_length=255)
    estimate_price = models.FloatField(null=True, blank=True)
    price = models.FloatField(default=0.0)
    storages_id = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True, blank=True)  # from app users
    shelf_id = models.IntegerField(blank=True, null=True)
    free_description = models.TextField(blank=True, null=True)
    pictures = models.ManyToManyField(Picture)
    condition = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

