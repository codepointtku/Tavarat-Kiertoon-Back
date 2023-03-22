from django.test import TestCase

from contact_forms.models import ContactForm


class TestContactForms(TestCase):
    def setUp(self):
        self.test_contactform = ContactForm.objects.create(
            name="Kalle Kahvi",
            email="kkahvi@turku.fi",
            subject="kahvittelu",
            message="mennäänkö kahville?",
        )

    def test_self_contactform_string(self):
        self.assertEqual(
            str(self.test_contactform),
            f"{self.test_contactform.email}'s ContactForm({self.test_contanctform.id})"
        )