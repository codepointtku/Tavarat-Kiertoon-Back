import shutil
import urllib.request
from os.path import basename

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.utils import timezone

from categories.models import Category
from products.models import Color, Picture, Product, Storage
from users.models import CustomUser

TEST_DIR = "testmedia/"


class TestProducts(TestCase):
    @classmethod
    @override_settings(MEDIA_ROOT=TEST_DIR)
    def setUpTestData(cls):
        cls.test_color = Color.objects.create(name="punainen")
        cls.test_storage = Storage.objects.create(name="mokkavarasto")
        cls.test_storage1 = Storage.objects.create(name="italiangoldstorage")
        cls.test_parentcategory = Category.objects.create(name="coffee")
        cls.test_category = Category.objects.create(
            name="subcoffee", parent=cls.test_parentcategory
        )
        cls.test_category1 = Category.objects.create(
            name="subcoffee2", parent=cls.test_parentcategory
        )

        result = urllib.request.urlretrieve("https://picsum.photos/200")
        cls.test_picture = Picture.objects.create(
            picture_address=ContentFile(
                open(result[0], "rb").read(), name=f"{timezone.now().timestamp()}.jpeg"
            )
        )
        cls.test_picture1 = Picture.objects.create(
            picture_address=ContentFile(
                open(result[0], "rb").read(), name=f"{timezone.now().timestamp()}.jpeg"
            )
        )
        cls.test_product = Product.objects.create(
            name="nahkasohva",
            price=0,
            category=cls.test_category,
            color=cls.test_color,
            storages=cls.test_storage,
            available=True,
            free_description="tämä sohva on nahkainen",
            weight=50,
        )
        cls.test_product1 = Product.objects.create(
            name="sohvanahka",
            price=0,
            category=cls.test_category,
            color=cls.test_color,
            storages=cls.test_storage,
            available=True,
            free_description="tämä nahka on sohvainen",
            weight=50,
        )
        cls.user = CustomUser.objects.create_user(
            first_name="first_name",
            last_name="last_name",
            email="testi1@turku.fi",
            phone_number="phone_number",
            password="turku",
            address="address",
            zip_code="zip_code",
            city="city",
            username="testi1@turku.fi",
        )

        queryset = Product.objects.all()
        for query in queryset:
            query.pictures.set(
                [
                    Picture.objects.get(id=cls.test_picture.id),
                    Picture.objects.get(id=cls.test_picture1.id),
                ],
            )

    def login_test_user(self):
        url = "/users/login/"
        data = {
            "username": "testi1@turku.fi",
            "password": "turku",
        }
        self.client.post(url, data, content_type="application/json")
        a = CustomUser.objects.get(username="testi1@turku.fi")
        return a

    def test_get_colors(self):
        url = "/colors/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_storages(self):
        url = "/storages/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_products(self):
        url = "/products/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_storageview_products(self):
        url = "/storage/products/"
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
        url = f"/categories/tree/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_multiple_products_multiple_pictures(self):
        self.login_test_user()
        url = "/storage/products/"
        data = {
            "name": "nahkatuoli",
            "price": 0,
            "category": self.test_category.id,
            "color": self.test_color.id,
            "storages": self.test_storage.id,
            "amount": 3,
            "pictures": [self.test_picture.id, self.test_picture1.id],
            "available": True,
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    @override_settings(MEDIA_ROOT=TEST_DIR)
    def test_post_product_with_new_picture(self):
        self.login_test_user()
        picture = urllib.request.urlretrieve(
            url="https://picsum.photos/200.jpg",
            filename="testmedia/pictures/testpicture1.jpeg",
        )
        url = "/storage/products/"
        data = {
            "name": "tuolinahka",
            "price": 0,
            "category": self.test_category.id,
            "color": self.test_color.id,
            "storages": self.test_storage.id,
            "amount": 1,
            "pictures[]": {open(picture[0], "rb")},
            "available": False,
            "weight": 15,
            "free_description": "tämä tuoli on hieno",
        }
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, 201)

    def test_post_product_color_as_string(self):
        url = "/storage/products/"
        colorstr = str("värikäs")
        data = {
            "name": "puusohva",
            "price": 0,
            "category": self.test_category.id,
            "color": colorstr,
            "storages": self.test_storage.id,
            "amount": 1,
            "pictures": [self.test_picture.id],
            "weight": 100,
            "free_description": "umpipuinen sohva",
        }
        self.login_test_user()
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_post_product_existing_color_as_string(self):
        self.login_test_user()
        url = "/storage/products/"
        colorstr = str("punainen")
        data = {
            "name": "puutuoli",
            "price": 0,
            "category": self.test_category.id,
            "color": colorstr,
            "storages": self.test_storage.id,
            "amount": 1,
            "pictures": [self.test_picture.id],
            "weight": 40,
            "free_description": "kova puinen tuoli",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_update_products_storage(self):
        url = f"/products/transfer/"
        data = {
            "products": [self.test_product.id, self.test_picture1.id],
            "storage": self.test_storage1.id,
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_update_product_name(self):
        self.login_test_user()
        url = f"/products/{self.test_product.id}/"
        data = {"name": "kahvisohva"}
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_self_color_string(self):
        self.assertEqual(
            str(self.test_color), f"Color: {self.test_color.name}({self.test_color.id})"
        )

    def test_self_storage_string(self):
        self.assertEqual(
            str(self.test_storage),
            f"Storage: {self.test_storage.name}({self.test_storage.id})",
        )

    def test_self_product_string(self):
        self.assertEqual(
            str(self.test_product),
            f"Product: {self.test_product.name}({self.test_product.id})",
        )

    def test_self_picture_string(self):
        self.assertEqual(
            str(self.test_picture),
            f"Picture: {basename(self.test_picture.picture_address.name)}({self.test_picture.id})",
        )

    def tearDownClass():
        print("\nDeleting temporary files...\n")
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass
