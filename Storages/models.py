"""module for Storages models"""
from django.db import models


# Create your models here.
class Storages(models.Model):
    """class for making Storages table for database"""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
