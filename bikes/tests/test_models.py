from django.test import TestCase
from django.utils import timezone

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
from products.models import Color
from users.models import CustomUser

class TestBikes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user1 = CustomUser.objects.create_user(
            first_name="Bike",
            last_name="Admin",
            email="bikeadmin@turku.fi",
            phone_number="0501111111",
            password="bikeadmin",
            address="Bikealley 1",
            zip_code="99999",
            city="Bikeland",
            username="bikeadmin@turku.fi",
        )
        cls.test_user1.is_active = True
        cls.test_user1.save()

        cls.test_color = Color.objects.create(name="musta")

        cls.test_bikesize = BikeSize.objects.create(
            name="48″",
        )
        cls.test_bikebrand = BikeBrand.objects.create(
            name="Chungus",
        )
        cls.test_biketype = BikeType.objects.create(
            name="Manual",
        )

        cls.test_bikemodel = Bike.objects.create(
            name="Nice bike",
            size=cls.test_bikesize,
            brand=cls.test_bikebrand,
            type=cls.test_biketype,
            description="a nice, comfortable bike"
        )

        cls.test_bikeobject1 = BikeStock.objects.create(
            package_only=True,
            number=101,
            frame_number=101,
            color=cls.test_color,
            bike=cls.test_bikemodel
        )

        cls.test_bikepackage1 = BikePackage.objects.create(
            name="test_package",
            description="package for test purposes"
        )

        cls.test_bikeamount1 = BikeAmount.objects.create(
            amount=1,
            bike=cls.test_bikemodel,
            package=cls.test_bikepackage1
        )

        cls.test_bikerental = BikeRental.objects.create(
            user=cls.test_user1,
            start_date=timezone.now(),
            end_date=timezone.now(),
            delivery_address="anywhere",
            contact_name="bikeperson",
            contact_phone_number="123456789",
            extra_info="lets ride"
        )


    def test_self_biketype_string(self):
        self.assertEqual(
            str(self.test_biketype),
            f"Bike type: {self.test_biketype.name}({self.test_biketype.id})",
        )

    def test_self_bikebrand_string(self):
        self.assertEqual(
            str(self.test_bikebrand),
            f"Bike brand: {self.test_bikebrand.name}({self.test_bikebrand.id})",
        )

    def test_self_bikesize_string(self):
        self.assertEqual(
            str(self.test_bikesize),
            f"Bike size: {self.test_bikesize.name}({self.test_bikesize.id})",
        )

    def test_self_bikemodel_string(self):
        self.assertEqual(
            str(self.test_bikemodel),
            f"Bike: {self.test_bikemodel.name}({self.test_bikemodel.id})"
        )

    def test_self_bikerental_string(self):
        self.assertEqual(
            str(self.test_bikerental),
            f"Bike rental: {self.test_user1}({self.test_bikerental.id})"
        )

    def test_self_bikeitem_string(self):
        self.assertEqual(
            str(self.test_bikeobject1),
            f"Bike stock: {self.test_bikeobject1.number}({self.test_bikeobject1.id})"
        )

    def test_self_bikepackage_string(self):
        self.assertEqual(
            str(self.test_bikepackage1),
            f"Bike package: {self.test_bikepackage1.name}({self.test_bikepackage1.id})"
        )

    def test_self_bikeamount_string(self):
        self.assertEqual(
            str(self.test_bikeamount1),
            f"Bike amount: {self.test_bikeamount1.amount}x{self.test_bikeamount1.bike}({self.test_bikeamount1.id})"
        )
