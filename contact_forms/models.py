"""module for contact_forms models"""
from django.db import models


# Create your models here.
class ContactForm(models.Model):
    """class for making ContactForm table for database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    order_id = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, default="Not read")

    def __str__(self) -> str:
        return f"{self.email}'s ContactForm({self.id})"


class Contact(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=100)
