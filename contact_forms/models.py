"""module for contact_forms models"""
from django.db import models


# Create your models here.
class ContactForm(models.Model):
    """class for making ContactForm table for database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255)
