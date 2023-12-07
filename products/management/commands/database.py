import json
import random
import uuid
from csv import reader
from datetime import datetime
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageOps

from bikes.models import (
    Bike,
    BikeAmount,
    BikeBrand,
    BikePackage,
    BikeSize,
    BikeStock,
    BikeType,
)
from bulletins.models import Bulletin
from categories.models import Category
from contact_forms.models import Contact, ContactForm
from orders.models import Order, OrderEmailRecipient, ShoppingCart
from products.models import Color, Picture, Product, ProductItem, Storage
from users.models import UserAddress

CustomUser = get_user_model()

MODE_POPULATE = "populate"


class Command(BaseCommand):
    help = "Creates instances for database tables from csv files from old database"

    def add_arguments(self, parser):
        parser.add_argument("--mode", type=str, help="Mode")

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("Creating database...")
        run_database(self, options["mode"])
        self.stdout.write("Done.")


def clear_data(mode):
    """Deletes all the database tables that this script populates"""

    CustomUser.objects.all().delete()
    Group.objects.all().delete()
    Color.objects.all().delete()
    Storage.objects.all().delete()
    Category.objects.all().delete()
    Product.objects.all().delete()
    Picture.objects.all().delete()

    OrderEmailRecipient.objects.all().delete()
    Bulletin.objects.all().delete()
    ContactForm.objects.all().delete()
    Contact.objects.all().delete()
    ShoppingCart.objects.all().delete()
    Order.objects.all().delete()
    ProductItem.objects.all().delete()
    UserAddress.objects.all().delete()

    Bike.objects.all().delete()
    BikeAmount.objects.all().delete()
    BikeBrand.objects.all().delete()
    BikePackage.objects.all().delete()
    BikeSize.objects.all().delete()
    BikeStock.objects.all().delete()
    BikeType.objects.all().delete()


def groups():
    """creates the user groups for permissions"""
    groups = [
        "user_group",
        "admin_group",
        "storage_group",
        "bicycle_group",
        "bicycle_admin_group",
    ]
    for group in groups:
        Group.objects.create(name=group)


def super_user():
    super = CustomUser.objects.create_superuser(username="super", password="super")
    super.group = "admin_group"
    super.save()
    for group in Group.objects.all():
        group.user_set.add(super)


def colors():
    default_colors = [
        "Keltainen",
        "Sininen",
        "Punainen",
        "Vihreä",
        "Violetti",
        "Oranssi",
        "Musta",
        "Valkoinen",
        "Harmaa",
        "Ruskea",
    ]
    for color in default_colors:
        Color.objects.create(name=color, default=True)
    file = reader(open("tk-db/colors.csv", encoding="utf-8"))
    next(file)
    for row in file:
        if not row[0] in default_colors:
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
                    im.save(f"media/{picture.split('/')[-1]}")
                Picture.objects.create(picture_address=picture.split("/")[-1])

        picture_objects = [
            Picture.objects.get(picture_address=picture_address.split("/")[-1]).id
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
                status="Available",
            )

        if color_objects:
            product_object.colors.add(*color_objects)
        if picture_objects:
            product_object.pictures.add(*picture_objects)


def create_bike_brands():
    brands = ["Cannondale", "Woom"]
    for bike_brand in brands:
        brand_object = BikeBrand(name=bike_brand)
        brand_object.save()


def create_bike_size():
    sizes = ["14″", "16″", "20″", "24″"]
    for bike_size in sizes:
        size_object = BikeSize(name=bike_size)
        size_object.save()


def create_bike_types():
    types = ["BMX", "City", "Muksubussi", "Sähkö"]
    for bike_type in types:
        bike_object = BikeType(name=bike_type)
        bike_object.save()


def create_bikes():
    with Image.open(f"tk-db/media/Bike.jpg") as im:
        im = ImageOps.exif_transpose(im)
        im.thumbnail((600, 600))
        im.save(f"media/bike.jpg")
    picture = Picture.objects.create(picture_address="bike.jpg")
    bikes = [
        {
            "name": "Todella hieno pyörä",
            "description": "Hyväkuntonen hieno pyörä suoraa 80-luvulta",
            "size": "14″",
        },
        {"name": "Ihmisten pyörä", "description": "Ihmisille", "size": "16″"},
        {"name": "Wow pyörä", "description": "Se ajaa", "size": "20″"},
        {
            "name": "Ruosteinen pyörä",
            "description": "En suosittele tätä",
            "size": "24″",
        },
    ]
    types = BikeType.objects.all()
    brands = BikeBrand.objects.all()
    colors = Color.objects.all()
    for bike in bikes:
        bike_object = Bike(
            name=bike["name"],
            description=bike["description"],
            size=BikeSize.objects.get(name=bike["size"]),
            brand=random.choice(brands),
            type=random.choice(types),
            color=random.choice(colors),
            picture=picture,
        )
        bike_object.save()


def create_bike_stock():
    storages = Storage.objects.all()
    bikes = Bike.objects.all()
    colors = Color.objects.all()
    for bike in bikes:
        for _ in range(random.randint(7, 12)):
            stock_object = BikeStock(
                number=uuid.uuid4(),
                frame_number=uuid.uuid4(),
                bike=bike,
                color=random.choice(colors),
                storage=random.choice(storages),
                package_only=random.choice([True, False]),
            )
            stock_object.save()


def create_bike_package():
    packages = [
        {
            "name": "Päiväkoti -paketti",
            "description": "16″ pyöriä 7 kpl, 14″ pyöriä 3 kpl, potkupyöriä 10 kpl, pyöräilykypäriä 20 kpl, käsipumppu, jalkapumppu, monitoimityökalu",
            "bikes": [{"size": "14″", "amount": 3}, {"size": "16″", "amount": 7}],
        },
        {
            "name": "Koulu -paketti",
            "description": "20″ pyöriä 6 kpl, 24″ pyöriä 6 kpl, pyöräilykypäriä 13 kpl, käsipumppu, jalkapumppu, monitoimityökalu, molempia pyöriä olemassa 7 kpl, mutta tällä määrällä peräkärry on helppo lastata",
            "bikes": [{"size": "20″", "amount": 6}, {"size": "24″", "amount": 6}],
        },
    ]
    for package in packages:
        package_object = BikePackage(
            name=package["name"], description=package["description"]
        )
        package_object.save()
        package_object = BikePackage.objects.get(name=package["name"])
        for bike in package["bikes"]:
            bike_object = Bike.objects.get(size=BikeSize.objects.get(name=bike["size"]))
            amount_object = BikeAmount(
                bike=bike_object, amount=bike["amount"], package=package_object
            )
            amount_object.save()


def create_bulletins():
    bulletins = [
        {
            "title": "Varha:an ei voi tilata tuotteita",
            "content": "Varha:an ei voi tilata tuotteita, koska se on suljettu. Tilausjärjestelmä on kuitenkin käytössä, joten voit tilata tuotteita, mutta ne eivät tule koskaan perille. Tämä on vain testi.",
        },
        {
            "title": "Askartelua ja sähköpostia",
            "content": "Askartelutuotteidein tilaus on ollut pitkään tauolla mutta meillä on nyt ilo kertoa että askartelutuotteet ovat tulossa takaisin, tuotteita tullaan lisäämään lähiaikoina ja askartelutilauksia aletaan ottamaan taas vastaan. Tarkemmasta ajankohdasta tiedotamme tarkemmin myöhemmin. Tavarat kiertoon järjestelmä alkaa nyt myös lähettämään tilannetietoa tilauksista. Tästä päivästä lähtien järjestelmä lähettää tilaajalle viestin sähköpostilla kun tilaus otetaan käsittelyyn sekä kun tilaus on toimitettu.",
        },
        {
            "title": "Tavarat Kiertoon saatavilla nyt VPN yhteydellä",
            "content": "Tavarat Kiertoon palvelua on nyt mahdollista käyttää kaupungin verkon ulkopuolelta VPN yhteydellä. Jos sinulla on jo VPN käytössä niin sivustolle pääsee välittömästi ilman toimenpiteitä. Jos sinulla ei ole VPN yhteyttä mutta sinulla on tarve päästä Tavarat Kiertoon sivustolle kaupungin verkon ulkopuolelta, pyydä VPN palvelu ohjeiden mukaan.",
        },
        {
            "title": "Vanha osoite rv.ekotuki.net poistettu käytöstä",
            "content": "Vanha osoite rv.ekotuki.net poistettu käytöstä. Tavarat Kiertoon palvelu on nyt saatavilla osoitteessa https://tavaratkiertoon.fi",
        },
        {
            "title": "Hakuvahti ominaisuus lisätty järjestelmään",
            "content": "Hakuvahti ominaisuus lisätty järjestelmään. Voit nyt asettaa hakuvahdin tuotteille ja järjestelmä ilmoittaa sinulle sähköpostilla kun tuote on saatavilla. Hakuvahti löytyy tuotteen tiedoista. Hakuvahti on vielä testausvaiheessa joten toivomme palautetta käyttäjiltä järjestelmän toimivuudesta. Hyvää kesää & lomia Tavarat Kiertoon kehitystiimiltä!",
        },
        {
            "title": "Tavarat kiertävät taas, sekä uusi palvelin",
            "content": "Toimituksia aletaan taas tekemään ja tuotteita voi nyt taas tilata järjestelmästä. Päivitimme myös järjestelmän palvelimen joten palvelun pitäisi toimia entistä nopeammin. Jos kuitenkin ilmenee ongelmia niin ota ihmeessä yhteyttä !",
        },
    ]
    authors = CustomUser.objects.filter(is_admin=False)
    for bulletin in bulletins:
        bulletin_object = Bulletin(
            title=bulletin["title"],
            content=bulletin["content"],
            author=random.choice(authors),
        )
        bulletin_object.save()


def create_orders():
    users = CustomUser.objects.filter(is_admin=False)
    statuses = ["Waiting", "Processing", "Finished"]
    order_infos = [
        "Ethän tamma laukkoo, elä heinee vällii haakkoo "
        "Ravirata tuolla jo pilikistää "
        "Tehhään kunnon toto, vaikka köyhä meillon koto "
        "Yhtää kierrosta vällii ei jiä "
        "Sitä eei kukkaa pahakseen paa "
        "Liikoo rahhoo jos kerralla saa "
        "Sitä kertoo nyt ootan minäkin "
        "Meen Mossella iltaraveihin "
        "Ylämäki, alamäki "
        "Oottaa raviväki "
        "Lähtöä toista jo haikaillaan "
        "No elä tykkee pahhoo "
        "Kohta suahaan paljon rahhoo "
        "Köyhinä kuollaan jos aikaillaan "
        "Taskut ympäri nyt kiännetään "
        "Kohta rikkaina pois viännetään "
        "Tunnen varsasta mustan hevosen "
        "Jota ohjoo Toivo Ryynänen "
        "Lähtö koittaa kuka voittaa "
        "Sehän nähhään kohta "
        "Tyhjätaskuks vieläkkii jiähä minä suan "
        "Mossen vaihan mersun laitan "
        "Leivän päälle lohta "
        "Römppäs Veikon varmat kun pitäsivät vuan "
        "Takasuoralla Ryynänen jää "
        "Veikko vihjeineen joukkoon häviää "
        "Viikon piästä no niinpä tietenkin "
        "Tuun nikitalla iltaraveihin",
        "Tässä on tekstiä, joka kertoo lisää tilauksesta "
        "Tilauksessa on asioita joita haluan kertoa teille "
        "Tällä tekstillä kerron mitä ne asiat joita haluan kertoa on",
    ]
    for user in users:
        order_obj = Order(
            user=user,
            status=random.choice(statuses),
            delivery_address=random.choice(
                UserAddress.objects.filter(user=user)
            ).address,
            recipient=user.first_name + " " + user.last_name,
            order_info=random.choice(order_infos),
            delivery_date=datetime.now(tz=timezone.utc),
            recipient_phone_number=user.phone_number,
        )
        order_obj.save()
        for product_id in ShoppingCart.objects.get(user=user).product_items.all():
            order_obj.product_items.add(product_id)


def create_contact_forms():
    """Creates contanct_forms"""
    c_forms = [
        {
            "name": "Billy Herrington",
            "email": "testi@turku.fi",
            "subject": "Yöpöytä tilaus",
            "message": "Tilasin yöpöydän, mutta sain tonttutaulun sen sijasta. :(",
            "order_id": 10,
            "status": "Read",
        },
        {
            "name": "Sami Imas",
            "email": "kavhila@turku.fi",
            "subject": "Rikkinäinen pelituoli",
            "message": "Se on rikki",
            "order_id": 7,
            "status": "Ignored",
        },
    ]
    for c_form in c_forms:
        c_form_obj = ContactForm(
            name=c_form["name"],
            email=c_form["email"],
            subject=c_form["subject"],
            message=c_form["message"],
            order_id=c_form["order_id"],
            status=c_form["status"],
        )
        c_form_obj.save()


def create_users():
    """Creates user objects from the list."""
    users = [
        {
            "first_name": "Billy",
            "last_name": "Herrington",
            "email": "billy.herrington@turku.fi",
            "phone_number": "0000000000",
            "password": "testi",
            "address": "Katulantiekuja 22",
            "zip_code": "20100",
            "city": "Turku",
            "username": "billy.herrington@turku.fi",
            "group": "user_group",
        },
        {
            "first_name": "Sami",
            "last_name": "Imas",
            "email": "testi@turku.fi",
            "phone_number": "358441234567",
            "password": "samionkuningas1987",
            "address": "Pizza on hyvää polku",
            "zip_code": "80085",
            "city": "Rauma",
            "username": "Samin mashausopisto",
            "group": "user_group",
        },
        {
            "first_name": "Pekka",
            "last_name": "Python",
            "email": "pekka.python@turku.fi",
            "phone_number": "0401234567",
            "password": "password",
            "address": "Pythosentie 12",
            "zip_code": "22222",
            "city": "Lohja",
            "username": "pekka.python@turku.fi",
            "group": "user_group",
        },
        {
            "first_name": "Pirjo",
            "last_name": "Pythonen",
            "email": "pirjo.pythonen@turku.fi",
            "phone_number": "0501234567",
            "password": "salasana",
            "address": "Pythosentie 12",
            "zip_code": "22222",
            "city": "Lohja",
            "username": "pirjo.pythonen@turku.fi",
            "group": "user_group",
        },
        {
            "first_name": "Jad",
            "last_name": "TzTok",
            "email": "TzTok-Jad@turku.fi",
            "phone_number": "702079597",
            "password": "F-you-woox",
            "address": "TzHaar Fight Cave",
            "zip_code": "Wave 63",
            "city": "Brimhaven",
            "username": "TzTok-Jad@turku.fi",
            "group": "user_group",
        },
        {
            "first_name": "Kavhi",
            "last_name": "La",
            "email": "kavhi@turku.fi",
            "phone_number": "1112223344",
            "password": "kavhi123",
            "address": "kavhilantie 1",
            "zip_code": "20100",
            "city": "Turku",
            "username": "Kavhila",
            "group": "user_group",
        },
    ]

    for user in users:
        created_user = CustomUser.objects.create_user(
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            phone_number=user["phone_number"],
            password=user["password"],
            address=user["address"],
            zip_code=user["zip_code"],
            city=user["city"],
            username=user["username"],
            group=user["group"],
        )
        created_user.is_active = True
        created_user.save()


def create_shopping_carts(mode):
    users = CustomUser.objects.all()
    for user in users:
        cart_obj = ShoppingCart(user=user)
        cart_obj.save()
    if mode == "populate":
        shopping_carts = ShoppingCart.objects.all()
        product_items = [
            product_item.id
            for product_item in ProductItem.objects.filter(available=True)
        ]
        for cart in shopping_carts:
            if cart.user.username == "super":
                cart.product_items.set(random.sample(product_items, 5))
                for product_item in cart.product_items.all():
                    product_item.available = False
                    product_item.save()
            else:
                cart.product_items.set(
                    random.sample(product_items, random.randint(1, 6))
                )
                for product_item in cart.product_items.all():
                    product_item.available = False
                    product_item.save()


def create_contacts():
    contacts = [
        {
            "name": "Vesa Lehtonen",
            "address": "Rieskalähteentie 76, 20300 Turku",
            "email": "tyokeskus.kierratys@turku.fi",
            "phone_number": "+358 40 531 8689",
        }
    ]
    for contact in contacts:
        contact_object = Contact(
            name=contact["name"],
            address=contact["address"],
            email=contact["email"],
            phone_number=contact["phone_number"],
        )
        contact_object.save()


def create_order_email_recipients():
    OrderEmailRecipient.objects.bulk_create(
        [
            OrderEmailRecipient(email="samimas@turku.fi"),
            OrderEmailRecipient(email="samsam@turku.fi"),
        ]
    )


def run_database(self, mode):
    clear_data(mode)
    groups()
    super_user()
    colors()
    storages()
    categories()
    self.stdout.write("Creating products, this might take a while")
    products()
    if mode == "populate":
        self.stdout.write("Populating rest of the data tables")
        create_users()
        create_shopping_carts(mode)
        create_bike_brands()
        create_bike_size()
        create_bike_types()
        create_bikes()
        create_bike_stock()
        create_bike_package()
        create_bulletins()
        create_orders()
        create_contact_forms()
        create_contacts()
        create_order_email_recipients()
    else:
        create_shopping_carts(mode)
