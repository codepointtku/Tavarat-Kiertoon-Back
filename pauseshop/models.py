from django.db import models


# Create your models here.
class Pause(models.Model):
    id = models.BigAutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
