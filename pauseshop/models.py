from django.db import models


# Create your models here.
class Pause(models.Model):
    class DepartmentChoices(models.TextChoices):
        """Choices for which department to pause."""

        TAVARATKIERTOON = "TAVARATKIERTOON"
        BIKES = "BIKES"

    id = models.BigAutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    department = models.CharField(
        max_length=255,
        choices=DepartmentChoices.choices,
        default=DepartmentChoices.choices[0][0],
    )
