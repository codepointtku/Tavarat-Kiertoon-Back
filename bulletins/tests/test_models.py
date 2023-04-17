from django.test import TestCase

from bulletins.models import Bulletin


class TestBulletins(TestCase):
    def setUp(self):
        self.test_bulletin = Bulletin.objects.create(
            title="testbulletin",
            content="coffeetime",
        )

    def test_self_bulletin_string(self):
        self.assertEqual(
            str(self.test_bulletin),
            f"Bulletin: {self.test_bulletin.title} ({self.test_bulletin.id})",
        )
