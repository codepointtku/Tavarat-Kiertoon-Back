import datetime

from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone

from categories.models import Category
from orders.models import Order, OrderEmailRecipient, ShoppingCart
from products.models import Color, Product, ProductItem, Storage
from users.models import CustomUser
from cron import clear_shopping_carts


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
            zip_code="100100",
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

        cls.test_user3 = CustomUser.objects.create_user(
            first_name="Cart",
            last_name="Man",
            email="cartman@turku.fi",
            phone_number="1111111111",
            password="eric",
            address="Katu 1",
            zip_code="10100",
            city="Kaupunki1",
            username="cartman@turku.fi",
        )
        cls.test_user3.is_active = True
        cls.test_user3.save()

        cls.test_user4 = CustomUser.objects.create_user(
            first_name="Cart",
            last_name="Man2",
            email="cartman2@turku.fi",
            phone_number="2222222222",
            password="eric2",
            address="Katu 2",
            zip_code="20200",
            city="Kaupunki2",
            username="cartman2@turku.fi",
        )
        cls.test_user4.is_active = True
        cls.test_user4.save()

        cls.test_user5 = CustomUser.objects.create_user(
            first_name="Cart",
            last_name="Man3",
            email="cartman3@turku.fi",
            phone_number="2222222222",
            password="eric3",
            address="Katu 3",
            zip_code="30300",
            city="Kaupunki3",
            username="cartman3@turku.fi",
        )
        cls.test_user5.is_active = True
        cls.test_user5.save()

        cls.test_color = Color.objects.create(name="punainen")
        cls.test_color1 = Color.objects.create(name="sininen")
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
            weight=50,
        )
        cls.test_product2 = Product.objects.create(
            category=cls.test_category2,
            name="sohvanahka",
            price=0,
            free_description="tämä nahka on sohvainen",
            weight=50,
        )
        cls.test_product3 = Product.objects.create(
            category=cls.test_category2,
            name="testikori",
            price=0,
            free_description="ostoskori",
            weight=10,
        )

        queryset = Product.objects.all()
        for query in queryset:
            query.colors.set(
                [
                    Color.objects.get(id=cls.test_color.id),
                    Color.objects.get(id=cls.test_color1.id),
                ],
            )

        cls.test_order_email_recipient = OrderEmailRecipient.objects.create(
            email="samimas@turku.fi"
        )

        for i in range(13):
            available = True
            if i % 5 == 0:
                available = False
            if i <= 5:
                cls.test_product_item1 = ProductItem.objects.create(
                    product=cls.test_product1,
                    available=available,
                    storage=cls.test_storage1,
                    shelf_id=1,
                    barcode=1234,
                )
            else:
                cls.test_product_item2 = ProductItem.objects.create(
                    product=cls.test_product2,
                    available=available,
                    storage=cls.test_storage2,
                    shelf_id=2,
                    barcode=1235,
                )
        for i in range(2):
            cls.test_product_item3 = ProductItem.objects.create(
                product=cls.test_product3,
                available=True,
                storage=cls.test_storage1,
                shelf_id=3,
                barcode=123456,
            )

        cls.test_order = Order.objects.create(
            user=cls.test_user1, recipient_phone_number="1234567890"
        )
        cls.test_order.product_items.set(
            [ProductItem.objects.get(id=cls.test_product_item1.id)]
        )

        cls.test_shoppingcart = ShoppingCart.objects.create(user=cls.test_user1)
        cls.test_shoppingcart.product_items.set(
            ProductItem.objects.filter(product=cls.test_product2)
        )
        cls.test_shoppingcart.product_items.add(
            ProductItem.objects.filter(
                product=cls.test_product1, available=True
            ).first()
        )

        cls.test_shoppingcart3 = ShoppingCart.objects.create(user=cls.test_user3)
        cls.test_shoppingcart3.product_items.add(
            ProductItem.objects.filter(product=cls.test_product3).first()
        )
        ShoppingCart.objects.filter(pk=cls.test_shoppingcart3.pk).update(
            date=timezone.now() - datetime.timedelta(hours=1)
        )
        cls.test_shoppingcart3.refresh_from_db()

        cls.test_shoppingcart4 = ShoppingCart.objects.create(user=cls.test_user4)
        cls.test_shoppingcart4.product_items.add(
            ProductItem.objects.filter(product=cls.test_product3).last()
        )
        ShoppingCart.objects.filter(pk=cls.test_shoppingcart4.pk).update(
            date=timezone.now() - datetime.timedelta(hours=3)
        )
        cls.test_shoppingcart4.refresh_from_db()

        cls.test_shoppingcart5 = ShoppingCart.objects.create(user=cls.test_user5)


        if Group.objects.filter(name="admin_group").count() == 0:
            cls.test_group_admin = Group.objects.create(name="admin_group")
            cls.test_group_admin.user_set.add(cls.test_user2)
            cls.test_group_admin.user_set.add(cls.test_user1)
        if Group.objects.filter(name="user_group").count() == 0:
            cls.test_group_user = Group.objects.create(name="user_group")
            cls.test_group_user.user_set.add(cls.test_user1)
            cls.test_group_user.user_set.add(cls.test_user2)
            cls.test_group_user.user_set.add(cls.test_user3)
            cls.test_group_user.user_set.add(cls.test_user4)
            cls.test_group_user.user_set.add(cls.test_user5)
        if Group.objects.filter(name="storage_group").count() == 0:
            cls.test_group_storage = Group.objects.create(name="storage_group")
            cls.test_group_storage.user_set.add(cls.test_user2)
            cls.test_group_storage.user_set.add(cls.test_user1)
        if Group.objects.filter(name="bicycle_group").count() == 0:
            cls.test_group_bicycle = Group.objects.create(name="bicycle_group")
            cls.test_group_bicycle.user_set.add(cls.test_user2)
            cls.test_group_bicycle.user_set.add(cls.test_user1)

    def login_test_user(self):
        url = "/users/login/"
        data = {
            "username": "kahvimarkus@turku.fi",
            "password": "qwe456",
        }
        self.client.post(url, data, content_type="application/json")
        user = CustomUser.objects.get(username="kahvimarkus@turku.fi")
        return user

    def login_test_user2(self):
        url = "/users/login/"
        data = {
            "username": "kahvimake@turku.fi",
            "password": "asd123",
        }
        self.client.post(url, data, content_type="application/json")
        user = CustomUser.objects.get(username="kahvimake@turku.fi")
        return user
    
    def login_test_user5(self):
        url = "/users/login/"
        data = {
            "username": "cartman3@turku.fi",
            "password": "eric3",
        }
        self.client.post(url, data, content_type="application/json")
        user = CustomUser.objects.get(username="cartman3@turku.fi")
        return user

    def test_post_shopping_cart(self):
        url = "/shopping_carts/"
        self.login_test_user()
        data = {
            "user": self.test_user1.id,
            "product_items": [self.test_product_item1.id],
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_post_shopping_cart_invalid(self):
        self.login_test_user()
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
        # self.assertEqual(
        #     response.status_code, 403, "when not logged in should be forbidden"
        # )

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
        self.assertEqual(
            response.json()["user"],
            CustomUser.objects.get(username="kahvimake@turku.fi").id,
        )

    def test_timed_clear_shopping_carts_function(self):
        clear_shopping_carts()
        self.assertNotEqual(list(self.test_shoppingcart3.product_items.values()), [])
        self.assertEqual(list(self.test_shoppingcart4.product_items.values()), [])

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
        data = {"product": self.test_product1.id, "amount": 2}
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(
            self.test_shoppingcart.product_items.filter(
                product=self.test_product1
            ).count(),
            2,
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
        self.assertEqual(
            self.test_shoppingcart.product_items.filter(
                product=self.test_product1
            ).count(),
            0,
        )

    def test_get_orders(self):
        self.login_test_user()
        url = "/orders/?status=Waiting"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_order(self):
        url = "/orders/"
        # self.client.login(username="kahvimake@turku.fi", password="asd123")
        self.login_test_user2()
        data = {
            "user": self.test_user1.id,
            "status": "Waiting",
            "recipient": "Antero Alakulo",
            "order_info": "nyrillataan",
            "recipient_phone_number": "99999",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.all().count(), 1)

        data = {
            "user": self.test_user1.id,
            "status": "Waiting",
            "delivery_address": "kuja123",
            "recipient": "Antero Alakulo",
            "order_info": "nyrillataan",
            "recipient_phone_number": "99999",
            "product_items": [self.test_product_item1.id],
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.all().count(), 2)

        data = {"user": self.test_user1.id}
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.all().count(), 2)

    def test_post_order_no_products(self):
        url = "/orders/"
        self.login_test_user5()
        data = {
            "user": self.test_user5.id,
            "recipient": "yes",
            "order_info": "no products",
            "recipient_phone_number": "2020202020",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, "Order has no products")

    def test_get_order(self):
        self.login_test_user()
        url = f"/orders/{self.test_order.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_order_logged_user(self):
        url = f"/orders/user/"
        response = self.client.get(url)
        self.client.login(username="kahvimake@turku.fi", password="asd123")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["results"][0]["user"]["id"],
            CustomUser.objects.get(username="kahvimake@turku.fi").id,
        )

    def test_remove_products_from_order(self):
        url = f"/orders/{self.test_order.id}/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {
            "status": "Waiting",
            "delivery_address": "string",
            "recipient": "string",
            "order_info": "string",
            "delivery_date": "2023-04-25T05:40:41.404Z",
            "recipient_phone_number": "11212121",
            "user": self.test_user1.id,
            "product_items": [],
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(
            response.json()["product_items"],
            [],
        )

    def test_update_order(self):
        url = f"/orders/{self.test_order.id}/"
        self.client.login(username="kahvimake@turku.fi", password="asd123")
        data = {
            "status": "Waiting",
            "delivery_address": "string",
            "recipient": "string",
            "order_info": "string",
            "delivery_date": "2023-04-25T05:40:41.404Z",
            "recipient_phone_number": "11212121",
            "user": self.test_user1.id,
            "product_items": [
                product_item.id
                for product_item in self.test_shoppingcart.product_items.all()
            ],
        }

        # filtering before posting order for correct list of items that should go through
        available_queryset = (
            self.test_shoppingcart.product_items.all()
            .filter(available=True)
            .values_list("id", flat=True)
            .order_by("id")
        )
        comparison_list = []
        for product_i in available_queryset:
            comparison_list.append(product_i)

        response = self.client.put(url, data, content_type="application/json")

        self.assertEqual(response.status_code, 202)
        self.assertQuerysetEqual(
            comparison_list,
            self.test_order.product_items.all()
            .values_list("id", flat=True)
            .order_by("id"),
        )

        data = {
            "status": "Waiting",
            "user": self.test_user1.id,
            "recipient_phone_number": "11212121",
            "delivery_date": "asd",
            "products": [
                product_item.id for product_item in self.test_order.product_items.all()
            ],
        }
        response = self.client.put(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_get_order_email_recipient(self):
        self.login_test_user()
        url = "/orders/emailrecipients/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        url = f"/orders/emailrecipients/{self.test_order_email_recipient.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_order_email_recipient(self):
        current_recipients = OrderEmailRecipient.objects.count()
        self.login_test_user()
        url = "/orders/emailrecipients/"
        response = self.client.post(
            url, {"email": "samsam@turku.fi"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(OrderEmailRecipient.objects.count(), current_recipients + 1)

        response = self.client.post(
            url, {"mail": "samsam@turku.fi"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_put_order_email_recipient(self):
        self.login_test_user()
        url = f"/orders/emailrecipients/{self.test_order_email_recipient.id}/"
        response = self.client.put(
            url, {"email": "samsam@turku.fi"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            OrderEmailRecipient.objects.get(
                id=self.test_order_email_recipient.id
            ).email,
            "samsam@turku.fi",
        )

        response = self.client.put(
            url, {"mail": "samsam@turku.fi"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_order_email_recipient(self):
        self.login_test_user()
        current_recipients = OrderEmailRecipient.objects.count()
        url = f"/orders/emailrecipients/{self.test_order_email_recipient.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(OrderEmailRecipient.objects.count(), current_recipients - 1)
