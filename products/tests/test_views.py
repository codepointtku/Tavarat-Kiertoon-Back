import urllib.request

from django.test import TestCase
from django.urls import reverse
from django.core.files.base import ContentFile
from django.utils import timezone

from products.models import Product, Picture, Color, Storage
from categories.models import Category


class TestProduct(TestCase):
    def setUp(self):
        self.test_color = Color.objects.create(name="punainen")
        self.test_storage = Storage.objects.create(name="mokkavarasto")
        self.test_category = Category.objects.create(name="coffee")

        result = urllib.request.urlretrieve("https://picsum.photos/200")
        picture_object = Picture(
        picture_address=ContentFile(
            open(result[0], "rb").read(), name=f"{timezone.now().timestamp()}.jpg"
            )
        )
        picture_object.save()
        self.test_picture = picture_object

        self.test_product = Product.objects.create(
            name="nahkasohva", price=0, category=self.test_category,
            color=self.test_color, storages=self.test_storage
            )

    def test_get_colors(self): 
        url = "/colors/" 
        response = self.client.get(url) 
        self.assertEqual(response.status_code, 200)

    def test_get_categories(self):
        url = "/categories/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_storages(self):
        url = "/storages/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_pictures(self):
        url = "/pictures/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_products(self):
        url = "/products/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        print(Product.objects.all())
        print(self.test_product)

    def test_post_product_amount_multiple(self):
        url = "/products/"
        data = {
            "name": "nahkatuoli", "price": 0, "category": self.test_category.id,
            "color": self.test_color.id, "storages": self.test_storage.id, "amount": 2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        print(Product.objects.all())

    def test_post_product_color_as_string(self):
        url = "/products/"
        data = {
            "name": "nahkatuoli", "price": 0, "category": self.test_category.id,
            "color": "nahka", "storages": self.test_storage.id, "amount": 1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        print(Product.objects.all())

    def test_get_product(self):
        url = "/products/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
