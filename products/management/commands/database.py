import json
from csv import reader
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from categories.models import Category
from products.models import Color, Picture, Product, ProductItem, Storage

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
    Product.objects.all().delete()
    Picture.objects.all().delete()


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
    Storage.objects.create(
        name="Iso-Heikkilän Varasto",
        address="Iso-Heikkiläntie 6",
        zip_code="20200",
        city="Turku",
    )


def products():
    file = reader(open("tk-db/products_full.csv", encoding="utf8"))
    header = next(file)
    products = []
    for row in file:
        products.append(
            {
                header[0]: row[0],
                header[1]: row[1],
                header[2]: row[2],
                header[3]: row[3],
                header[4]: row[4],
                header[5]: row[5],
                header[6]: row[6],
                header[7]: row[7],
                header[8]: row[8],
                header[9]: row[9],
                header[10]: row[10],
                header[11]: row[11],
            }
        )
    for product in products:
        pictures = set(json.loads(product["file"]))
        for picture in pictures:
            if picture != None:
                Picture.objects.create(picture_address=picture)

        picture_objects = [
            Picture.objects.get(picture_address=picture_address).id
            for picture_address in pictures
            if picture_address != None
        ]

        color_objects = [
            Color.objects.get(name=color_name).id
            for color_name in json.loads(product["color"])
            if color_name != None
        ]

        free_description = product["free_description"]
        if free_description == "NULL":
            free_description = ""
        try:
            weight = float(product["weight"])
        except ValueError:
            weight = 0.0

        product_object = Product.objects.create(
            category=Category.objects.get(name="Muut Tuolit"),
            name=product["name"],
            price=float(product["price"]),
            free_description=free_description,
            # pictures
            measurements=product["measurements"],
            # colors
            weight=weight,
        )

        for _ in range(int(float(product["amount"]))):
            ProductItem.objects.create(
                product=product_object,
                available=True,
                storage=Storage.objects.get(name="Iso-Heikkilän Varasto"),
                barcode=product["barcode"],
            )

        if color_objects:
            product_object.colors.add(*color_objects)
        if picture_objects:
            product_object.pictures.add(*picture_objects)


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
