import random
import urllib.request
import uuid
from copy import copy
from datetime import datetime

from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
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
    BikeTrailerModel,
    BikeTrailer,
)
from bulletins.models import Bulletin
from categories.models import Category
from contact_forms.models import Contact, ContactForm
from orders.models import Order, OrderEmailRecipient, ShoppingCart
from products.models import (
    Color,
    Picture,
    Product,
    ProductItem,
    ProductItemLogEntry,
    Storage,
)
from pauseshop.models import Pause
from users.models import CustomUser, UserAddress

# python manage.py seed

"""Clear all data and create objects."""
MODE_REFRESH = "refresh"

"""Clear all data and do not create any object."""
MODE_CLEAR = "clear"

"""Create huge amounts of objects for testing"""
MODE_GIGA = "giga"


class Command(BaseCommand):
    help = "Seed database for testing and development."

    def add_arguments(self, parser):
        parser.add_argument("--mode", type=str, help="Mode")

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")
        run_seed(self, options["mode"])
        self.stdout.write("Done. Superuser name is super and password is super. ")


def clear_data():
    """Deletes all the table data."""
    OrderEmailRecipient.objects.all().delete()
    Bulletin.objects.all().delete()
    Category.objects.all().delete()
    ContactForm.objects.all().delete()
    Contact.objects.all().delete()
    ShoppingCart.objects.all().delete()
    Order.objects.all().delete()
    Color.objects.all().delete()
    Picture.objects.all().delete()
    Storage.objects.all().delete()
    Product.objects.all().delete()
    ProductItem.objects.all().delete()
    CustomUser.objects.all().delete()
    UserAddress.objects.all().delete()
    Bike.objects.all().delete()
    BikeAmount.objects.all().delete()
    BikeBrand.objects.all().delete()
    BikePackage.objects.all().delete()
    BikeSize.objects.all().delete()
    BikeStock.objects.all().delete()
    BikeType.objects.all().delete()
    Group.objects.all().delete()
    Pause.objects.all().delete()


def create_order_email_recipients():
    OrderEmailRecipient.objects.bulk_create(
        [
            OrderEmailRecipient(email="samimas@turku.fi"),
            OrderEmailRecipient(email="samsam@turku.fi"),
        ]
    )


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
            "status": "Not read",
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


def create_colors():
    """Creates color objects from the list."""
    colors = ["Punainen", "Sininen", "Vihreä", "Musta", "Valkoinen", "Ruskea"]
    for color in colors:
        color_object = Color(name=color, default=True)
        color_object.save()


def create_groups():
    """creates the user groups used in project"""
    groups = [
        "user_group",
        "admin_group",
        "storage_group",
        "bicycle_group",
        "bicycle_admin_group",
    ]
    for group in groups:
        group_object = Group(name=group)
        group_object.save()


def create_storages():
    """Creates storage objects from the list."""
    storages = [
        {
            "name": "Varasto X",
            "address": "Blabla 2b, 20230 Turku",
            "zip_code": "20100",
            "city": "Turku",
            "in_use": True,
        },
        {
            "name": "Kahvivarasto",
            "address": "tonipal_kahville katu",
            "zip_code": "20300",
            "city": "Turku",
            "in_use": True,
        },
        {
            "name": "Pieni varasto",
            "address": "Roskalava",
            "zip_code": "20200",
            "city": "Turku",
            "in_use": False,
        },
    ]
    for storage in storages:
        storage_object = Storage(
            name=storage["name"],
            address=storage["address"],
            zip_code=storage["zip_code"],
            city=storage["city"],
            in_use=storage["in_use"],
        )
        storage_object.save()


def create_categories():
    """Creates category objects from the list."""
    categories = [
        {"name": "Huonekalut"},
        {"name": "Tuolit", "parent": "Huonekalut"},
        {"name": "Pöydät", "parent": "Huonekalut"},
        {"name": "Sohvat", "parent": "Huonekalut"},
        {"name": "Kaapit", "parent": "Huonekalut"},
        #
        {"name": "Toimistotuolit", "parent": "Tuolit"},
        {"name": "Jakkarat", "parent": "Tuolit"},
        {"name": "Pallit", "parent": "Tuolit"},
        {"name": "Nojatuolit", "parent": "Tuolit"},
        #
        {"name": "Yöpöydät", "parent": "Pöydät"},
        {"name": "Päiväpöydät", "parent": "Pöydät"},
        {"name": "Ruokapöydät", "parent": "Pöydät"},
        {"name": "Sohvapöydät", "parent": "Pöydät"},
        {"name": "Apupöydät", "parent": "Pöydät"},
        #
        {"name": "Normaalit", "parent": "Sohvat"},
        {"name": "Erikois", "parent": "Sohvat"},
        #
        {"name": "Säilytyskaapit", "parent": "Kaapit"},
        {"name": "Hyllyt", "parent": "Kaapit"},
        {"name": "Arkistokaapit", "parent": "Kaapit"},
        #
        {"name": "Laitteet"},
        {"name": "Toimistotarvikkeet", "parent": "Laitteet"},
        {"name": "Elektroniikka", "parent": "Laitteet"},
        {"name": "Sekalaiset", "parent": "Toimistotarvikkeet"},
        {"name": "Keittiö", "parent": "Elektroniikka"},
        {"name": "Viihde-elektroniikka", "parent": "Elektroniikka"},
        {"name": "Oheislaitteet", "parent": "Toimistotarvikkeet"},
        #
        {"name": "Askartelu"},
        {"name": "Kynät", "parent": "Askartelu"},
        {"name": "Pensselit", "parent": "Askartelu"},
        {"name": "Paperit", "parent": "Askartelu"},
        {"name": "Maalit", "parent": "Askartelu"},
        {"name": "Tussit", "parent": "Askartelu"},
        #
        {"name": "Puuvärikynät", "parent": "Kynät"},
        {"name": "Lyijykynät", "parent": "Kynät"},
        {"name": "Hiilitikut", "parent": "Kynät"},
        {"name": "Paksut pensselit", "parent": "Pensselit"},
        {"name": "Hyvät pensselit", "parent": "Pensselit"},
        {"name": "Bob Rossin pensselit", "parent": "Pensselit"},
        {"name": "Viikset", "parent": "Pensselit"},
        {"name": "Piirrustuspaperit", "parent": "Paperit"},
        {"name": "Talouspaperit", "parent": "Paperit"},
        {"name": "Henkkarit", "parent": "Paperit"},
        {"name": "Sätkäpaperit", "parent": "Paperit"},
        {"name": "Akryylimaalit", "parent": "Maalit"},
        {"name": "Talomaalit", "parent": "Maalit"},
        {"name": "Vappumaalit", "parent": "Maalit"},
        {"name": "Faber Castell", "parent": "Tussit"},
        {"name": "Kuivuneet tussit", "parent": "Tussit"},
        {"name": "Hyvät tussit", "parent": "Tussit"},
    ]
    for category in categories:
        if "parent" in category:
            parent_object = Category.objects.get(name=category["parent"])
            category_object = Category(name=category["name"], parent=parent_object)
        else:
            category_object = Category(name=category["name"])
        category_object.save()


def create_users(mode):
    """Creates user objects from the list."""
    super = CustomUser.objects.create_superuser(username="super", password="super")
    super.phone_number = 900090009
    super.first_name = "Super"
    super.last_name = "Super"
    super.email = "super@turku.fi"
    super.group = "admin_group"
    super.save()
    UserAddress.objects.create(
        address="Superkatu6000", zip_code="9001", city="Superkylä", user=super
    )
    for group in Group.objects.all():
        group.user_set.add(super)
    if mode == "giga":
        for i in range(10, 1011):
            user = CustomUser.objects.create_user(
                first_name=f"first_name{i}",
                last_name=f"last_name{i}",
                email=f"email{i}@turku.fi",
                phone_number="0505556677",
                password=str(i),
                address=str(i),
                zip_code="20100",
                city="Mänttä-Vilppula",
                username=f"email{i}@turku.fi",
                group="user_group",
            )
            user.is_active = True
            user.save()

    else:
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


def create_picture():
    """Creates a picture object from an api."""
    result = urllib.request.urlretrieve("https://picsum.photos/200")
    picture_object = Picture(
        picture_address=ContentFile(
            open(result[0], "rb").read(), name=f"{timezone.now().timestamp()}.jpg"
        )
    )
    picture_object.save()


def create_products_and_product_items(mode):
    """Creates product objects from the list."""
    products = [
        {
            "name": "Toimistotuoli 1",
            "free_description": "Istumakorkeuden säätö, selkänojan säätö",
            "category": "Toimistotuolit",
        },
        {
            "name": "Toimistotuoli 2",
            "free_description": "Istumakorkeuden säätö, selkänojan säätö",
            "category": "Toimistotuolit",
        },
        {
            "name": "Wau toimistotuoli",
            "free_description": "Istumakorkeuden, selkänojan, ja käsinojien säädöt",
            "category": "Toimistotuolit",
        },
        {
            "name": "Eisveikee jakkara",
            "free_description": "Savolaista designia",
            "category": "Jakkarat",
        },
        {
            "name": "Simmone jakkara",
            "free_description": "Turkulaista käsityötä",
            "category": "Jakkarat",
        },
        {
            "name": "Kui jakkara",
            "free_description": "Aurajoesta poimittu jakkara",
            "category": "Jakkarat",
        },
        {
            "name": "Painava jakkara",
            "free_description": "Tammilevy, valurauta jalat",
            "category": "Jakkarat",
        },
        {
            "name": "Rehtorin palli",
            "free_description": "Luotettava, mukava istua",
            "category": "Pallit",
        },
        {
            "name": "Punainen palli",
            "free_description": "Selkänojaton ja käsinojaton tuolimalli",
            "category": "Pallit",
        },
        {
            "name": "Sisustus palli",
            "free_description": "Mitat: 33cm * 33cm, korkeus 40cm",
            "category": "Pallit",
        },
        {
            "name": "Pehmeä nojatuoli",
            "free_description": "On muute mukava istua, herra siunaa",
            "category": "Nojatuolit",
        },
        {
            "name": "Rentoutumis nojatuoli",
            "free_description": "Tähän voisi vaikka nukahtaa.",
            "category": "Nojatuolit",
        },
        {
            "name": "Design nojatuoli",
            "free_description": "Fartek tuoli 50-luvulta, kolmannessa puurimassa pieni halkeama",
            "category": "Nojatuolit",
        },
        {
            "name": "Kiikkutuoli",
            "free_description": "Ihan jees, hyvä tuoli vauvan sylittelyyn ja nukuttamiseen, mukava kiikkusäde",
            "category": "Nojatuolit",
        },
        {
            "name": "Yöpöytä 1",
            "free_description": "Jee",
            "category": "Yöpöydät",
        },
        {
            "name": "Yöpöytä 2",
            "free_description": "Jee jee",
            "category": "Yöpöydät",
        },
        {
            "name": "Pöytä",
            "free_description": "Tämä on pöytä. Sen päälle voi laskea asioita, ja siihen voi nojata.",
            "category": "Päiväpöydät",
        },
        {
            "name": "Iso työpöytä",
            "free_description": "Nii iso pöytä ettei se mahdu farmariautoon. Helkkari hyvä toimistohommiin.",
            "category": "Päiväpöydät",
        },
        {
            "name": "Massiivinen ruokapöytä",
            "free_description": "Tämän pöydän ääreen mahtuu koko kylä aterioimaan.",
            "category": "Ruokapöydät",
        },
        {
            "name": "Rekursiivinen ruokapöytä",
            "free_description": "Pöytä pöytä pöytä pöytä pöytä pöytä.....",
            "category": "Ruokapöydät",
        },
        {
            "name": "Resessiivinen ruokapöytä",
            "free_description": "Perinnöllisyystieteessä resessiivinen eli väistyvä ominaisuus tulee näkyviin yksilön ilmiasussa eli fenotyypissä vain, mikäli ominaisuuden aiheuttava alleeli on periytynyt yksilölle homotsygoottina eli samaperintäisenä. Jos genotyyppi on lokuksen suhteen heterotsygootti eli eriperintäinen, dominoiva alleeli määrää ilmiasun ja resessiivisellä alleelilla ei ole vaikutusta. Tämän vuoksi resessiivinen alleeli voi periytyä monen sukupolven yli ilman, että se tulee näkyviin ilmiasussa. ",
            "category": "Ruokapöydät",
        },
        {
            "name": "Sopivan kokoinen ruoka pöytä",
            "free_description": "Sopiva pöytä esimerkiksi päiväkotiin tai ala-asteelle, missä opetellaan yhdyssanoja.",
            "category": "Ruokapöydät",
        },
        {
            "name": "Soffan kaveri",
            "free_description": "Helppokäyttöinen, sekä aivan passeli viinilasille ja feta-lautaselle.",
            "category": "Sohvapöydät",
        },
        {
            "name": "Outo sohvapöytä",
            "free_description": "Vaikeaselkoinen, epämääräinen, ja hassun muotoinen, kuten isoäitinikin oli.",
            "category": "Sohvapöydät",
        },
        {
            "name": "Päällikkö sohvapöytä",
            "free_description": "Jämpti vehje.",
            "category": "Sohvapöydät",
        },
        {
            "name": "Avulias sivupöytä",
            "free_description": "Ystävällinen ja kätevä pöytä. Aina paikalla.",
            "category": "Apupöydät",
        },
        {
            "name": "Abupöytä",
            "free_description": "Aladdinin apinan innoittama pöydänkäppänä. Vekkuli laite.",
            "category": "Apupöydät",
        },
        {
            "name": "Sivupöytä",
            "free_description": "Pyörillä varustettu, säädettävä korkeus",
            "category": "Apupöydät",
        },
        {
            "name": "Kolmen istuttava sohva",
            "free_description": "Käynnistyy myös kylmällä + iskarit vaihdettu viime vuonna",
            "category": "Normaalit",
        },
        {
            "name": "Perus sohva",
            "free_description": "Klassikko muotoilu. Perusvarma. Hyvä istua.",
            "category": "Normaalit",
        },
        {
            "name": "Divaani",
            "free_description": "Kulmasohva tummansininen. Syyläri räkii ja pakari pitäis hitsata, muute ok",
            "category": "Erikois",
        },
        {
            "name": "Kova sohva",
            "free_description": "Kuin kirkonpenkki.",
            "category": "Erikois",
        },
        {
            "name": "Makuualustoja",
            "free_description": "Hyvät esimerkiksi päiväkodin nukkariin. 15kpl 6cm paksuja vaahtomuovialustoja",
            "category": "Erikois",
        },
        {
            "name": "80cm sänky",
            "free_description": "Leveys 80cm",
            "category": "Erikois",
        },
        {
            "name": "Jenkkisänky",
            "free_description": "Ei nitise.",
            "category": "Erikois",
        },
        {
            "name": "Rulokaappi",
            "free_description": "Alle 18000km ajettu, ilmanputsari vaihdettu. Kuskinpuoleinen ikkuna ei aukene, pelkääjänpuoleinen ovi jäätyy umpeen talvisin. Suht uudet kitkarenkaat.",
            "category": "Arkistokaapit",
        },
        {
            "name": "Tulokaappi",
            "free_description": "Palkkakuitit ja shekit tulevat tänne",
            "category": "Säilytyskaapit",
        },
        {
            "name": "Kulokaappi",
            "free_description": "Kuivassa ruohikossa tai metsän pintakasvillisuudessa tai myös puiden latvuksissa leviävä tuli, kulovalkea, metsäpalo.",
            "category": "Säilytyskaapit",
        },
        {
            "name": "Mul o kaappi",
            "free_description": "On, on!",
            "category": "Säilytyskaapit",
        },
        {
            "name": "Sul o kaappi",
            "free_description": "ON!",
            "category": "Säilytyskaapit",
        },
        {
            "name": "Hyllylevy",
            "free_description": "1 metri levee, joku 30cm syvä. Ei kannakkeita",
            "category": "Hyllyt",
        },
        {
            "name": "Vichy-pullo",
            "free_description": "Tyhjä",
            "category": "Keittiö",
        },
        {
            "name": "Nyssykkä",
            "free_description": "Tää on hyvä",
            "category": "Keittiö",
        },
        {
            "name": "Sähkövatkain",
            "free_description": "Semmone",
            "category": "Keittiö",
        },
        {
            "name": "Mikro",
            "free_description": "Juuri huollettu, Täysi huoltohistoria, jakoremmi vaihdettu 12000km sitten",
            "category": "Keittiö",
        },
        {
            "name": "Mikroaaltouuni",
            "free_description": "Pinttyneitä pastakastikkeen jämiä, mutta toimii täysin. Ei syö paljoa öljyä.",
            "category": "Keittiö",
        },
        {
            "name": "Minijääkaappi",
            "free_description": "Erään koulun edesmenneen talonmiehen minijäkis tarjolla. Vetää 6packin helposti, 1.5l vissypullo mahtuu pystyyn. Sähkönkulutus B-",
            "category": "Keittiö",
        },
        {
            "name": "Leivänpaahdin",
            "free_description": "Lämmittää mukavasti. Säädettävä paahtoaika.",
            "category": "Keittiö",
        },
        {
            "name": "Kahvinkeitin",
            "free_description": "Alalemun koulu osti opehuoneeseen uuden mokkamasterin, tää wanha jäi ylimääräseks",
            "category": "Keittiö",
        },
        {
            "name": "Keitin kahvin",
            "free_description": "Vain yhden. Olisikko sääki halunnu?",
            "category": "Keittiö",
        },
        {
            "name": "Akkuporakone",
            "free_description": "Tällä voi porata reikiä.",
            "category": "Viihde-elektroniikka",
        },
        {
            "name": "Ruuvinväännin",
            "free_description": "Vasara-ominaisuudella varustettu",
            "category": "Viihde-elektroniikka",
        },
        {
            "name": "Piikkausvasara",
            "free_description": "TRRRRRRRrr",
            "category": "Viihde-elektroniikka",
        },
        {
            "name": "Lehtipuhallin",
            "free_description": "Se laite mikä herättää sinut päiväunilta vapaapäivänäsi",
            "category": "Viihde-elektroniikka",
        },
        {
            "name": "Piirtoheitin",
            "free_description": "Wanha kunno piirto heiti",
            "category": "Oheislaitteet",
        },
        {
            "name": "Kasa johtoja",
            "free_description": "Erilaisia kaapeleita SCART USB HDMI kaikkee..",
            "category": "Oheislaitteet",
        },
        {
            "name": "Videotykki",
            "free_description": "Ok",
            "category": "Oheislaitteet",
        },
        {
            "name": "Videokangas",
            "free_description": "Ok",
            "category": "Oheislaitteet",
        },
        {
            "name": "Pöytätietokone",
            "free_description": "Benttium i19, ati-radeon viistonnine, 18 gigaa ram, ladan virtalähde, 256mb kiintolevy",
            "category": "Viihde-elektroniikka",
        },
        {
            "name": "Lihasvasara",
            "free_description": "Nopeus 220 bpm",
            "category": "Viihde-elektroniikka",
        },
        {
            "name": "Paperikansio",
            "free_description": "Hyvä kansio ja klemmarit päälle",
            "category": "Sekalaiset",
        },
        {
            "name": "Niittijuttukone",
            "free_description": "Se mil voi niitata paperei yhteen",
            "category": "Sekalaiset",
        },
    ]
    true_false = [1, 1, 1, 0]
    colors = Color.objects.all()
    storages = Storage.objects.all()
    pictures = Picture.objects.all()
    log_entry = ProductItemLogEntry.objects.create(
        action=ProductItemLogEntry.ActionChoices.CREATE,
        user=CustomUser.objects.get(username="super"),
    )
    barcode = 1234

    if mode == "giga":
        for _ in range(81):
            for product in products:
                storage = random.choice(storages)
                barcode += 1
                product_object = Product(
                    name=product["name"],
                    free_description=product["free_description"],
                    category=Category.objects.get(name=product["category"]),
                    measurements="",
                )
                product_object.save()
                for _ in range(1, random.randint(2, 8)):
                    product_item = ProductItem.objects.create(
                        product=product_object,
                        available=random.choice(true_false),
                        modified_date=timezone.now(),
                        storage=storage,
                        barcode=str(barcode),
                    )
                    product_item.log_entries.add(log_entry)
    else:
        for product in products:
            storage = random.choice(storages)
            barcode += 1
            product_object = Product(
                name=product["name"],
                free_description=product["free_description"],
                category=Category.objects.get(name=product["category"]),
                measurements="",
            )
            product_object.save()
            for _ in range(
                random.choices(
                    range(1, 11), cum_weights=[10, 15, 18, 20, 21, 22, 23, 24, 25, 26]
                )[0]
            ):
                product_item = ProductItem.objects.create(
                    product=product_object,
                    available=True,
                    modified_date=timezone.now(),
                    storage=storage,
                    barcode=str(barcode),
                )
                product_item.log_entries.add(log_entry)
    queryset = Product.objects.all()
    pictures = Picture.objects.all()
    for query in queryset:
        query.colors.set(
            [
                random.choice(colors),
                random.choice(colors),
            ]
        )
        query.pictures.set(
            [
                random.choice(pictures),
                random.choice(pictures),
                random.choice(pictures),
            ],
        )


def create_shopping_carts():
    users = CustomUser.objects.all()
    for user in users:
        cart_obj = ShoppingCart(user=user)
        cart_obj.save()
    shopping_carts = ShoppingCart.objects.all()
    for cart in shopping_carts:
        product_items = [
            product_item.id
            for product_item in ProductItem.objects.filter(available=True)
        ]
        if cart.user.username == "super":
            cart.product_items.set(random.sample(product_items, 5))
            for product_item in cart.product_items.all():
                product_item.available = False
                product_item.status = "In cart"
                product_item.save()
        else:
            cart.product_items.set(random.sample(product_items, random.randint(1, 6)))
            for product_item in cart.product_items.all():
                product_item.available = False
                product_item.status = "In cart"
                product_item.save()


def create_orders(mode):
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
    if mode == "giga":
        for i in range(10):
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
            for order in Order.objects.all():
                product_items = [
                    product_item.id
                    for product_item in ProductItem.objects.filter(available=True)
                ]
                order.product_items.set(
                    random.sample(product_items, random.randint(1, 6))
                )
    else:
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
        for order in Order.objects.all():
            product_items = [
                product_item.id
                for product_item in ProductItem.objects.filter(available=True)
            ]
            order.product_items.set(random.sample(product_items, random.randint(1, 6)))
            for product_item in order.product_items.all():
                product_item.available = False
                product_item.status = "Unavailable"
                product_item.save()


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


def create_contacts():
    contacts = [
        {
            "name": "Vesa Lehtonen",
            "address": "Iso-Heikkiläntie 6 20200 Turku",
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
    pictures = Picture.objects.all()
    for bike in bikes:
        bike_object = Bike(
            name=bike["name"],
            description=bike["description"],
            size=BikeSize.objects.get(name=bike["size"]),
            brand=random.choice(brands),
            type=random.choice(types),
            picture=random.choice(pictures),
        )
        bike_object.save()


def create_bike_stock():
    bikes = Bike.objects.all()
    colors = Color.objects.all()
    for bike in bikes:
        for _ in range(random.randint(7, 12)):
            stock_object = BikeStock(
                number=uuid.uuid4(),
                frame_number=uuid.uuid4(),
                bike=bike,
                color=random.choice(colors),
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


def create_bike_trailers():
    trailer_model = BikeTrailerModel(
        name="Peräkärry", description="Peräkärry pyöräpakettien kuljettamiseen"
    )
    trailer_model.save()

    trailers = [
        {
            "register_number": "ASD-123",
        },
        {
            "register_number": "QWE-123",
        },
        {
            "register_number": "ZXC-123",
        },
    ]
    for trailer in trailers:
        trailer_object = BikeTrailer(
            register_number=trailer["register_number"], trailer_type=trailer_model
        )
        trailer_object.save()


def run_seed(self, mode):
    """Seed database based on mode.

    :param mode: refresh / clear
    :return:
    """
    clear_data()
    if mode == MODE_CLEAR:
        return
    create_order_email_recipients()
    create_contact_forms()
    create_colors()
    create_groups()
    create_storages()
    create_categories()
    create_users(mode)
    for _ in range(6):
        create_picture()
    create_products_and_product_items(mode)
    create_shopping_carts()
    create_orders(mode)
    create_bulletins()
    create_contacts()
    create_bike_brands()
    create_bike_size()
    create_bike_types()
    create_bikes()
    create_bike_stock()
    create_bike_package()
    # create_bike_trailers()
