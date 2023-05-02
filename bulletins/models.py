from django.db import models

from users.models import CustomUser


# Create your models here.
class Bulletin(models.Model):
    """class for making Bulletin table for database"""

    id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=False
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Bulletin: {self.title} ({self.id})"
