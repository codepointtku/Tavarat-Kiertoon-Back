import random
import urllib.request
import uuid

from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

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
from contact_forms.models import Contact
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
        self.stdout.write("Done.")


def clear_data():
    """Deletes all the table data."""
    Color.objects.all().delete()
    Storage.objects.all().delete()
    Category.objects.all().delete()
    CustomUser.objects.all().delete()
    Picture.objects.all().delete()
    Product.objects.all().delete()
    Bulletin.objects.all().delete()
    Contact.objects.all().delete()
    Group.objects.all().delete()
    UserAddress.objects.all().delete()
    Bike.objects.all().delete()
    BikeAmount.objects.all().delete()
    BikeBrand.objects.all().delete()
    BikePackage.objects.all().delete()
    BikeSize.objects.all().delete()
    BikeStock.objects.all().delete()
    BikeType.objects.all().delete()


def create_colors():
    """Creates color objects from the list."""
    colors = ["Punainen", "Sininen", "Vihreä", "Musta", "Valkoinen", "Ruskea"]
    for color in colors:
        color_object = Color(name=color)
        color_object.save()
    return


def create_groups():
    """creates the user groups used in project"""
    groups = ["user_group", "admin_group", "storage_group", "bicycle_group"]
    for group in groups:
        group_object = Group(name=group)
        group_object.save()
    return


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

    return


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

    return


def create_picture():
    """Creates a picture object from an api."""
    result = urllib.request.urlretrieve("https://picsum.photos/200")
    picture_object = Picture(
        picture_address=ContentFile(
            open(result[0], "rb").read(), name=f"{timezone.now().timestamp()}.jpg"
        )
    )
    picture_object.save()
    return


def create_products():
    """Creates product objects from the list."""
    products = [
        {
            "name": "Piirtoheitin",
            "free_description": "Hyväkuntone piirtoheitin suoraa 80-luvulta",
        },
        {
            "name": "Jakkara",
            "free_description": "Eläköityneen rehtorin luotettava jakkara",
        },
        {
            "name": "Bob Rossin pensselit",
            "free_description": "5 kpl setti eri paksusia, jouhet ok, vähän maalinjämiä",
        },
        {
            "name": "Vichy-pullo",
            "free_description": "Tyhjä",
        },
        {
            "name": "Kahvinkeitin",
            "free_description": "Alalemun koulu osti opehuoneeseen uuden mokkamasterin, tää wanha jäi ylimääräseks",
        },
        {
            "name": "Joku missä on överipitkä teksti",
            "free_description": "Katotaas mitä tapahtuu kun tähän kirjoittaa ihan älyttömän mällin tekstiä, jos joku vaikka innostuu copypasteemaan tähän free_descriptioniin vahingossa koko users manualin viidellä eri kielellä ja silleenspäin pois ja tuolleen noin ja siitä ja puita!",
        },
        {
            "name": "Työtuoli",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto. ",
        },
        {
            "name": "Kahvikuppi",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
        {
            "name": "Kahvikuppi",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
        {
            "name": "Kahvikuppi",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
        {
            "name": "Kahvinkeitin",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
        {
            "name": "Kahvipaketti",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
        {
            "name": "Kahvimylly",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
        {
            "name": "Kahvipapu",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
        {
            "name": "Tonipal_kahville",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
        {
            "name": "Kahvipannu",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
        {
            "name": "Termoskannu",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
        {
            "name": "Kahvilautanen",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
        {
            "name": "Kahviaddiktio",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
        {
            "name": "Jakkara",
            "free_description": "Tuotteen tarkempi kuvaus ja kunto.",
        },
    ]
    categories = Category.objects.all()
    colors = Color.objects.all()
    storages = Storage.objects.all()
    for product in products:
        product_object = Product(
            available=True,
            name=product["name"],
            free_description=product["free_description"],
            category=random.choice(categories),
            color=random.choice(colors),
            storages=random.choice(storages),
        )
        product_object.save()

    queryset = Product.objects.all()
    pictures = Picture.objects.all()
    for query in queryset:
        query.pictures.set(
            [
                random.choice(pictures),
                random.choice(pictures),
                random.choice(pictures),
            ],
        )
    return


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
    users = CustomUser.objects.all()
    for bulletin in bulletins:
        bulletin_object = Bulletin(
            title=bulletin["title"],
            content=bulletin["content"],
            author=random.choice(users),
        )
        bulletin_object.save()
    return


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
    return


def create_bike_brands():
    brands = ["Cannondale", "Woom"]
    for bike_brand in brands:
        brand_object = BikeBrand(name=bike_brand)
        brand_object.save()
    return


def create_bike_size():
    sizes = ["14″", "16″", "20″", "24″"]
    for bike_size in sizes:
        size_object = BikeSize(name=bike_size)
        size_object.save()
    return


def create_bike_types():
    types = ["BMX", "City", "Muksubussi", "Sähkö"]
    for bike_type in types:
        bike_object = BikeType(name=bike_type)
        bike_object.save()
    return


def create_bikes():
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
        )
        bike_object.save()
    return


def create_bike_stock():
    storages = Storage.objects.all()
    bikes = Bike.objects.all()
    for bike in bikes:
        for i in range(random.randint(3, 9)):
            stock_object = BikeStock(
                number=uuid.uuid4(),
                frame_number=uuid.uuid4(),
                bike=bike,
                storage=random.choice(storages),
            )
            stock_object.save()
    return


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
    return


def run_seed(self, mode):
    """Seed database based on mode.

    :param mode: refresh / clear
    :return:
    """
    clear_data()
    if mode == MODE_CLEAR:
        return

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
    create_bike_brands()
    create_bike_size()
    create_bike_types()
    create_bikes()
    create_bike_stock()
    create_bike_package()
