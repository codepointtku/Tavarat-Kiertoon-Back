"""module for contact_forms models"""
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.
class Category(MPTTModel):
    """class for making Category table for database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    