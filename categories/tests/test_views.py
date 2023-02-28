from django.test import TestCase
from django.urls import reverse

from categories.models import Category


class TestCategories(TestCase):
    def setUp(self):
        self.test_category = Category.objects.create(name="coffee")
        self.test_category0 = Category.objects.create(
            name="pot", parent=self.test_category
        )
        self.test_category1 = Category.objects.create(
            name="bean", parent=self.test_category0
        )

    def test_get(self):
        url = "/categories/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        url = "/categories/"
        data = {"name": "cup", "parent": self.test_category0.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_post_past_level_limit(self):
        url = "/categories/"
        data = {"name": "tea", "parent": self.test_category1.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_post_parent_none(self):
        url = "/categories/"
        data = {"name": "parentless", "parent": ""}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_post_invalid_serializer(self):
        url = "/categories/"
        data = {"parent": self.test_category0.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_self_string(self):
        self.assertEqual(str(self.test_category),
            f"Category: {self.test_category.name}({self.test_category.id})"
        )
        self.assertEqual(str(self.test_category0),(
            f"Category: {self.test_category0.name}({self.test_category0.id}) "
            f"Parent Category: {self.test_category0.parent.name}({self.test_category0.parent.id})"
        ))
