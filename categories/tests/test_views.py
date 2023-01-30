from django.test import TestCase
from django.urls import reverse

from categories.models import Category


class TestCategories(TestCase):
    def setUp(self):
        self.test_category = Category.objects.create(name="coffee", parent=None)
        self.test_category0 = Category.objects.create(
            name="pot", parent=self.test_category
        )

    def test_get(self):
        url = "/categories/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        url = "/categories/"
        data = {"name": "cup", "parent": self.test_category0}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
