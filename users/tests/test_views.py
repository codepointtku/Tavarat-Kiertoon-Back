from django.test import TestCase
from users.models import CustomUser, UserAddress, Group
from django.core.exceptions import ObjectDoesNotExist


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
        print("EKA")
        self.assertNotEqual(2,3)
        self.assertEqual(CustomUser.objects.count(),2)

    def test_get_users_forbidden(self):
        print("TOKA")
        url = "/users/"
        response = self.client.get(url)
        print("-----------------------------")
        print("testresponse: ",  response)
        self.assertEqual(response.status_code, 403)
    
    def test_post_user_creation(self):
        print("KOLMAS")
        current_user_number = CustomUser.objects.count()

        url = "/users/create/"

        data = {
            "first_name" : "testi",
            "last_name" : "tstilä",
            "email" : "testingly@turku.fi",
            "phone_number" : "54519145",
            "password" : "1234",
            "joint_user": "false",
            "username" : "testiiiing username",
            "address" : "testiläntie 12",
            "zip_code" : "12552",
            "city" : "TESTIKAUPUNKI",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        #print("luonnin jälkee: ", CustomUser.objects.count())
        after_first_creation = CustomUser.objects.count()
        self.assertNotEqual(current_user_number, after_first_creation)
        
        try:
            user = CustomUser.objects.get(username="testingly@turku.fi")
            print("not derp")
        except ObjectDoesNotExist:
            print("derp")
            user = None
        
        self.assertIsNotNone(user)
        
        imperfect_data = {
            "last_name" : "tstilä",
            "email" : "testingly@sssss.fi",
        }
        response = self.client.post(url, imperfect_data, content_type="application/json")
        self.assertEqual(response.status_code, 400)