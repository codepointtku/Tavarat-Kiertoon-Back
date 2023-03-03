import random
import urllib.request
from copy import copy

from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from bulletins.models import Bulletin, BulletinSubject
from categories.models import Category
from contact_forms.models import Contact, ContactForm
from orders.models import Order, ShoppingCart
from products.models import Color, Picture, Product, Storage
from users.models import CustomUser, UserAddress

# python manage.py seed

"""Clear all data and create objects."""
MODE_REFRESH = "refresh"

"""Clear all data and do not create any object."""
MODE_CLEAR = "clear"


class Command(BaseCommand):
    help = "Seed database for testing and development."

    def add_arguments(self, parser):
        parser.add_argument("--mode", type=str, help="Mode")

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")
        run_seed(self, options["mode"])
        self.stdout.write("Done. Remember to createsuperuser if needed.")


def clear_data():
    """Deletes all the table data."""
    BulletinSubject.objects.all().delete()
    Bulletin.objects.all().delete()
    Category.objects.all().delete()
    # ContactForm
    Contact.objects.all().delete()
    ShoppingCart.objects.all().delete()
    # Order
    Color.objects.all().delete()
    Picture.objects.all().delete()
    Storage.objects.all().delete()
    Product.objects.all().delete()
    CustomUser.objects.all().delete()
    UserAddress.objects.all().delete()
    Group.objects.all().delete()


def create_bulletin_subjects():
    """Creates bulletin subjects from the list"""
    b_subjects = ["Yleinen", "Sivusto", "Mobiili"]
    for subject in b_subjects:
        b_subject_obj = BulletinSubject(name=subject)
        b_subject_obj.save()


def create_colors():
    """Creates color objects from the list."""
    colors = ["Punainen", "Sininen", "Vihreä"]
    for color in colors:
        color_object = Color(name=color)
        color_object.save()


def create_groups():
    """creates the user groups used in project"""
    groups = ["user_group", "admin_group", "storage_group", "bicycle_group"]
    for group in groups:
        group_object = Group(name=group)
        group_object.save()


def create_storages():
    """Creates storage objects from the list."""
    storages = [
        {"name": "Varasto X", "address": "Blabla 2b, 20230 Turku", "in_use": True},
        {"name": "Kahvivarasto", "address": "tonipal_kahville katu", "in_use": True},
        {"name": "Pieni varasto", "address": "Roskalava", "in_use": False},
    ]
    for storage in storages:
        storage_object = Storage(
            name=storage["name"], address=storage["address"], in_use=storage["in_use"]
        )
        storage_object.save()


def create_categories():
    """Creates category objects from the list."""
    categories = [
        {"name": "Huonekalut"},
        {"name": "Tuolit", "parent": "Huonekalut"},
        {"name": "Toimistotuolit", "parent": "Tuolit"},
        {"name": "Jakkarat", "parent": "Tuolit"},
        {"name": "Pöydät", "parent": "Huonekalut"},
        {"name": "Yöpöydät", "parent": "Pöydät"},
        {"name": "Ruokapöydät", "parent": "Pöydät"},
        {"name": "Elektroniikka"},
        {"name": "Keittiölaitteet", "parent": "Elektroniikka"},
        {"name": "Kahvinkeitin", "parent": "Keittiölaitteet"},
    ]
    for category in categories:
        if "parent" in category:
            parent_object = Category.objects.get(name=category["parent"])
            category_object = Category(name=category["name"], parent=parent_object)
        else:
            category_object = Category(name=category["name"])
        category_object.save()


def create_users():
    """Creates user objects from the list."""
    users = [
        {
            "user_name": "testi@turku.fi",
            "password": "testi",
            "email": "testi@turku.fi",
        },
        {
            "user_name": "kavhila@turku.fi",
            "password": "1234",
            "email": "kavhila@turku.fi",
        },
    ]
    # creating test super user
    # Fix Samis shit by using createsuperuser
    user_object_super = CustomUser(user_name="super", email="super")
    user_object_super.set_password(raw_password="super")
    user_object_super.is_admin = True
    user_object_super.is_staff = True
    user_object_super.is_superuser = True
    user_object_super.save()

    for user in users:
        user_object = CustomUser(user_name=user["user_name"], email=user["email"])
        user_object.set_password(raw_password=user["password"])
        user_object.save()
        group = Group.objects.get(name="user_group")
        user_object.groups.add(group)


def create_useraddress():
    """Creates user_address objects from the list."""
    user_addresses = [
        {"address": "Kebabbilan tie 1", "zip_code": "20210", "city": "Kebab"},
        {
            "address": "Chuck Norriksen Kartano 666",
            "zip_code": "60606",
            "city": "Manala",
        },
        {"address": "Pizza on hyvää polku", "zip_code": "123456789", "city": "Pitsa"},
    ]
    for address in user_addresses:
        address_object = UserAddress(
            address=address["address"],
            zip_code=address["zip_code"],
            city=address["city"],
            linked_user=CustomUser.objects.get(user_name="super"),
        )
        address_object.save()

    address_object = UserAddress(
        address="testila 1",
        zip_code="123456789",
        city="testi city",
        linked_user=CustomUser.objects.get(user_name="testi@turku.fi"),
    )
    address_object.save()


def create_picture():
    """Creates a picture object from an api."""
    result = urllib.request.urlretrieve("https://picsum.photos/200")
    picture_object = Picture(
        picture_address=ContentFile(
            open(result[0], "rb").read(), name=f"{timezone.now().timestamp()}.jpg"
        )
    )
    picture_object.save()


def create_products():
    """Creates product objects from the list."""
    products = [
        {
            "name": "Piirtoheitin",
            "free_description": "Hyväkuntone piirtoheitin suoraa 80-luvulta",
            "group_id": "1",
            "barcode": "1234",
        },
        {
            "name": "Jakkara",
            "free_description": "Eläköityneen rehtorin luotettava jakkara",
            "group_id": "2",
            "barcode": "1235",
        },
        {
            "name": "Bob Rossin pensselit",
            "free_description": "5 kpl setti eri paksusia, jouhet ok, vähän maalinjämiä",
            "group_id": "3",
            "barcode": "1236",
        },
        {
            "name": "Vichy-pullo",
            "free_description": "Tyhjä",
            "group_id": "4",
            "barcode": "1237",
        },
        {
            "name": "Kahvinkeitin",
            "free_description": "Alalemun koulu osti opehuoneeseen uuden mokkamasterin, tää wanha jäi ylimääräseks",
            "group_id": "5",
            "barcode": "1238",
        },
        {
            "name": "Joku missä on överipitkä teksti",
            "free_description": "Katotaas mitä tapahtuu kun tähän kirjoittaa ihan älyttömän mällin tekstiä, jos joku vaikka innostuu copypasteemaan tähän free_descriptioniin vahingossa koko users manualin viidellä eri kielellä ja silleenspäin pois ja tuolleen noin ja siitä ja puita!",
            "group_id": "6",
            "barcode": "1239",
        },
        {
            "name": "Työtuoli",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto. ",
            "group_id": "7",
            "barcode": "1240",
        },
        {
            "name": "Kahvikuppi",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
            "group_id": "8",
            "barcode": "1241",
        },
        {
            "name": "Kahvipaketti",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
            "group_id": "9",
            "barcode": "1242",
        },
        {
            "name": "Kahvimylly",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
            "group_id": "10",
            "barcode": "1243",
        },
        {
            "name": "Kahvipapu",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
            "group_id": "11",
            "barcode": "1244",
        },
        {
            "name": "Tonipal_kahville",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
            "group_id": "12",
            "barcode": "1245",
        },
        {
            "name": "Kahvipannu",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
            "group_id": "13",
            "barcode": "1246",
        },
        {
            "name": "Termoskannu",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
            "group_id": "14",
            "barcode": "1247",
        },
        {
            "name": "Kahvilautanen",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
            "group_id": "15",
            "barcode": "1248",
        },
        {
            "name": "Kahviaddiktio",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
            "group_id": "16",
            "barcode": "1249",
        },
    ]
    true_false = [1, 1, 1, 0]
    for product in products:
        same_products = []
        product_object = Product(
            name=product["name"],
            group_id=product["group_id"],
            barcode=product["barcode"],
            free_description=product["free_description"],
            category=random.choice(Category.objects.filter(level=2)),
            color=random.choice(Color.objects.all()),
            storages=random.choice(Storage.objects.all()),
        )
        for _ in range(
            random.choices(
                range(1, 11), cum_weights=[10, 13, 15, 16, 17, 18, 19, 20, 21, 22]
            )[0]
        ):
            same_products.append(copy(product_object))
            same_products[-1].available = random.choice(true_false)
        Product.objects.bulk_create(same_products)
    queryset = Product.objects.all()
    for query in queryset:
        query.pictures.set(
            [
                random.choice(Picture.objects.all()),
                random.choice(Picture.objects.all()),
                random.choice(Picture.objects.all()),
            ],
        )


def create_shopping_carts():
    users = CustomUser.objects.all()
    for user in users:
        cart_obj = ShoppingCart(user=user)
        cart_obj.save()
    queryset = ShoppingCart.objects.all()
    for query in queryset:
        query.products.set(
            random.sample(
                list(Product.objects.filter(available=True)), random.randint(1, 6)
            )
        )


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
    for bulletin in bulletins:
        bulletin_object = Bulletin(
            title=bulletin["title"],
            content=bulletin["content"],
            author=random.choice(CustomUser.objects.all()),
        )
        bulletin_object.save()
    queryset = Bulletin.objects.all()
    for query in queryset:
        query.subject.set(
            [
                random.choice(BulletinSubject.objects.all()),
                random.choice(BulletinSubject.objects.all()),
                random.choice(BulletinSubject.objects.all()),
            ]
        )


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


def run_seed(self, mode):
    """Seed database based on mode.

    :param mode: refresh / clear
    :return:
    """
    clear_data()
    if mode == MODE_CLEAR:
        return

    create_bulletin_subjects()
    create_colors()
    create_groups()
    create_storages()
    create_categories()
    create_users()
    create_useraddress()
    for i in range(6):
        create_picture()
    create_products()
    create_bulletins()
    create_contacts()
    create_shopping_carts()
