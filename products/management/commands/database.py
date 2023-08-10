from csv import reader
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from categories.models import Category
from products.models import Color, Product, ProductItem, Storage

CustomUser = get_user_model()


class Command(BaseCommand):
    help = "Creates instances for database tables from csv files from old database"

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("Creating database...")
        run_database(self)
        self.stdout.write("Done.")


def clear_data():
    """Deletes all the database tables that this script populates"""

    CustomUser.objects.all().delete()
    Group.objects.all().delete()
    Color.objects.all().delete()
    Storage.objects.all().delete()
    Category.objects.all().delete()


def super_user():
    CustomUser.objects.create_superuser(username="super", password="super")


def groups():
    """creates the user groups for permissions"""
    groups = ["user_group", "admin_group", "storage_group", "bicycle_group"]
    for group in groups:
        Group.objects.create(name=group)


def colors():
    file = reader(open("tk-db/colors.csv"))
    next(file)
    for row in file:
        Color.objects.create(name=row[0])


def storages():
    file = reader(open("tk-db/storages.csv", encoding="utf8"))
    next(file)
    for row in file:
        Storage.objects.create(name=row[0], address="")


def products():
    file = reader(open("tk-db/products.csv", encoding="utf8"))
    header = next(file)
    products = {}
    for row in file:
        products[int(row[0])] = {header[1]: row[1], header[2]: row[2]}
    print(products)


def categories():
    """placeholder category for products"""
    Category.objects.create(name="Huonekalut")
    Category.objects.create(
        name="Tuolit", parent=Category.objects.get(name="Huonekalut")
    )
    Category.objects.create(
        name="Muut Tuolit", parent=Category.objects.get(name="Tuolit")
    )


def run_database(self):
    clear_data()
    super_user()
    groups()
    colors()
    storages()
    categories()
    products()
