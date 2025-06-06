from django.test import TestCase

from orders.models import Order, ShoppingCart
from users.models import CustomUser


class TestOrdersModels(TestCase):
    def setUp(self):
        self.test_user = CustomUser.objects.create_user(
            first_name="Kahvi",
            last_name="Make",
            email="kahvimake@turku.fi",
            phone_number="1112223344",
            password="Rekkamies88",
            address="Karvakuja 1",
            zip_code="100500",
            city="Puuhamaa",
            username="kahvimake@turku.fi",
            group="user_group",
        )
        self.test_user.is_active = True
        self.test_user.save()
        self.test_shoppingcart = ShoppingCart.objects.create(user=self.test_user)
        self.test_order = Order.objects.create(
            user=self.test_user, recipient_phone_number="1234567890"
        )

    def test_self_shoppingcart_string(self):
        self.assertEqual(
            str(self.test_shoppingcart),
            f"{self.test_shoppingcart.user}'s ShoppingCart({self.test_shoppingcart.id})",
        )

    def test_self_order_string(self):
        self.assertEqual(
            str(self.test_order),
            f"{self.test_order.user}'s Order({self.test_order.id})",
        )
