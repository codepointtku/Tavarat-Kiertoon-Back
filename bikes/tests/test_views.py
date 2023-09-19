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

        if Group.objects.filter(name="admin_group").count() == 0:
            cls.test_group_admin = Group.objects.create(name="admin_group")
            cls.test_group_admin.user_set.add(cls.test_user1)
        if Group.objects.filter(name="user_group").count() == 0:
            cls.test_group_user = Group.objects.create(name="user_group")
            cls.test_group_user.user_set.add(cls.test_user1)
            cls.test_group_user.user_set.add(cls.test_user2)
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
        self.assertEqual(Bike.objects.all().count(), 1)

    def test_post_bikesize(self):
        url = "/bikes/size/"
        self.login_test_user()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BikeSize.objects.all().count(), 1)
