from django.db import models


class DepartmentChoices(models.TextChoices):
    """Choices for which department to pause."""

    TAVARATKIERTOON = "TAVARATKIERTOON"
    BIKES = "BIKES"


class Pause(models.Model):

    id = models.BigAutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    department = models.CharField(
        max_length=255,
        choices=DepartmentChoices.choices,
        default=DepartmentChoices.choices[0][0],
    )
