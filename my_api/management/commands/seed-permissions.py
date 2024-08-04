from django.db import transaction
from django.core.management.base import BaseCommand
from my_api.models import Permissions, Roles, Configurations, Permission_roles, User_permissions, Users
from my_api.serializers import PermissionsSerializer

def addDefaultPermissionToRole(role_name, role):
    partner_default_permissions = [
        'users_view',
        'users_view_details',
        'exercises_view_all',
        'exercises_view',
        'documents_view_all',
        'documents_view',
        'documents_update',
        'collaborations_view',
        'documents_update_status',
        'documents_update_file',
        'documents_view_partner',
        'download_document'
    ]

    collaborator_default_permissions = [
        'users_view_all',
        'users_view',
        'users_view_details',
        'exercises_view_all',
        'exercises_view',
        'documents_view_all',
        'documents_view',
        'exercice_configurations_view_all',
        'exercice_configurations_view',
        'exercice_configurations_create',
        'exercice_configurations_update',
        'collaborations_view_all',
        'collaborations_view',
        'contacts_view_all',
        'contacts_view',
        'contacts_create',
        'contacts_update',
        'documents_update_status',
        'documents_update_file',
        'documents_view_partner',
        'documents_view_manager',
        'exercise_status_distribution',
        'documents_per_periodicity',
        'contacts_per_profession',
        'collaborations_per_month',
        'user_type_distribution',
        'document_status_distribution',
        'get_statistics',
        'validate_document',
        'rejete_documents',
        'download_document'
    ]

    default_permissions = None
    if role_name == 'Partenaire':
        default_permissions = partner_default_permissions
    elif role_name == 'Collaborateur':
        default_permissions = collaborator_default_permissions

    if default_permissions is not None:
        for permission_key in default_permissions:
            permission = Permissions.objects.get(permission_key=permission_key)
            Permission_roles.objects.get_or_create(role=role, permission=permission)

    return True


class Seeder:
    @classmethod
    def seedRoles(cls):
        with transaction.atomic():
            roles_data = [
                {
                    'name': 'Admin',
                    'type': 'User',
                    'description': 'Administrator rôle',
                },
                {
                    'name': 'Collaborateur',
                    'type': 'User',
                    'description': 'Collaborateur rôle',
                },
                {
                    'name': 'Partenaire',
                    'type': 'Partner',
                    'description': 'Partenaire rôle',
                },
            ]
            for role_data in roles_data:
                role, created = Roles.objects.get_or_create(
                    name=role_data['name'],
                    defaults={'description': role_data['description'], 'type': role_data['type']}
                )
                if created:
                    print(f"Role '{role.name}' created.")

                if addDefaultPermissionToRole(role_data['name'], role):
                    print(f"Permissions par défaut des '{role_data['name']}' ajoutés.")

    @classmethod
    def seedPermissions(cls):
        with transaction.atomic():
            # Créer des permissions pour chaque modèle

            list_permissions_view_view_all_update = [
                ('Utilisateurs', 'Users'), 
                ('Exercices', 'Exercises'), 
                ('Documents', 'Documents'), 
                ('Configurations des exercices', 'Exercice_configurations'), 
                ('Logs', 'Logs'), 
                ('Rôles', 'Roles'), 
                ('Permissions', 'Permissions'), 
                ('Rôles de permission', 'Permission_roles'), 
                ('Permissions utilisateur', 'User_permissions'), 
                ('Configurations', 'Configurations'),
                ('Collaborations', 'Collaborations'),
                ('Contacts', 'Contacts')
            ]

            list_permissions_delete = [
                ('Utilisateurs', 'Users'), 
                ('Exercices', 'Exercises'), 
                ('Documents', 'Documents'), 
                ('Configurations des exercices', 'Exercice_configurations'), 
                ('Logs', 'Logs'), 
                ('Rôles', 'Roles'), 
                ('Rôles de permission', 'Permission_roles'), 
                ('Permissions utilisateur', 'User_permissions'),
                ('Collaborations', 'Collaborations'),
                ('Contacts', 'Contacts')
            ]

            others_permissions = [
                {
                    'permission_key': 'documents_update_status',
                    'permission_name': 'Modifier le status d\'un document',
                    'categorie': 'documents'
                },
                {
                    'permission_key': 'documents_active_unactive',
                    'permission_name': 'Activer/Désactiver un document',
                    'categorie': 'documents'
                },
                {
                    'permission_key': 'documents_update_file',
                    'permission_name': 'Modifier un fichier',
                    'categorie': 'documents'
                },
                {
                    'permission_key': 'exercices_update_date',
                    'permission_name': 'Modifier la date d\'un exercice',
                    'categorie': 'exercises'
                },
                {
                    'permission_key': 'documents_update_assign',
                    'permission_name': 'Assigner un document à un nouveau parténaire',
                    'categorie': 'documents'
                },
                {
                    'permission_key': 'exercices_update_open_close',
                    'permission_name': 'Ouvrir/Fermer un exercice',
                    'categorie': 'exercises'
                },
                {
                    'permission_key': 'documents_view_partner',
                    'permission_name': 'Voir les documents d\'un partenaire',
                    'categorie': 'documents'
                },
                {
                    'permission_key': 'documents_view_manager',
                    'permission_name': 'Voir les documents d\'un responsable',
                    'categorie': 'documents'
                },
                {
                    'permission_key': 'download_document',
                    'permission_name': 'Téléchager un document',
                    'categorie': 'documents'
                },
                {
                    'permission_key': 'rejete_documents',
                    'permission_name': 'Rejeter un document',
                    'categorie': 'documents'
                },
                {
                    'permission_key': 'validate_document',
                    'permission_name': 'Valider un document',
                    'categorie': 'documents'
                },
                {
                    'permission_key': 'update_document_date',
                    'permission_name': 'Modifier la date d\'écheance d\'un documnent',
                    'categorie': 'documents'
                },
                {
                    'permission_key': 'update_document_partner',
                    'permission_name': 'Modifier la date le partenaire associé à un documnent',
                    'categorie': 'documents'
                },
                {
                    'permission_key': 'users_active_unactive',
                    'permission_name': 'Activer/Désactiver un utilisateurs',
                    'categorie': 'users'
                },
                {
                    'permission_key': 'set_user_permissions',
                    'permission_name': 'Modifer les permissions d\'un utilisateur',
                    'categorie': 'permissions'
                },
                {
                    'permission_key': 'renew_exercise',
                    'permission_name': 'Reconduire un exercice sur l\'année suivante',
                    'categorie': 'exercises'
                },
                {
                    'permission_key': 'get_statistics',
                    'permission_name': 'Voir les statistiques',
                    'categorie': 'statistics'
                },
                {
                    'permission_key': 'document_status_distribution',
                    'permission_name': 'Voir la distribution des statuts des documents',
                    'categorie': 'statistics'
                },
                {
                    'permission_key': 'user_type_distribution',
                    'permission_name': 'Voir la distribution des types d\'utilisateurs',
                    'categorie': 'statistics'
                },
                {
                    'permission_key': 'collaborations_per_month',
                    'permission_name': 'Voir les collaborations par mois',
                    'categorie': 'statistics'
                },
                {
                    'permission_key': 'contacts_per_profession',
                    'permission_name': 'Voir les contacts par profession',
                    'categorie': 'statistics'
                },
                {
                    'permission_key': 'documents_per_periodicity',
                    'permission_name': 'Voir les documents par périodicité',
                    'categorie': 'statistics'
                },
                {
                    'permission_key': 'exercise_status_distribution',
                    'permission_name': 'Voir la distribution des statuts des exercices',
                    'categorie': 'statistics'
                },
                {
                    'permission_key': 'users_view_details',
                    'permission_name': 'Voir les documents, exercices et configurations d\'un utilisateur',
                    'categorie': 'users'
                },
                {
                    'permission_key': 'can_update_user_information',
                    'permission_name': 'Peut modifier les informations des utilisateurs',
                    'categorie': 'users'
                },
                {
                    'permission_key': 'can_see_all_exercice',
                    'permission_name': 'Voir tout les exercices sans exceptions',
                    'categorie': 'exercises'
                },
                {
                    'permission_key': 'can_see_all_dpcument_in_exercice',
                    'permission_name': 'Voir tout les documents présent dans un exercice sans exceptions',
                    'categorie': 'exercises'
                },
                {
                    'permission_key': 'get_report',
                    'permission_name': 'Voir les rapports',
                    'categorie': 'raports'
                },
            ]
            
            for french_name, model_name in list_permissions_view_view_all_update:
                permission_name = f'Afficher tout {french_name}'
                permission_key = f'{model_name.lower()}_view_all'
                permission, _ = Permissions.objects.update_or_create(
                    permission_key=permission_key,
                    defaults={'permission_name': permission_name, 'categorie': model_name.lower()}
                )
                print(f"Permission '{permission.permission_name}' created or update.")

                permission_name = f'Afficher {french_name}'
                permission_key = f'{model_name.lower()}_view'
                permission, _ = Permissions.objects.update_or_create(
                    permission_key=permission_key,
                    defaults={'permission_name': permission_name, 'categorie': model_name.lower()}
                )
                print(f"Permission '{permission.permission_name}'  created or update.")

                permission_name = f'Ajouter un {french_name}'
                permission_key = f'{model_name.lower()}_create'
                permission, _ = Permissions.objects.update_or_create(
                    permission_key=permission_key,
                    defaults={'permission_name': permission_name, 'categorie': model_name.lower()}
                )
                print(f"Permission '{permission.permission_name}'  created or update.")

                permission_name = f'Modifier un {french_name}'
                permission_key = f'{model_name.lower()}_update'
                permission, _ = Permissions.objects.update_or_create(
                    permission_key=permission_key,
                    defaults={'permission_name': permission_name, 'categorie': model_name.lower()}
                )
                print(f"Permission '{permission.permission_name}'  created or update.")

            for french_name, model_name in list_permissions_delete:
                permission_name = f'Supprimer un {french_name}'
                permission_key = f'{model_name.lower()}_delete'
                permission, _ = Permissions.objects.update_or_create(
                    permission_key=permission_key,
                    defaults={'permission_name': permission_name, 'categorie': model_name.lower()}
                )
                print(f"Permission '{permission.permission_name}'  created or update.")

            for permission_data in others_permissions:
                permission, _ = Permissions.objects.update_or_create(
                    permission_key=permission_data['permission_key'],
                    defaults={'permission_name': permission_data['permission_name'], 'categorie': permission_data['categorie']}
                )
                print(f"Permission '{permission.permission_name}'  created or update.")

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Role & Permissions...')
        Seeder.seedPermissions()
        Seeder.seedRoles()
        self.stdout.write(self.style.SUCCESS('Successfully seeded rôle & permissions'))
