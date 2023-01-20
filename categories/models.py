"""module for contact_forms models"""
from django.db import models

# Create your models here.
class Category(models.Model):
    """class for making Category table for database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

class Hierarchy(models.Model):
    """class for making Hierarchy table for database"""

    id = models.BigAutoField(primary_key=True)
    categories_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_id")
    parent = models.ManyToManyField(Category, blank=True, null=True, related_name="parent_id")
    child = models.ManyToManyField(Category, blank=True, null=True, related_name="child_id")
