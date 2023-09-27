import datetime

from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
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
from products.models import Color, Storage
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

        cls.test_user2 = CustomUser.objects.create_user(
            first_name="Biker",
            last_name="Person",
            email="bikerperson@turku.fi",
            phone_number="0502222222",
            password="bikerperson",
            address="Bikealley 2",
            zip_code="99999",
            city="Bikeland",
            username="bikerperson@turku.fi",
        )
        cls.test_user2.is_active = True
        cls.test_user2.save()

        cls.test_storage = Storage.objects.create(name="Bikestorage")
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
            color=cls.test_color,
            description="a nice, comfortable bike"
        )

        cls.test_bikemodel2 = Bike.objects.create(
            name="Better bike",
            size=cls.test_bikesize,
            brand=cls.test_bikebrand,
            type=cls.test_biketype,
            color=cls.test_color,
            description="a nicer, more comfortable bike"
        )

        cls.test_bikeobject1 = BikeStock.objects.create(
            package_only=True,
            number=101,
            frame_number=101,
            color=cls.test_color,
            storage=cls.test_storage,
            bike=cls.test_bikemodel
        )

        cls.test_bikeobject2 = BikeStock.objects.create(
            package_only=True,
            number=101,
            frame_number=102,
            color=cls.test_color,
            storage=cls.test_storage,
            bike=cls.test_bikemodel
        )

        cls.test_bikeobject3 = BikeStock.objects.create(
            package_only=True,
            number=101,
            frame_number=103,
            color=cls.test_color,
            storage=cls.test_storage,
            bike=cls.test_bikemodel
        )

        cls.test_bikeobject11 = BikeStock.objects.create(
            package_only=False,
            number=101,
            frame_number=111,
            color=cls.test_color,
            storage=cls.test_storage,
            bike=cls.test_bikemodel
        )

        cls.test_bikeobject12 = BikeStock.objects.create(
            package_only=False,
            number=102,
            frame_number=112,
            color=cls.test_color,
            storage=cls.test_storage,
            bike=cls.test_bikemodel
        )

        cls.test_bikeobject21 = BikeStock.objects.create(
            package_only=True,
            number=201,
            frame_number=201,
            color=cls.test_color,
            storage=cls.test_storage,
            bike=cls.test_bikemodel2
        )

        cls.test_bikeobject22 = BikeStock.objects.create(
            package_only=True,
            number=201,
            frame_number=202,
            color=cls.test_color,
            storage=cls.test_storage,
            bike=cls.test_bikemodel2
        )

        cls.test_bikepackage1 = BikePackage.objects.create(
            name="test_package",
            description="package for test purposes"
        )

        cls.test_bikeamount1 = BikeAmount.objects.create(
            amount=2,
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
        cls.test_bikerental.bike_stock.set(
            [
                cls.test_bikeobject1.id,
                cls.test_bikeobject12.id
            ]
        )

        if Group.objects.filter(name="admin_group").count() == 0:
            cls.test_group_admin = Group.objects.create(name="admin_group")
            cls.test_group_admin.user_set.add(cls.test_user1)
        if Group.objects.filter(name="storage_group").count() == 0:
            cls.test_group_storage = Group.objects.create(name="storage_group")
            cls.test_group_storage.user_set.add(cls.test_user1)
        if Group.objects.filter(name="bicycle_group").count() == 0:
            cls.test_group_bicycle = Group.objects.create(name="bicycle_group")
            cls.test_group_bicycle.user_set.add(cls.test_user2)
            cls.test_group_bicycle.user_set.add(cls.test_user1)

    def login_test_user(self):
        url = "/users/login/"
        data = {
            "username": "bikeadmin@turku.fi",
            "password": "bikeadmin",
        }
        self.client.post(url, data, content_type="application/json")
        user = CustomUser.objects.get(username="bikeadmin@turku.fi")
        return user
    
    def login_test_user2(self):
        url = "/users/login/"
        data = {
            "username": "bikerperson@turku.fi",
            "password": "bikerperson",
        }
        self.client.post(url, data, content_type="application/json")
        user = CustomUser.objects.get(username="bikerperson@turku.fi")
        return user

    def test_post_bikemodel(self):
        url = "/bikes/models/"
        self.login_test_user()
        data = {
            "name": "Big bike",
            "size": self.test_bikesize.id,
            "brand": self.test_bikebrand.id,
            "type": self.test_biketype.id,
            "color": self.test_color.id,
            "description": "A very large bike",
        }

        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Bike.objects.all().count(), 3)

    def test_post_bikesize(self):
        url = "/bikes/size/"
        self.login_test_user()
        data = {
            "name": "99¨"
        }

        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(BikeSize.objects.all().count(), 2)

    def test_post_biketype(self):
        url = "/bikes/type/"
        self.login_test_user()
        data = {
            "name": "Electric"
        }

        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(BikeType.objects.all().count(), 2)

    def test_post_bikebrand(self):
        url = "/bikes/brand/"
        self.login_test_user()
        data = {
            "name": "Kuraharawa"
        }

        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(BikeBrand.objects.all().count(), 2)

    def test_post_bikerental(self):
        url = "/bikes/rental/"
        self.login_test_user2()
        data = {
            "bike_stock": {
            f"package-{self.test_bikepackage1.id}": 1,
            f"{self.test_bikemodel.id}": 1
            },
            "start_date": timezone.now(),
            "end_date": timezone.now(),
            "delivery_address": "bikestreet 123",
            "pickup": False,
            "contact_name": "Bikeman",
            "contact_phone_number": "123456789",
            "extra_info": "I like bikes"
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(BikeRental.objects.all().count(), 2)
        self.assertEqual(len(response.data["bike_stock"]), 3)

    def test_post_bikerental_bad_request(self):
        url = "/bikes/rental/"
        self.login_test_user2()
        data = {
            "delivery_address": "bikestreet 123",
            "pickup": False,
            "contact_name": "Bikeman",
            "contact_phone_number": "123456789",
            "extra_info": "I like bikes"
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_post_bikepackage(self):
        url = "/bikes/packages/"
        self.login_test_user()
        data = {
            "name": "package500",
            "description": "500package",
            "bikes": [
                {
                    "amount": 1,
                    "bike": self.test_bikemodel.id
                }
            ]
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(BikePackage.objects.all().count(), 2)
        print(response.data)

    def test_update_bikepackage_part1(self):
        url = f"/bikes/packages/{self.test_bikepackage1.id}/"
        self.login_test_user()
        data = {
            "name": "package-x",
            "description": "package for undefined purposes",
            "bikes": [
                {
                    "amount": 2,
                    "bike": self.test_bikemodel2.id
                }
            ]
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BikePackage.objects.all().count(), 1)
        print(response.data)

    def test_update_bikepackage_part2(self):
        url = f"/bikes/packages/{self.test_bikepackage1.id}/"
        self.login_test_user()
        data = {
            "name": "package-x",
            "description": "package for undefined purposes",
            "bikes": [
                {
                    "id": self.test_bikeamount1.id,
                    "amount": 3,
                    "bike": self.test_bikemodel.id
                }
            ]
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BikePackage.objects.all().count(), 1)
        print(response.data)

    def test_get_availability_info(self):
        url = "/bikes/"
        self.login_test_user2()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
