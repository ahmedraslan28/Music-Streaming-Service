from django.core.management.base import BaseCommand
from api.models import User, Artist


class Command(BaseCommand):
    help = 'Populates the database with collections and products'

    def handle(self, *args, **options):
        pass
