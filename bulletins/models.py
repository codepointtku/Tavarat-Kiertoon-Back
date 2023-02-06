from django.db import models

from users.models import CustomUser


# Create your models here.
class BulletinSubject(models.Model):
    """class for making BulletinSubject table for database"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"BulletinSubject: {self.name} ({self.id})"


class Bulletin(models.Model):
    """class for making Bulletin table for database"""

    id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    subject = models.ManyToManyField(BulletinSubject)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Bulletin: {self.title} ({self.id})"
