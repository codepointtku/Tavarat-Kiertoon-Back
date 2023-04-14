from django.test import TestCase

from bulletins.models import Bulletin, BulletinSubject


class TestBulletins(TestCase):
    def setUp(self):
        self.test_bulletinsubject = BulletinSubject.objects.create(name="testsubject")
        self.test_bulletin = Bulletin.objects.create(
            title="testbulletin",
            content="coffeetime",
        )
        self.test_bulletin.subject.set([self.test_bulletinsubject])

    def test_self_bulletinsubject_string(self):
        self.assertEqual(
            str(self.test_bulletinsubject),
            f"BulletinSubject: {self.test_bulletinsubject.name} ({self.test_bulletinsubject.id})"
        )

    def test_self_bulletin_string(self):
        self.assertEqual(
            str(self.test_bulletin),
            f"Bulletin: {self.test_bulletin.title} ({self.test_bulletin.id})"
        )
