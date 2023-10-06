import json
from csv import reader
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps

from categories.models import Category
from orders.models import ShoppingCart
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
    ShoppingCart.objects.create(user=CustomUser.objects.get(username="super"))


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


def categories():
    """Categories"""
    categories = [
        {"name": "Huonekalut"},
        #
        #
        {"name": "Tuolit", "parent": "Huonekalut"},
        #
        {"name": "Toimistotuolit", "parent": "Tuolit"},
        {"name": "Penkit", "parent": "Tuolit"},
        {"name": "Muut tuolit", "parent": "Tuolit"},
        #
        {"name": "Pöydät", "parent": "Huonekalut"},
        #
        {"name": "Sähköpöydät", "parent": "Pöydät"},
        {"name": "Työpöydät", "parent": "Pöydät"},
        {"name": "Neuvottelupöydät", "parent": "Pöydät"},
        {"name": "Muut pöydät", "parent": "Pöydät"},
        #
        {"name": "Säilytys ja kaapit", "parent": "Huonekalut"},
        #
        {"name": "Kaapit", "parent": "Säilytys ja kaapit"},
        {"name": "Naulakot", "parent": "Säilytys ja kaapit"},
        {"name": "Lipastot", "parent": "Säilytys ja kaapit"},
        {"name": "Hyllyt", "parent": "Säilytys ja kaapit"},
        {"name": "Muu säilytys", "parent": "Säilytys ja kaapit"},
        #
        {"name": "Sisustus", "parent": "Huonekalut"},
        #
        {"name": "Taulut", "parent": "Sisustus"},
        {"name": "Muu sisustus", "parent": "Sisustus"},
        #
        #
        {"name": "Laitteet"},
        #
        {"name": "Kodinkoneet", "parent": "Laitteet"},
        #
        {"name": "Jääkaapit", "parent": "Kodinkoneet"},
        {"name": "Kahvinkeittimet", "parent": "Kodinkoneet"},
        {"name": "Muut kodinkoneet", "parent": "Kodinkoneet"},
        #
        {"name": "Toimisto elektroniikka", "parent": "Laitteet"},
        #
        {"name": "Näppäimistöt", "parent": "Toimisto elektroniikka"},
        {"name": "Näytöt", "parent": "Toimisto elektroniikka"},
        {"name": "Hiiret", "parent": "Toimisto elektroniikka"},
        {"name": "Videotykit", "parent": "Toimisto elektroniikka"},
        {"name": "Muu toimisto elektroniikka", "parent": "Toimisto elektroniikka"},
        #
        #
        {"name": "Askartelu"},
        #
        {"name": "Materiaalit", "parent": "Askartelu"},
        #
        {"name": "Tekstiilit", "parent": "Materiaalit"},
        {"name": "Maalit", "parent": "Materiaalit"},
        {"name": "Muut materiaalit", "parent": "Materiaalit"},
        #
        {"name": "Tarvikkeet", "parent": "Askartelu"},
        #
        {"name": "Napit ja vetoketjut", "parent": "Tarvikkeet"},
        {"name": "Muut tarvikkeet", "parent": "Tarvikkeet"},
        #
        {"name": "Välineet", "parent": "Askartelu"},
        #
        {"name": "Muut välineet", "parent": "Välineet"},
    ]
    for category in categories:
        if "parent" in category:
            Category.objects.create(
                name=category["name"],
                parent=Category.objects.get(name=category["parent"]),
            )
        else:
            Category.objects.create(name=category["name"])
    # Category.objects.create(name="", parent=Category.objects.get(name=""))


def products():
    file = reader(open("tk-db/products_full.csv", encoding="utf8"))
    header = next(file)
    category_names = [
        {"name": "Jääkaapit", "words": ["jääkaappi"]},
        {"name": "Kahvinkeittimet", "words": ["kahvinkeitin"]},
        {"name": "Näppäimistöt", "words": ["näppäimistö"]},
        {"name": "Näytöt", "words": ["näyttö", "tv"]},
        {"name": "Hiiret", "words": ["hiiri"]},
        {"name": "Videotykit", "words": ["videotykki"]},
        {"name": "Toimistotuolit", "words": ["toimistotuoli"]},
        {"name": "Penkit", "words": ["penkki"]},
        {"name": "Sähköpöydät", "words": ["sähköpöytä", "sähkötyöpöytä"]},
        {"name": "Työpöydät", "words": ["työpöytä", "pöytä"]},
        {"name": "Neuvottelupöydät", "words": ["neuvottelupöytä"]},
        {"name": "Hyllyt", "words": ["hylly"]},
        {"name": "Kaapit", "words": ["kaappi"]},
        {"name": "Naulakot", "words": ["naulakko"]},
        {"name": "Lipastot", "words": ["lipasto"]},
        {"name": "Taulut", "words": ["taulu"]},
        {"name": "Tekstiilit", "words": ["tekstiili", "kangas"]},
        {"name": "Maalit", "words": ["maali"]},
        {
            "name": "Napit ja vetoketjut",
            "words": ["nappi", "vetoketju", "nappeja", "vetoketjuja"],
        },
    ]
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
        pictures = list(set(json.loads(product["file"])))
        pictures.sort()
        for picture in pictures:
            if picture != None:
                with Image.open(f"tk-db/media/{picture}") as im:
                    im = ImageOps.exif_transpose(im)
                    im.thumbnail((600, 600))
                    im.save(f"media/{picture}")
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

        def find_category(product_name):
            for cat in category_names:
                for word in cat["words"]:
                    if product_name.lower() == word.lower():
                        return cat["name"]

            for cat in category_names:
                for word in cat["words"]:
                    if product_name.lower() in word.lower():
                        return cat["name"]

            for cat in category_names:
                for word in cat["words"]:
                    if word.lower() in product_name.lower():
                        return cat["name"]

            return "Muut tuolit"

        product_object = Product.objects.create(
            category=Category.objects.get(name=find_category(product["name"])),
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


def run_database(self):
    clear_data()
    super_user()
    groups()
    colors()
    storages()
    categories()
    self.stdout.write("Creating products, this might take a while")
    products()
