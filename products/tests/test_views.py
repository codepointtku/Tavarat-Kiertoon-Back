import urllib.request

from os.path import basename

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
        self.test_parentcategory = Category.objects.create(name="coffee")
        self.test_category = Category.objects.create(name="subcoffee", parent=self.test_parentcategory)
        self.test_category1 = Category.objects.create(name="subcoffee2", parent=self.test_parentcategory)
        # result = urllib.request.urlretrieve("https://picsum.photos/200")
        # picture_object = Picture(
        # picture_address=ContentFile(
        #     open(result[0], "rb").read(), name=f"{timezone.now().timestamp()}.jpg"
        #     )
        # )
        # picture_object.save()
        self.test_picture = Picture.objects.create(picture_address="https://picsum.photos/200.jpg")
        self.test_picture1 = Picture.objects.create(picture_address="https://picsum.photos/200.jpg")

        self.test_product = Product.objects.create(
            name="nahkasohva", price=0, category=self.test_category,
            color=self.test_color, storages=self.test_storage
        )
        self.test_product1 = Product.objects.create(
            name="sohvanahka", price=0, category=self.test_category,
            color=self.test_color, storages=self.test_storage
        )

    def test_get_colors(self):
        url = "/colors/"
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

    def test_get_product(self):
        url = f"/products/{self.test_product.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_category_products(self):
        url = f"/categories/{self.test_parentcategory.id}/products/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_picture(self):
        picture = urllib.request.urlretrieve(url="https://picsum.photos/200.jpg", filename="testpicture.jpg")
        url = "/pictures/"
        data = {"file": open(picture[0], "rb")}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, 201)

    def test_post_multiple_products_multiple_pictures(self):
        url = "/products/"
        data = {
            "name": "nahkatuoli", "price": 0, "category": self.test_category.id,
            "color": self.test_color.id, "storages": self.test_storage.id, "amount": 3,
            "pictures": [self.test_picture.id, self.test_picture1.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_post_product_color_as_string(self):
        url = "/products/"
        colorstr = str("värikäs")
        data = {
            "name": "nahkanahka", "price": 0, "category": self.test_category.id,
            "color": colorstr, "storages": self.test_storage.id, "amount": 1,
            "pictures": [self.test_picture.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_post_product_existing_color_as_string(self):
        url = "/products/"
        colorstr = str("punainen")
        data = {
            "name": "nahkasika", "price": 0, "category": self.test_category.id,
            "color": colorstr, "storages": self.test_storage.id, "amount": 1,
            "pictures": [self.test_picture.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_self_color_string(self):
        self.assertEqual(str(self.test_color),
            f"Color: {self.test_color.name}({self.test_color.id})"
        )
    def test_self_storage_string(self):
        self.assertEqual(str(self.test_storage),
            f"Storage: {self.test_storage.name}({self.test_storage.id})"
        )
    def test_self_product_string(self):
        self.assertEqual(str(self.test_product),
            f"Product: {self.test_product.name}({self.test_product.id})"
        )
    def test_self_picture_string(self):
        self.assertEqual(str(self.test_picture),
            f"Picture: {basename(self.test_picture.picture_address.name)}({self.test_picture.id})"
        )
