from django.db import transaction
from django.core.management.base import BaseCommand
from my_api.models import Permissions, Roles, Configurations, Permission_roles, User_permissions, Users
from my_api.serializers import PermissionsSerializer

class Seeder:
    @classmethod
    def appSeed(cls):
        data = [
            {'key': 'app_name', 'value': 'DGPED E-ALERT', 'type': 'text'},
            {'key': 'app_slogan', 'value': 'Gestionnaire des alerts', 'type': 'text'},
            {'key': 'logo', 'value': 'path/to/logo.png', 'type': 'image'},
            {'key': 'email_addresses', 'value': 'email1,email2,email3', 'type': 'serialized'},
        ]

        with transaction.atomic():
            for item in data:
                key = item['key']
                value = item['value']
                config_type = item['type']

                config, created = Configurations.objects.get_or_create(key=key)

                config.value = value
                config.type = config_type
                config.save()

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding App Config...')
        Seeder.appSeed()
        self.stdout.write(self.style.SUCCESS('Successfully seeded the App Config'))
