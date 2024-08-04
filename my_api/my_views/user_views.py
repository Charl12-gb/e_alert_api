from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from ..serializers import UsersSerializer, RolesSerializer, UsersSerializer, CollaborationsSerializer, UsersSerializerAdd
from ..models import Users, Roles, Permissions, Permission_roles, User_permissions, Collaborations
from rest_framework.permissions import AllowAny
from ..permission_classes import PermissionVerify
from django.core.files.storage import FileSystemStorage
from django.db.models import Count
from django.db import transaction
from ..mail_config import MailConfig
from django.shortcuts import get_object_or_404
import string
import random

def attachPermissionsToAdminRole(role_id, permission_ids):
        """
        Attach des permissions à un rôle
        """
        role = Roles.objects.filter(id=role_id).first()
        if not role:
            return Response({'message': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        for permission_id in permission_ids:
            permission = Permissions.objects.filter(id=permission_id).first()
            if permission:
                Permission_roles.objects.get_or_create(role=role, permission=permission)
        return True

def generate_password():
    """
    Générer un nouveau mot de passe aléatoire
    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(8))

class User_view:

    @api_view(['POST'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def register(request):
        if not PermissionVerify.has_permission(request, 'users_create'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        new_password = generate_password()
        hashed_password = make_password(new_password)
        data['username'] = data.get('email')

        serializer = UsersSerializerAdd(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save(password=hashed_password, username=request.data.get('email'), is_active=True)

        role = user.role
        role_permissions = Permission_roles.objects.filter(role=role)
        for permission_role in role_permissions:
            permission = permission_role.permission
            User_permissions.objects.create(
                user=user,
                permission=permission
            )

        dataUser = Users.objects.get(id=user.id)
        userSerializer = UsersSerializerAdd(dataUser)

        MailConfig.sendResetPasswordEmail(user.email, new_password, user)

        return Response({'message': "Success", 'user': userSerializer.data}, status=status.HTTP_201_CREATED)


    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def getUserPartnerActiveAndFree(request):
        # Récupérer les utilisateurs actifs dont le type est 'Partner' et n'ont pas de collaborateurs dans Collaborations
        users_active = Users.objects.filter(is_active=True, type='Partner').exclude(id__in=Collaborations.objects.values_list('partner_id', flat=True))
        
        # Serializer les utilisateurs pour les renvoyer en réponse
        serializer = UsersSerializer(users_active, many=True)
        return Response(serializer.data)
    
    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def users(request):
        if not PermissionVerify.has_permission(request, 'users_view_all'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        users = Users.objects.all()
        serializer = UsersSerializer(users, many=True)
        return Response(serializer.data)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def usersByType(request, user_type):
        if not PermissionVerify.has_permission(request, 'users_view_all'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        if user_type == 'all':
            users = Users.objects.values('type').annotate(count=Count('id'))
            users_by_type = {}
            for user in users:
                user_type = user['type']
                user_count = user['count']
                user_list = Users.objects.filter(type=user_type)
                serializer = UsersSerializer(user_list, many=True)
                users_by_type[user_type] = serializer.data
            
            return Response(users_by_type)

        users = Users.objects.filter(type=user_type)
        serializer = UsersSerializer(users, many=True)
        return Response(serializer.data)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def user(request, user_id):
        if not PermissionVerify.has_permission(request, 'users_view'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UsersSerializer(user)
        return Response(serializer.data)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def update(request, user_id):
        if not PermissionVerify.has_permission(request, 'users_update'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UsersSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            if 'logo' in request.FILES:
                logo_file = request.FILES['logo']
                fs = FileSystemStorage(location='/e_alert/storage/images/')
                logo_filename = fs.save(logo_file.name, logo_file)
                logo_path = '/e_alert/storage/images/' + fs.url(logo_filename)
                serializer.validated_data['logo'] = logo_path
            
            updated_user = serializer.save()

            # Clear existing permissions and add permissions based on updated role
            updated_user.user_permissions.clear()
            role = updated_user.role
            permissions = Permission_roles.objects.filter(role=role).values_list('permission', flat=True)
            updated_user.user_permissions.add(*permissions)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def delete(request, user_id):
        if not PermissionVerify.has_permission(request, 'users_delete'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user.delete()
        return Response({'message': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def updatePassword(request, id):
        user = Users.objects.get(id=id)
        # Vérifier que l'utilisateur existe
        if not user:
            return Response({'message': 'Cet utilisateur n\'existe pas'}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier que l'ancien mot de passe est correct
        old_password = request.data.get('password')
        if not check_password(old_password, user.password):
            return Response({'message': 'Le mot de passe actuel est incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        # Mettre à jour le mot de passe
        new_password = request.data.get('new_password')
        user.password = make_password(new_password)
        user.save()
        
        return Response({'message': 'Mot de passe mis à jour avec succès'}, status=status.HTTP_200_OK) 

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def resetPassword(request):
        """
        Réinitialiser le mot de passe d'un utilisateur
        """
        email = request.data.get('email')
        try:
            user = Users.objects.get(email=email)
            new_password = generate_password()
            user.password = make_password(new_password)  # hacher le nouveau mot de passe
            user.save()
            # Envoyer un email contenant le nouveau mot de passe à l'utilisateur
            MailConfig.sendResetPasswordEmail(user.email, new_password, user)
            return Response({'message': 'Un email contenant le nouveau mot de passe a été envoyé à l\'adresse email associée à ce compte'}, status=200)
        except ObjectDoesNotExist:
            return Response({'message': 'Utilisateur non trouvé'}, status=404)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def activeOrInactiveUser(request, user_id):
        if not PermissionVerify.has_permission(request, 'users_active_unactive'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user.is_active = not user.is_active
        user.save()
        return Response({'message': 'User updated'}, status=status.HTTP_200_OK)
    
    @api_view(['POST'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def addRole(request):
        """
        Ajouter un nouveau rôle
        """
        if not PermissionVerify.has_permission(request, 'roles_create'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = RolesSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            if role.name == "Admin":
                permissions = Permissions.objects.all()
                permission_ids = [permission.id for permission in permissions]
                attachPermissionsToAdminRole(role.id, permission_ids)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def roles(request):
        """
        Récupérer la liste de tous les rôles
        """
        if not PermissionVerify.has_permission(request, 'roles_view_all'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        roles = Roles.objects.all()
        serializer = RolesSerializer(roles, many=True)
        return Response(serializer.data)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def role(request, role_id):
        """
        Récupérer les détails d'un rôle spécifique
        """
        if not PermissionVerify.has_permission(request, 'roles_view'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            role = Roles.objects.get(id=role_id)
        except Roles.DoesNotExist:
            return Response({'message': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RolesSerializer(role)
        return Response(serializer.data)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def updateRole(request, role_id):
        """
        Mettre à jour les détails d'un rôle
        """
        if not PermissionVerify.has_permission(request, 'roles_update'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            role = Roles.objects.get(id=role_id)
        except Roles.DoesNotExist:
            return Response({'message': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RolesSerializer(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def deleteRole(request, role_id):
        """
        Supprimer un rôle
        """
        if not PermissionVerify.has_permission(request, 'roles_delete'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            role = Roles.objects.get(id=role_id)
        except Roles.DoesNotExist:
            return Response({'message': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def attachPermissionsToRole(request, role_id):
        """
        Attach des permissions à un rôle
        """
        if not PermissionVerify.has_permission(request, 'permission_roles_create'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        role = Roles.objects.filter(id=role_id).first()
        if not role:
            return Response({'message': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        permissions = request.data.get('permissions', [])

        for permission_id in permissions:
            permission = Permissions.objects.filter(id=permission_id).first()
            if permission:
                Permission_roles.objects.get_or_create(role=role, permission=permission)

                # Récupérer tous les utilisateurs ayant le rôle spécifié
                users = Users.objects.filter(role=role)
                for user in users:
                    # Vérifier si l'utilisateur a déjà la permission, sinon l'ajouter
                    user_permission = User_permissions.objects.filter(user=user, permission=permission).first()
                    if not user_permission:
                        User_permissions.objects.create(user=user, permission=permission)

        return Response({'message': 'Permissions attached to role successfully'}, status=status.HTTP_200_OK)
    
    @api_view(['DELETE'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def removePermissionsToRole(request, role_id):
        """
        Détache des permissions d'un rôle
        """
        if not PermissionVerify.has_permission(request, 'permission_roles_delete'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        role = Roles.objects.filter(id=role_id).first()
        if not role:
            return Response({'message': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        permissions = request.data.get('permissions', [])

        for permission_id in permissions:
            permission = Permissions.objects.filter(id=permission_id).first()
            if permission:
                # Supprimer la relation entre le rôle et la permission
                Permission_roles.objects.filter(role=role, permission=permission).delete()

                # Récupérer tous les utilisateurs ayant le rôle spécifié
                users = Users.objects.filter(role=role)
                for user in users:
                    # Supprimer la permission de l'utilisateur s'il la possède
                    User_permissions.objects.filter(user=user, permission=permission).delete()

        return Response({'message': 'Permissions removed from role successfully'}, status=status.HTTP_200_OK)

    @api_view(['POST'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def attachRole(request, user_id, role_id):
        """
        Attache un rôle à un utilisateur
        """
        if not PermissionVerify.has_permission(request, 'users_create'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        user = Users.objects.filter(id=user_id).first()
        role = Roles.objects.filter(id=role_id).first()

        if not user:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if not role:
            return Response({'message': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        # Récupérer les permissions associées au rôle
        permissions = Permission_roles.objects.filter(role=role).values_list('permission', flat=True)

        # Ajouter les permissions à l'utilisateur
        for permission_id in permissions:
            permission = Permissions.objects.filter(id=permission_id).first()
            if permission:
                user_permission = User_permissions.objects.get_or_create(user=user, permission=permission) 

        user.role = role
        user.save()
        return Response({'message': 'Role attached to user successfully'}, status=status.HTTP_200_OK)

    @api_view(['DELETE'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def removeRole(request, user_id, role_id):
        """
        Détache un rôle d'un utilisateur
        """
        user = Users.objects.filter(id=user_id).first()
        role = Roles.objects.filter(id=role_id).first()

        if not user:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if not role:
            return Response({'message': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        # Récupérer les ids des permissions_roles associés au rôle
        permission_role_ids = Permission_roles.objects.filter(role=role).values_list('id', flat=True)

        # Supprimer toutes les permissions utilisateur associées à ces permissions_roles
        user_permissions = User_permissions.objects.filter(user=user, permission__permission_roles__in=permission_role_ids)
        user_permissions.delete()

        # Supprimer le rôle pour l'utilisateur
        user.role = None
        user.save()

        return Response({'message': 'Role removed from user successfully'}, status=status.HTTP_200_OK)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def addSpecificPermissionToUser(request, user_id, permission_id):
        """
        Ajouter une permission spécifique à un utilisateur
        """
        if not PermissionVerify.has_permission(request, 'set_user_permissions'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            permission = Permissions.objects.get(id=permission_id)
        except Permissions.DoesNotExist:
            return Response({'message': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier si l'utilisateur a déjà la permission
        if User_permissions.objects.filter(user=user, permission=permission).exists():
            return Response({'message': 'Permission already granted to user'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ajouter la permission à l'utilisateur
        user_permission = User_permissions(user=user, permission=permission)
        user_permission.save()        
        return Response({'message': 'Permission granted to user'}, status=status.HTTP_200_OK)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def removeSpecificPermissionToUser(request, user_id, permission_id):
        """
        Supprimer une permission spécifique à un utilisateur
        """
        if not PermissionVerify.has_permission(request, 'set_user_permissions'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            permission = Permissions.objects.get(id=permission_id)
        except Permissions.DoesNotExist:
            return Response({'message': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            user_permission = User_permissions.objects.get(user=user, permission=permission)
            user_permission.delete()
            return Response({'message': 'Permission successfully removed from the user'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'message': 'Permission is not assigned to the user'}, status=status.HTTP_404_NOT_FOUND)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def getUserPermissions(request, user_id):
        # Récupérer l'utilisateur en fonction de son ID
        user = get_object_or_404(Users, id=user_id)

        # Récupérer toutes les permissions
        permissions = Permissions.objects.all()

        # Créer un dictionnaire pour stocker les permissions groupées par catégorie avec la valeur booléenne pour chaque permission
        permissions_data = {}

        for permission in permissions:
            # Vérifier si l'utilisateur a la permission associée à son rôle
            has_permission = User_permissions.objects.filter(user=user, permission=permission).exists()

            # Vérifier si la catégorie existe déjà dans le dictionnaire, sinon l'ajouter avec une liste vide
            if permission.categorie not in permissions_data:
                permissions_data[permission.categorie] = []

            # Ajouter la permission avec la valeur booléenne au dictionnaire de catégorie
            permissions_data[permission.categorie].append({
                'id': permission.id,
                'permission_name': permission.permission_name,
                'permission_key': permission.permission_key,
                'has_permission': has_permission
            })

        return Response(permissions_data, status=status.HTTP_200_OK)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def getRolePermissions(request, role_id):
        # Récupérer le rôle en fonction de son ID
        role = get_object_or_404(Roles, id=role_id)

        # Récupérer toutes les permissions
        permissions = Permissions.objects.all()

        # Créer un dictionnaire pour stocker les permissions groupées par catégorie avec les détails et l'indicateur has_permission
        permissions_data = {}

        for permission in permissions:
            # Vérifier si le rôle a la permission associée
            has_permission = Permission_roles.objects.filter(role=role, permission=permission).exists()

            # Vérifier si la catégorie existe déjà dans le dictionnaire, sinon l'ajouter avec une liste vide
            if permission.categorie not in permissions_data:
                permissions_data[permission.categorie] = []

            # Ajouter les détails de la permission avec l'indicateur has_permission au dictionnaire de catégorie
            permissions_data[permission.categorie].append({
                'id': permission.id,
                'permission_name': permission.permission_name,
                'permission_key': permission.permission_key,
                'has_permission': has_permission
            })

        return Response(permissions_data, status=status.HTTP_200_OK)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def getCurrentUser(request):
        user = request.user 
        serializer = UsersSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def getPermissions(request):
        user = request.user
        if user:
            # Récupérer l'utilisateur en fonction de son ID
            user = get_object_or_404(Users, id=user.id)

            # Récupérer toutes les permissions
            permissions = Permissions.objects.all()

            # Créer une liste pour stocker les permissions avec leur has_permission
            permissions_data = []

            for permission in permissions:
                # Vérifier si l'utilisateur a la permission associée à son rôle
                has_permission = User_permissions.objects.filter(user=user, permission=permission).exists()

                permissions_data.append({
                    'id': permission.id,
                    'permission_name': permission.permission_name,
                    'permission_key': permission.permission_key,
                    'has_permission': has_permission
                })

            return Response(permissions_data, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_200_OK)