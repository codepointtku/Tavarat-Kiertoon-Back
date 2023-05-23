from django.test import TestCase

from categories.models import Category
from orders.models import Order, ShoppingCart
from products.models import Color, Product, ProductItem, Storage
from users.models import CustomUser


class TestOrders(TestCase):
    @classmethod
    def setUpTestData(cls):
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

        cls.test_color = Color.objects.create(name="punainen")
        cls.test_storage1 = Storage.objects.create(name="mokkavarasto")
        cls.test_storage2 = Storage.objects.create(name="italiangoldstorage")
        cls.test_parentcategory = Category.objects.create(name="coffee")
        cls.test_category1 = Category.objects.create(
            name="subcoffee", parent=cls.test_parentcategory
        )
        cls.test_category2 = Category.objects.create(
            name="subcoffee2", parent=cls.test_parentcategory
        )
        cls.test_product1 = Product.objects.create(
            category=cls.test_category1,
            name="nahkasohva",
            price=0,
            free_description="tämä sohva on nahkainen",
            color=cls.test_color,
            weight=50,
        )
        cls.test_product2 = Product.objects.create(
            category=cls.test_category2,
            name="sohvanahka",
            price=0,
            free_description="tämä nahka on sohvainen",
            color=cls.test_color,
            weight=50,
        )
        for i in range(5):
            available = True
            if i % 5 == 0:
                available = False
            cls.test_product_item1 = ProductItem.objects.create(
                product=cls.test_product1,
                available=available,
                storage=cls.test_storage1,
                shelf_id=1,
                barcode=1234,
            )

        cls.test_product_item3 = ProductItem.objects.create(
            product=cls.test_product2,
            available=True,
            storage=cls.test_storage2,
            shelf_id=2,
            barcode=1235,
        )
        cls.test_product_item4 = ProductItem.objects.create(
            product=cls.test_product2,
            available=True,
            storage=cls.test_storage2,
            shelf_id=2,
            barcode=1235,
        )
        cls.test_order = Order.objects.create(
            user=cls.test_user1, phone_number="1234567890"
        )
        cls.test_order.product_items.set(
            [ProductItem.objects.get(id=cls.test_product_item1.id)]
        )
        cls.test_shoppingcart = ShoppingCart.objects.create(user=cls.test_user1)
        cls.test_shoppingcart.product_items.set(
            ProductItem.objects.filter(product=cls.test_product2)
        )

    def test_post_shopping_cart(self):
        url = "/shopping_carts/"
        data = {
            "user": self.test_user1.id,
            "product_items": [self.test_product_item1.id],
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_post_shopping_cart_invalid(self):
        url = "/shopping_carts/"
        data = {
            "user": self.test_user1.id,
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_shopping_cart_getbyid_anonymous(self):
        url = "/shopping_cart/"
        response = self.client.get(url)
        self.assertEqual(
            response.content.decode(),
            '"You must be logged in to see your shoppingcart"',
        )

    def test_get_shopping_cart_doesnotexist(self):
        url = "/shopping_cart/"
        self.client.login(username="kahvimarkus@turku.fi", password="qwe456")
        response = self.client.get(url)
        self.assertEqual(
            response.content.decode(), '"Shopping cart for this user does not exist"'
        )

    def test_put_shopping_cart_doesnotexist(self):
        url = "/shopping_cart/"
        self.client.login(username="kahvimarkus@turku.fi", password="qwe456")
        response = self.client.put(url)
        self.assertEqual(
            response.content.decode(), '"Shopping cart for this user does not exist"'
        )

    def test_get_shopping_cart(self):
        url = "/shopping_cart/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        response = self.client.get(url)
        self.assertEqual(response.json()["user"], self.test_user1.id)

    def test_empty_shopping_cart(self):
        url = "/shopping_cart/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {"amount": -1}
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()["product_items"], [])

    def test_add_to_shopping_cart(self):
        url = "/shopping_cart/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {"product": self.test_product1.id, "amount": 1}
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(
            self.test_shoppingcart.product_items.filter(
                product=self.test_product1
            ).count(),
            1,
        )

    def test_add_to_shopping_cart_amountovermax(self):
        url = "/shopping_cart/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {"product": self.test_product1.id, "amount": 10}
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(
            self.test_shoppingcart.product_items.filter(
                product=self.test_product1
            ).count(),
            4,
        )

    def test_remove_from_shopping_cart(self):
        url = "/shopping_cart/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {"product": self.test_product1.id, "amount": 0}
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 202)

    def test_get_orders(self):
        url = "/orders/?status=Waiting"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_order(self):
        url = "/orders/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {
            "user": self.test_user1.id,
            "status": "Waiting",
            "delivery_address": "kuja123",
            "contact": "Antero Alakulo",
            "order_info": "nyrillataan",
            "phone_number": "99999",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

        data = {"user": self.test_user1.id}
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_get_order(self):
        url = f"/orders/{self.test_order.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_order_logged_user(self):
        url = f"/orders/user/"
        response = self.client.get(url)
        self.client.login(username="kahvimake@turku.fi", password="asd123")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_remove_products_from_order(self):
        url = f"/orders/{self.test_order.id}/"
        data = {
            "status": "Waiting",
            "delivery_address": "string",
            "contact": "string",
            "order_info": "string",
            "delivery_date": "2023-04-25T05:40:41.404Z",
            "phone_number": "11212121",
            "user": self.test_user1.id,
            "product_items": [],
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(
            [product_item.id for product_item in self.test_order.product_items.all()],
            [],
        )

    def test_update_order(self):
        url = f"/orders/{self.test_order.id}/"
        data = {
            "status": "Waiting",
            "delivery_address": "string",
            "contact": "string",
            "order_info": "string",
            "delivery_date": "2023-04-25T05:40:41.404Z",
            "phone_number": "11212121",
            "user": self.test_user1.id,
            "product_items": [
                product_item.id for product_item in self.test_order.product_items.all()
            ],
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 202)

        data = {
            "status": "Waiting",
            "user": self.test_user1.id,
            "phone_number": "11212121",
            "delivery_date": "asd",
            "products": [
                product_item.id for product_item in self.test_order.product_items.all()
            ],
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
