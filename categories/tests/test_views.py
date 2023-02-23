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
        print(self.test_category)
        print(self.test_category0)
        print(self.test_category1)
    def test_get(self):
        url = "/categories/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        url = "/categories/"
        data = {"name": "cup", "parent": 1}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    # def test_post_past_level_limit(self):
    #     url = "/categories/"
    #     data = {"name": "tea", "parent": 3}
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, 400)
        