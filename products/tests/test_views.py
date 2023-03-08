import urllib.request
import shutil

from os.path import basename

from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.base import ContentFile
from django.utils import timezone

from products.models import Product, Picture, Color, Storage
from categories.models import Category

TEST_DIR = "testmedia/"

class TestProduct(TestCase):
    @classmethod
    @override_settings(MEDIA_ROOT=TEST_DIR) 
    def setUpTestData(cls):
        cls.test_color = Color.objects.create(name="punainen")
        cls.test_storage = Storage.objects.create(name="mokkavarasto")
        cls.test_parentcategory = Category.objects.create(name="coffee")
        cls.test_category = Category.objects.create(name="subcoffee", parent=cls.test_parentcategory)
        cls.test_category1 = Category.objects.create(name="subcoffee2", parent=cls.test_parentcategory)
        
        result = urllib.request.urlretrieve("https://picsum.photos/200")
        cls.test_picture = Picture.objects.create(picture_address=ContentFile(
                open(result[0], "rb").read(),
                name=f"{timezone.now().timestamp()}.jpeg"
            )
        )
        cls.test_picture1 = Picture.objects.create(picture_address=ContentFile(
                open(result[0], "rb").read(),
                name=f"{timezone.now().timestamp()}.jpeg"
            )
        )
        cls.test_product = Product.objects.create(
            name="nahkasohva", price=0, category=cls.test_category,
            color=cls.test_color, storages=cls.test_storage, available=True
        )
        cls.test_product1 = Product.objects.create(
            name="sohvanahka", price=0, category=cls.test_category,
            color=cls.test_color, storages=cls.test_storage, available=True
        )

        queryset = Product.objects.all()
        for query in queryset:
            query.pictures.set(
                [
                    Picture.objects.get(id=cls.test_picture.id),
                    Picture.objects.get(id=cls.test_picture1.id),
                ],
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

    def test_get_products_search(self):
        url = "/products/?search=sohva"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_products_search_multiple_parameters(self):
        url = f"/products/?search=sohva&color={self.test_color.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_products_paginate(self):
        url = "/products/?page=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_product_by_id(self):
        url = f"/products/{self.test_product.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_category_products(self):
        url = f"/categories/{self.test_parentcategory.id}/products/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(MEDIA_ROOT=TEST_DIR)
    def test_post_picture(self):
        picture = urllib.request.urlretrieve(
            url="https://picsum.photos/200.jpg",
            filename="testmedia/pictures/testpicture.jpeg"
        )
        url = "/pictures/"
        data = {"file": open(picture[0], "rb")}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, 201)

    def test_post_multiple_products_multiple_pictures(self):
        url = "/products/"
        data = {
            "name": "nahkatuoli", "price": 0, "category": self.test_category.id,
            "color": self.test_color.id, "storages": self.test_storage.id, "amount": 3,
            "pictures": [self.test_picture.id, self.test_picture1.id], "available": True
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    @override_settings(MEDIA_ROOT=TEST_DIR) 
    def test_post_product_with_new_picture(self):
        picture = urllib.request.urlretrieve(
            url="https://picsum.photos/200.jpg",
            filename="testmedia/pictures/testpicture1.jpeg"
        )
        url = "/products/"
        data = {
            "name": "tuolinahka", "price": 0, "category": self.test_category.id,
            "color": self.test_color.id, "storages": self.test_storage.id, "amount": 1,
            "pictures[]": {open(picture[0], "rb")}, "available": False
        }
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, 201)

    def test_post_product_color_as_string(self):
        url = "/products/"
        colorstr = str("värikäs")
        data = {
            "name": "puusohva", "price": 0, "category": self.test_category.id,
            "color": colorstr, "storages": self.test_storage.id, "amount": 1,
            "pictures": [self.test_picture.id]
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_post_product_existing_color_as_string(self):
        url = "/products/"
        colorstr = str("punainen")
        data = {
            "name": "puutuoli", "price": 0, "category": self.test_category.id,
            "color": colorstr, "storages": self.test_storage.id, "amount": 1,
            "pictures": [self.test_picture.id]
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
    
    def test_update_product(self):
        url = f"/products/{self.test_product.id}/"
        data = {
            "name": "kahvisohva"
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)

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

    def tearDownClass():
        print("\nDeleting temporary files...\n")
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass
