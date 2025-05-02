from django.db import models


# Create your models here.
class Pause(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
