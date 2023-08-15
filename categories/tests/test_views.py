from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from categories.models import Category
from users.models import CustomUser
from users.serializers import UsersLoginRefreshResponseSerializer

User = get_user_model()


class TestCategories(TestCase):
    # function for logging in test admin user to get cookeis to test admin user
    def login_test_admin(self):
        url = "/users/login/"
        data = {
            "username": "admin",
            "password": "admin",
        }
        user = User.objects.get(username="admin")
        # print("userin groupit: ", user.groups)
        ser = UsersLoginRefreshResponseSerializer(user)
        # print("ser check: ", ser.data["groups"])
        return user

    def setUp(self):
        self.test_category = Category.objects.create(name="coffee")
        self.test_category0 = Category.objects.create(
            name="pot", parent=self.test_category
        )
        self.test_category1 = Category.objects.create(
            name="bean", parent=self.test_category0
        )

        groups = ["user_group", "admin_group", "storage_group", "bicycle_group"]
        for group in groups:
            group_object = Group(name=group)
            group_object.save()

        user3_set = CustomUser.objects.create_user(
            first_name="admin",
            last_name="adming",
            email="admin@turku.fi",
            phone_number="admin",
            password="admin",
            address="admin",
            zip_code="admin",
            city="admin",
            username="admin",
        )
        user3_set.is_active = True
        user3_set.save()
        for group in Group.objects.all():
            group.user_set.add(user3_set)

    def test_get(self):
        self.login_test_admin()
        url = "/categories/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.login_test_admin()
        url = "/categories/"
        data = {"name": "cup", "parent": self.test_category0.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_post_past_level_limit(self):
        self.login_test_admin()
        url = "/categories/"
        data = {"name": "tea", "parent": self.test_category1.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_post_parent_none(self):
        self.login_test_admin()
        url = "/categories/"
        data = {"name": "parentless", "parent": ""}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_post_invalid_serializer(self):
        user = self.login_test_admin()
        # ser = UsersLoginRefreshResponseSerializer(user)
        # print("ser check: ", ser.data["groups"])

        url = "/categories/"
        data = {"parent": self.test_category0.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_self_string(self):
        self.login_test_admin()
        self.assertEqual(
            str(self.test_category),
            f"Category: {self.test_category.name}({self.test_category.id})",
        )
        self.assertEqual(
            str(self.test_category0),
            (
                f"Category: {self.test_category0.name}({self.test_category0.id}) "
                f"Parent Category: {self.test_category0.parent.name}({self.test_category0.parent.id})"
            ),
        )
