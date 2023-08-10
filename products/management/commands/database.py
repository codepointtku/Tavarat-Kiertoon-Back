from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from products.models import Color

CustomUser = get_user_model()


class Command(BaseCommand):
    help = "Creates instances for database tables from csv files from old database"

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("Creating database...")
        run_database(self)
        self.stdout.write("Done.")


def clear_data():
    """Deletes all the database tables that this script populates"""
    Color.objects.all().delete()
    CustomUser.objects.all().delete()
    Group.objects.all().delete()


def super_user():
    CustomUser.objects.create_superuser(username="super", password="super")


def groups():
    """creates the user groups for permissions"""
    groups = ["user_group", "admin_group", "storage_group", "bicycle_group"]
    for group in groups:
        group_object = Group(name=group)
        group_object.save()


def colors(self):
    file = open("tk-db/colors.csv")
    for row in file:
        Color.objects.create(name=row)


def run_database(self):
    clear_data()
    super_user()
    groups()
    colors(self)
