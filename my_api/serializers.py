from rest_framework import serializers
from .models import Users, Exercises, Documents, Exercice_configurations, Logs, Roles, Permissions, Permission_roles, User_permissions, Configurations, Collaborations, Contacts


class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'

class UsersSerializerAdd(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }


class UsersSerializer(serializers.ModelSerializer):
    role = RolesSerializer()
    class Meta:
        model = Users
        fields = (
            'id',
            'type',
            'is_external',
            'name',
            'email',
            'phone',
            'is_active',
            'role',
            'sigle',
            'logo'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'name': {'required': True},
            'phone': {'required': True},
            'role': {'required': True}
        }

class ExercisesSerializerAdd(serializers.ModelSerializer):
    class Meta:
        model = Exercises
        fields = '__all__'

class DocumentsSerializerAdd(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = '__all__'

class CollaborationsSerializerAdd(serializers.ModelSerializer):
    class Meta:
        model = Collaborations
        fields = '__all__'

class CollaborationsSerializer(serializers.ModelSerializer):
    partner = UsersSerializer(read_only=True)
    manager = UsersSerializer(read_only=True)
    class Meta:
        model = Collaborations
        fields = '__all__'

class ContactsSerializer(serializers.ModelSerializer):
    partner = UsersSerializer(read_only=True)
    class Meta:
        model = Contacts
        fields = '__all__'

class ContactsSerializerAdd(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        fields = '__all__'

class DocumentsSerializer(serializers.ModelSerializer):
    exercise = ExercisesSerializerAdd(read_only=True)
    partner = UsersSerializer(read_only=True)
    manager = UsersSerializer(read_only=True)

    class Meta:
        model = Documents
        fields = '__all__'

class ExercisesSerializer(serializers.ModelSerializer):
    documents = DocumentsSerializer(many=True, read_only=True)

    class Meta:
        model = Exercises
        fields = '__all__'

class ExerciceConfigurationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercice_configurations
        fields = '__all__'

class LogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = '__all__'

class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permissions
        fields = '__all__'

class PermissionRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission_roles
        fields = '__all__'

class UserPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_permissions
        fields = '__all__'

class ConfigurationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configurations
        fields = '__all__'

class PartnerDocumentsSerializer(serializers.Serializer):
    user = UsersSerializer()  # Utiliser le serializer approprié pour l'utilisateur
    service = serializers.ListField(child=serializers.CharField())  # Liste des services

    class Meta:
        fields = ['user', 'service']