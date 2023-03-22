from django.test import TestCase
from users.models import CustomUser, UserAddress, Group

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
        
        self.assertNotEqual(2,3)
        self.assertEqual(CustomUser.objects.count(),2)