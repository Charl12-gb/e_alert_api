from django.db import transaction
from django.core.management.base import BaseCommand
from my_api.models import Permissions, Roles, Configurations, Permission_roles, User_permissions, Users
from my_api.serializers import PermissionsSerializer

class Seeder:
    @classmethod
    def seedSuperAdmin(cls):
        # Vérifier si le rôle "Admin" existe déjà ou le créer s'il n'existe pas
        admin_role, created = Roles.objects.get_or_create(
            name='Admin',
            defaults={
                'description': 'Administrator role'
            }
        )
        all_permissions = Permissions.objects.all()
        for permission in all_permissions:
            Permission_roles.objects.get_or_create(role=admin_role, permission=permission)

        # Créer un nouvel utilisateur avec le rôle "Admin"
        with transaction.atomic():
            admin_user, created = Users.objects.get_or_create(
                role=admin_role,
                defaults={
                    'email': 'admin@e-alert.it-servicegroup.com',
                    'type': 'User',
                    'is_external': False,
                    'name': 'DGPED-E Admin',
                    'phone': '1234567890',
                    'is_active': True,
                    'role': admin_role
                }
            )

            if created:
                admin_user.set_password("password")
                admin_user.save()

            # Accorder toutes les permissions à l'utilisateur
            for permission in all_permissions:
                User_permissions.objects.get_or_create(user=admin_user, permission=permission)
            print (f"Welcome \nName: {admin_user.name} \nEmail : {admin_user.email} \nPassword: password")

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Super Admin...')
        Seeder.seedSuperAdmin()
        self.stdout.write(self.style.SUCCESS('Successfully seeded the Super Admin'))
