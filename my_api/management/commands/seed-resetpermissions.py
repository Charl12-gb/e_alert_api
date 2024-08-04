from django.db import transaction
from django.core.management.base import BaseCommand
from my_api.models import Permissions, Roles, Configurations, Permission_roles, User_permissions, Users
from my_api.serializers import PermissionsSerializer

class Seeder:
    @classmethod
    def seedResetPermissions(cls):
        with transaction.atomic():
            all_users = Users.objects.all()
            for user in all_users:
                role = user.role
                role_permissions = Permission_roles.objects.filter(role=role)
                for permission_role in role_permissions:
                    permission = permission_role.permission
                    User_permissions.objects.get_or_create(
                        user=user,
                        permission=permission
                    )
            

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Reset Permissions...')
        Seeder.seedResetPermissions()
        self.stdout.write(self.style.SUCCESS('Successfully seeded Reset permissions'))
