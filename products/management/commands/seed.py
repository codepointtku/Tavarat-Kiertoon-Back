from django.core.management.base import BaseCommand

from categories.models import Category
from products.models import Color, Storage

# python manage.py seed --mode=refresh

""" Clear all data and create objects."""
MODE_REFRESH = "refresh"

""" Clear all data and do not create any object."""
MODE_CLEAR = "clear"


class Command(BaseCommand):
    help = "Seed database for testing and development."

    def add_arguments(self, parser):
        parser.add_argument("--mode", type=str, help="Mode")

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")
        run_seed(self, options["mode"])
        self.stdout.write("Done.")


def clear_data():
    """Deletes all the table data."""
    Color.objects.all().delete()
    Storage.objects.all().delete()
    Category.objects.all().delete()


def create_colors():
    """Creates color objects from the list."""
    colors = ["Punainen", "Sininen", "Vihreä"]
    for color in colors:
        color_object = Color(name=color)
        color_object.save()
    return


def create_storages():
    """Creates storage objects from the list."""
    storages = [
        {"name": "Varasto X", "address": "Blabla 2b, 20230 Turku", "in_use": True},
        {"name": "Hieno varasto", "address": "Yoyo 1c, 20830 Turku", "in_use": True},
        {"name": "Pieni varasto", "address": "Hahhahhah, 20234 Turku", "in_use": False},
    ]
    for storage in storages:
        storage_object = Storage(
            name=storage["name"], address=storage["address"], in_use=storage["in_use"]
        )
        storage_object.save()
    return


def create_categories():
    """Creates category objects from the list."""
    categories = [
        {"name": "Huonekalut"},
        {"name": "Tuolit", "parent": "Huonekalut"},
        {"name": "Toimistotuolit", "parent": "Tuolit"},
        {"name": "Keittiökamat"},
        {"name": "Kahvinkeitin", "parent": "Keittiökamat"},
    ]
    for category in categories:
        if "parent" in category:
            parent_object = Category.objects.get(name=category["parent"])
            category_object = Category(name=category["name"], parent=parent_object)
        else:
            category_object = Category(name=category["name"])
        category_object.save()
    return


def run_seed(self, mode):
    """Seed database based on mode.

    :param mode: refresh / clear
    :return:
    """
    # Clear data from tables
    clear_data()
    if mode == MODE_CLEAR:
        return

    create_colors()
    create_storages()
    create_categories()
