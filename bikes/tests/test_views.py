import datetime

from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.utils import timezone
from users.models import CustomUser


from bikes.models import (
    BikeType,
    BikeBrand,
    BikeSize,
    Bike,
    BikeStock,
    BikeRental,
    BikePackage,
    BikeAmount,
)
from products.models import Color, Storage


class TestProducts(TestCase):
    @classmethod
    @override_settings(MEDIA_ROOT=TEST_DIR)
    def setUpTestData(cls):
        asd = "asd"

