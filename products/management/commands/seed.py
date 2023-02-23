import random
import urllib.request

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from bulletins.models import Bulletin, BulletinSubject
from categories.models import Category
from contact_forms.models import Contact
from products.models import Color, Picture, Product, Storage
from users.models import CustomUser

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
        self.stdout.write("Remember to createsuperuser.")


def clear_data():
    """Deletes all the table data."""
    Color.objects.all().delete()
    Storage.objects.all().delete()
    Category.objects.all().delete()
    CustomUser.objects.all().delete()
    Picture.objects.all().delete()
    Product.objects.all().delete()
    BulletinSubject.objects.all().delete()
    Bulletin.objects.all().delete()
    Contact.objects.all().delete()


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
        {"email": "testi@turku.fi"},
        {"email": "testi2@turku.fi"},
    ]
    for user in users:
        user_object = CustomUser(email=user["email"])
        user_object.save()

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
    for product in products:
        product_object = Product(
            available=True,
            name=product["name"],
            free_description=product["free_description"],
            category=random.choice(Category.objects.all()),
            color=random.choice(Color.objects.all()),
            storages=random.choice(Storage.objects.all()),
        )
        product_object.save()
    queryset = Product.objects.all()
    for query in queryset:
        query.pictures.set(
            [
                random.choice(Picture.objects.all()),
                random.choice(Picture.objects.all()),
                random.choice(Picture.objects.all()),
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
    for bulletin in bulletins:
        bulletin_object = Bulletin(
            title=bulletin["title"],
            content=bulletin["content"],
            author=random.choice(CustomUser.objects.all()),
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


def run_seed(self, mode):
    """Seed database based on mode.

    :param mode: refresh / clear
    :return:
    """
    clear_data()
    if mode == MODE_CLEAR:
        return

    create_colors()
    create_storages()
    create_categories()
    create_users()
    for i in range(6):
        create_picture()
    create_products()
    create_bulletins()
    create_contacts()
