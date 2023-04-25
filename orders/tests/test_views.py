from django.test import TestCase

from categories.models import Category
from orders.models import Order, ShoppingCart
from products.models import Color, Product, Storage
from users.models import CustomUser


class TestOrders(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = CustomUser.objects.create_user(
            first_name="Kahvi",
            last_name="Make",
            email="kahvimake@turku.fi",
            phone_number="1112223344",
            password="asd123",
            address="Karvakuja 1",
            zip_code="100500",
            city="Puuhamaa",
            username="kahvimaestro",
            joint_user=False,
        )
        cls.test_user1 = CustomUser.objects.create_user(
            first_name="Kahvimpi",
            last_name="Markus",
            email="kahvimarkus@turku.fi",
            phone_number="1112223323",
            password="qwe456",
            address="Karvakuja 2",
            zip_code="100500",
            city="Puuhamaa",
            username="nyrrillataa",
            joint_user=False,
        )
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
        cls.test_product = Product.objects.create(
            name="nahkasohva",
            group_id=1,
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
            group_id=909,
            price=0,
            category=cls.test_category,
            color=cls.test_color,
            storages=cls.test_storage,
            available=True,
            free_description="tämä nahka on sohvainen",
            weight=50,
        )
        cls.test_order = Order.objects.create(
            user=cls.test_user, phone_number="1234567890"
        )
        cls.test_order.products.set([Product.objects.get(id=cls.test_product1.id)])
        cls.test_shoppingcart = ShoppingCart.objects.create(user=cls.test_user)
        cls.test_shoppingcart.products.set(
            [Product.objects.get(id=cls.test_product.id)]
        )

    def test_post_shopping_cart(self):
        url = "/shopping_carts/"
        data = {"user": self.test_user.id, "products": [self.test_product.id]}
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
        self.assertEqual(response.json()["user"], self.test_user.id)

    def test_empty_shopping_cart(self):
        url = "/shopping_cart/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {"amount": 0}
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()["products"], [])

    def test_add_to_shopping_cart(self):
        url = "/shopping_cart/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {"products": self.test_product1.id, "amount": 1}
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 202)

    def test_add_to_shopping_cart_amountovermax(self):
        url = "/shopping_cart/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {"products": self.test_product1.id, "amount": 10}
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 202)

    def test_remove_from_shopping_cart(self):
        url = "/shopping_cart/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {"products": self.test_product.id, "amount": -1}
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 202)

    def test_remove_from_shopping_cart_amountovermax(self):
        url = "/shopping_cart/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {"products": self.test_product.id, "amount": -10}
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
            "user": self.test_user.id,
            "status": "Waiting",
            "delivery_address": "kuja123",
            "contact": "Antero Alakulo",
            "order_info": "nyrillataan",
            "phone_number": "99999",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

        data = {"user": self.test_user.id}
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
            "user": self.test_user.id,
            "products": [],
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual([product.id for product in self.test_order.products.all()], [])

    def test_update_order(self):
        url = f"/orders/{self.test_order.id}/"
        data = {
            "status": "Waiting",
            "delivery_address": "string",
            "contact": "string",
            "order_info": "string",
            "delivery_date": "2023-04-25T05:40:41.404Z",
            "phone_number": "11212121",
            "user": self.test_user.id,
            "products": [product.id for product in self.test_order.products.all()],
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 202)

        data = {
            "status": "Waiting",
            "user": self.test_user.id,
            "phone_number": "11212121",
            "delivery_date": "asd",
            "products": [product.id for product in self.test_order.products.all()],
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
