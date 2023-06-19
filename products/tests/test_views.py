import shutil
import urllib.request
from os.path import basename

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.utils import timezone

from categories.models import Category
from orders.models import ShoppingCart
from products.models import Color, Picture, Product, ProductItem, Storage
from users.models import CustomUser

TEST_DIR = "testmedia/"


class TestProducts(TestCase):
    @classmethod
    @override_settings(MEDIA_ROOT=TEST_DIR)
    def setUpTestData(cls):
        cls.test_color = Color.objects.create(name="punainen")
        cls.test_color1 = Color.objects.create(name="sininen")
        cls.test_storage = Storage.objects.create(name="mokkavarasto")
        cls.test_storage1 = Storage.objects.create(name="italiangoldstorage")
        cls.test_parentcategory = Category.objects.create(name="huonekalut")
        cls.test_category = Category.objects.create(
            name="istuttavat huonekalut", parent=cls.test_parentcategory
        )
        cls.test_category1 = Category.objects.create(
            name="sohvat", parent=cls.test_category
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
            category=cls.test_category1,
            free_description="tämä sohva on nahkainen",
            measurements="210x100x90",
            weight=50,
        )
        cls.test_product1 = Product.objects.create(
            name="sohvanahka",
            price=0,
            category=cls.test_category1,
            free_description="tämä nahka on sohvainen",
            measurements="210x100x90",
            weight=50,
        )

        queryset = Product.objects.all()
        for query in queryset:
            query.pictures.set(
                [
                    Picture.objects.get(id=cls.test_picture.id),
                    Picture.objects.get(id=cls.test_picture1.id),
                ],
            ),
            query.color.set(
                [
                    Color.objects.get(id=cls.test_color.id),
                    Color.objects.get(id=cls.test_color1.id),
                ],
            )

        for productitem in range(10):
            cls.test_product_item = ProductItem.objects.create(
                product=cls.test_product,
                storage=cls.test_storage,
                available=True,
                shelf_id="12a",
                barcode=f"1000000{productitem}",
            )

        for productitem in range(10):
            cls.test_product_item1 = ProductItem.objects.create(
                product=cls.test_product1,
                storage=cls.test_storage,
                available=True,
                shelf_id="12b",
                barcode=f"2000000{productitem}",
            )

        cls.test_user1 = CustomUser.objects.create_user(
            first_name="Kahvi",
            last_name="Make",
            email="kahvimake@turku.fi",
            phone_number="1112223344",
            password="asd123",
            address="Karvakuja 1",
            zip_code="100500",
            city="Puuhamaa",
            username="kahvimake@turku.fi",
        )
        cls.test_user1.is_active = True
        cls.test_user1.save()

        cls.test_user2 = CustomUser.objects.create_user(
            first_name="Kahvimpi",
            last_name="Markus",
            email="kahvimarkus@turku.fi",
            phone_number="1112223323",
            password="qwe456",
            address="Karvakuja 2",
            zip_code="100500",
            city="Puuhamaa",
            username="kahvimarkus@turku.fi",
        )
        cls.test_user2.is_active = True
        cls.test_user2.save()

        cls.test_shoppingcart = ShoppingCart.objects.create(user=cls.test_user1)
        cls.test_shoppingcart.product_items.set(
            ProductItem.objects.filter(product=cls.test_product1)
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
        self.assertEqual(Product.objects.all().count(), 2)

    def test_get_productitems(self):
        url = "/products/items/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductItem.objects.all().count(), 20)

    def test_get_products_search(self):
        url = f"/products/?search={self.test_product.name}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_get_products_search_multiple_parameters(self):
        url = f"/products/?search=sohva&color={self.test_color.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)

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

    @override_settings(MEDIA_ROOT=TEST_DIR)
    def test_post_picture(self):
        picture = urllib.request.urlretrieve(
            url="https://picsum.photos/200.jpg",
            filename="testmedia/pictures/testpicture.jpeg",
        )
        url = "/pictures/"
        data = {"file": open(picture[0], "rb")}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, 201)

    def test_post_products_new_color(self):
        url = "/products/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {
            "product_item": {
                "available": True,
                "shelf_id": "asd12",
                "barcode": "30000001",
                "storage": self.test_storage.id,
            },
            "name": "nahkatuoli",
            "category": self.test_category1.id,
            "colors": ["punainen", "ruskea"],
            "free_description": "istuttava nahkainen tuoli",
            "measurements": "90x90x100",
            "weight": 20,
            "amount": 10,
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    @override_settings(MEDIA_ROOT=TEST_DIR)
    def test_post_product_with_new_picture(self):
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        picture = urllib.request.urlretrieve(
            url="https://picsum.photos/200.jpg",
            filename="testmedia/pictures/testpicture1.jpeg",
        )
        url = "/products/"
        data = {
            "product_item": {
                "available": True,
                "shelf_id": "asd12",
                "barcode": "30000001",
                "storage": self.test_storage.id,
            },
            "name": "tuolinahka",
            "category": self.test_category1.id,
            "colors": [str(self.test_color1.id)],
            "amount": 1,
            "pictures[]": {open(picture[0], "rb")},
            "weight": 15,
            "free_description": "tämä tuoli on hieno",
        }
        response = self.client.post(url, data, format="multipart")
        print(response)
        self.assertEqual(response.status_code, 201)

    def test_post_products_existing_color(self):
        url = "/products/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {
            "product_item": {
                "available": True,
                "shelf_id": "asd14",
                "barcode": "40000001",
                "storage": self.test_storage.id,
            },
            "name": "puusohva",
            "category": self.test_category1.id,
            "colors": [str(self.test_color.id)],
            "amount": 5,
            "weight": 100,
            "measurements": "100x90x190",
            "free_description": "umpipuinen sohva",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_post_product_existing_color_as_string(self):
        url = "/products/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {
            "product_item": {
                "available": True,
                "shelf_id": "asd15",
                "barcode": "50000001",
                "storage": self.test_storage1.id,
            },
            "name": "puutuoli",
            "category": self.test_category1.id,
            "colors": [str(self.test_color.id)],
            "amount": 7,
            "weight": 40,
            "measurements": "90x90x100",
            "free_description": "kova puinen tuoli",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_update_product_item(self):
        url = f"/products/items/{self.test_product_item.id}"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {"available": False, "modify_date": "asd"}
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_update_product_item_without_modify_date(self):
        url = f"/products/items/{self.test_product_item.id}"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {
            "available": False,
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_update_products_storage(self):
        url = "/products/transfer/"
        data = {
            "product_items": [self.test_product_item.id, self.test_product_item1.id],
            "storage": self.test_storage1.id,
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_update_product_name(self):
        url = f"/products/{self.test_product.id}/"
        data = {
            "name": "kahvisohva",
            "category": self.test_category1.id,
            "color": [self.test_color.id],
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_shoppingcart_available_amount_list(self):
        url = "/shopping_cart/available_amount/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_shoppingcart_available_amount_list_failed_attempts(self):
        url = "/shopping_cart/available_amount/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.login(username="kahvimarkus@turku.fi", password="qwe456")
        response = self.client.get(url)
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

    @classmethod
    def tearDownClass(self):
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass
        super().tearDownClass()
