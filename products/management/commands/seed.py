import random
import urllib.request
from copy import copy
from datetime import datetime

from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from bulletins.models import Bulletin, BulletinSubject
from categories.models import Category
from contact_forms.models import Contact, ContactForm
from orders.models import Order, ShoppingCart
from orders.views import product_availibility_check
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
        self.stdout.write("Done. Superuser name is super and password is super. ")


def clear_data():
    """Deletes all the table data."""
    BulletinSubject.objects.all().delete()
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
    CustomUser.objects.all().delete()
    UserAddress.objects.all().delete()
    Group.objects.all().delete()


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
            "first_name": "Billy",
            "last_name": "Herrington",
            "email": "billy.herrington@turku.fi",
            "phone_number": "0000000000",
            "password": "testi",
            "address": "Katulantiekuja 22",
            "zip_code": "20100",
            "city": "Turku",
            "user_name": "",
            "joint_user": False,
        },
        {
            "first_name": "Sami",
            "last_name": "Imas",
            "email": "testi@turku.fi",
            "phone_number": "+358441234567",
            "password": "samionkuningas1987",
            "address": "Pizza on hyvää polku",
            "zip_code": "80085",
            "city": "Rauma",
            "user_name": "Samin mashausopisto",
            "joint_user": True,
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
            "user_name": "",
            "joint_user": False,
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
            "user_name": "",
            "joint_user": False,
        },
        {
            "first_name": "Jad",
            "last_name": "TzTok",
            "email": "TzTok-Jad@turku.fi",
            "phone_number": "702-079597",
            "password": "F-you-woox",
            "address": "TzHaar Fight Cave",
            "zip_code": "Wave 63",
            "city": "Brimhaven",
            "user_name": "",
            "joint_user": False,
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
            "user_name": "Kavhila",
            "joint_user": True,
        },
    ]
    CustomUser.objects.create_superuser(user_name="super", password="super")
    for user in users:
        CustomUser.objects.create_user(
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            phone_number=user["phone_number"],
            password=user["password"],
            address=user["address"],
            zip_code=user["zip_code"],
            city=user["city"],
            user_name=user["user_name"],
            joint_user=user["joint_user"],
        )


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
    categories = Category.objects.filter(level=2)
    colors = Color.objects.all()
    storages = Storage.objects.all()
    pictures = Picture.objects.all()
    for product in products:
        same_products = []
        product_object = Product(
            name=product["name"],
            group_id=product["group_id"],
            barcode=product["barcode"],
            free_description=product["free_description"],
            category=random.choice(categories),
            color=random.choice(colors),
            storages=random.choice(storages),
        )
        for _ in range(
            random.choices(
                range(1, 11), cum_weights=[10, 15, 18, 20, 21, 22, 23, 24, 25, 26]
            )[0]
        ):
            same_products.append(copy(product_object))
            same_products[-1].available = random.choice(true_false)
        Product.objects.bulk_create(same_products)
    queryset = Product.objects.all()
    for query in queryset:
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
    queryset = ShoppingCart.objects.all()
    products = list(Product.objects.filter(available=True))
    for query in queryset:
        query.products.set(random.sample(products, random.randint(1, 6)))


def create_orders():
    users = CustomUser.objects.filter(is_admin=False)
    statuses = ["Waiting", "Delivery", "Finished"]
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
                UserAddress.objects.filter(linked_user=user)
            ).address,
            contact=user.email,
            order_info=random.choice(order_infos),
            delivery_date=datetime.now(tz=timezone.utc),
        )
        order_obj.save()
        for product_id in product_availibility_check(user.id):
            order_obj.products.add(product_id)


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
    queryset = Bulletin.objects.all()
    bulletin_subjects = BulletinSubject.objects.all()
    for query in queryset:
        query.subject.set(
            [
                random.choice(bulletin_subjects),
                random.choice(bulletin_subjects),
                random.choice(bulletin_subjects),
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

    create_contact_forms()
    create_bulletin_subjects()
    create_colors()
    create_groups()
    create_storages()
    create_categories()
    create_users()
    for _ in range(6):
        create_picture()
    create_products()
    create_shopping_carts()
    create_orders()
    create_bulletins()
    create_contacts()
