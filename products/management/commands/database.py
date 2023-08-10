from typing import Any

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates instances for database tables from csv files from old database"

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("Creating database...")
        run_database()
        self.stdout.write("Done.")


def run_database():
    pass
