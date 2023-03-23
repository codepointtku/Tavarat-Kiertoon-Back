from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from orders.models import ShoppingCart
from users.models import CustomUser, Group, UserAddress


class TestUsers(TestCase):
    def setUp(self):
        groups = ["user_group", "admin_group", "storage_group", "bicycle_group"]
        for group in groups:
            group_object = Group(name=group)
            group_object.save()

        super = CustomUser.objects.create_superuser(username="super", password="super")
        for group in Group.objects.all():
            group.user_set.add(super)

        user = CustomUser.objects.create_user(
            first_name="first_name",
            last_name="last_name",
            email="email",
            phone_number="phone_number",
            password="password",
            address="address",
            zip_code="zip_code",
            city="city",
            username="username",
            joint_user="joint_user",
        )

    def test_setup(self):
        print("EKA, count user objs after setup?: ", CustomUser.objects.count())
        # self.assertNotEqual(2, 3)
        self.assertEqual(
            CustomUser.objects.count(),
            2,
            "testing setup, somethigng went wrong with setup",
        )

    def test_get_users_forbidden(self):
        """
        Testing forbiddenr responses from urls
        """
        print("TOKA")
        url = "/users/"
        response = self.client.get(url)
        print("-----------------------------")
        print("testresponse: ", response)
        self.assertEqual(response.status_code, 403)

    def test_post_user_creation(self):
        print("KOLMAS")
        current_user_number = CustomUser.objects.count()
        url = "/users/create/"

        # test GET not alloweed
        response = self.client.get(url)
        self.assertEqual(
            response.status_code, 405, "testing GET response, shoul not be allowed"
        )

        # test response with imperfect data
        imperfect_data = {
            "last_name": "tstilä",
            "email": "testingly@sssss.fi",
        }
        response = self.client.post(
            url, imperfect_data, content_type="application/json"
        )
        self.assertEqual(
            response.status_code, 400, "user creation should fail with not enough data"
        )

        # test response with correct data for normal user creation
        data = {
            "first_name": "testi",
            "last_name": "tstilä",
            "email": "testingly@turku.fi",
            "phone_number": "54519145",
            "password": "1234",
            "address": "testiläntie 12",
            "zip_code": "12552",
            "city": "TESTIKAUPUNKI",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code, 201, "user creation was not succesfull with POST"
        )
        # print("luonnin jälkee: ", CustomUser.objects.count())
        after_creation = CustomUser.objects.count()
        self.assertNotEqual(
            current_user_number,
            after_creation,
            "user number should be higher after user is created somethign failing",
        )
        current_user_number = CustomUser.objects.count()

        try:
            user = CustomUser.objects.get(username="testingly@turku.fi")
            print("not derp")
        except ObjectDoesNotExist:
            print("derp")
            user = None

        self.assertIsNotNone(user, "user was not created with correct data")
        # print("username: ", user.username)
        self.assertEqual(
            user.email, user.username, "normal user should have same username and email"
        )

        # testing that same user creation
        response = self.client.post(url, data, content_type="application/json")
        self.assertNotEqual(
            response.status_code,
            201,
            "user creation should not go through with same user info",
        )

        # testing that shopping cart was created for created user
        self.assertNotEqual(
            ShoppingCart.objects.filter(user=user).count(),
            0,
            "sometghing wrong with shopping cart creation for user",
        )

        # test taht not allowed webdomain doesnt go thru
        data["email"] = "thisiswrongemaildomain@wrong_email_domain.fi"
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code, 400, "should get bad request with wrong email domain"
        )

        # test taht not allowed webdomain doesnt go thru
        data["email"] = "thisiswrongemaildomain"
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code, 400, "should get bad request with wrong email(no @)"
        )

        # test response with correct data for joint user creation wrongly and then correct
        data = {
            "first_name": "testi",
            "last_name": "tstilä",
            "email": "testingly@turku.fi",
            "phone_number": "54519145",
            "password": "1234",
            "joint_user": "true",
            "username": "",
            "address": "testiläntie 12",
            "zip_code": "12552",
            "city": "TESTIKAUPUNKI",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            400,
            "Joint user creation not working, username check fails, empty should not go through",
        )

        data = {
            "first_name": "testi",
            "last_name": "tstilä",
            "email": "testingly@turku.fi",
            "phone_number": "54519145",
            "password": "1234",
            "joint_user": "true",
            "username": "testin päiväkoti",
            "address": "testiläntie 12",
            "zip_code": "12552",
            "city": "TESTIKAUPUNKI",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            201,
            "Joint user creation not working with correct data",
        )

        after_creation = CustomUser.objects.count()
        self.assertNotEqual(
            current_user_number,
            after_creation,
            "user number should be higher after user is created somethign failing",
        )
        current_user_number = CustomUser.objects.count()

        try:
            user = CustomUser.objects.get(username="testin päiväkoti")
            print("not derp")
        except ObjectDoesNotExist:
            print("derp")
            user = None

        self.assertIsNotNone(user, "user was not created with correct data")

        self.assertNotEqual(
            user.email,
            user.username,
            "joint user should have not same username and email",
        )

    def test_order(self):
        print("ENLAJS, count user objs after setup?: ", CustomUser.objects.count())
        self.assertNotEqual(2, 3)
        self.assertEqual(CustomUser.objects.count(), 2)
