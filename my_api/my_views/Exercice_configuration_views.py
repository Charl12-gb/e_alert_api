from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from ..models import Exercice_configurations, Documents
from ..serializers import ExerciceConfigurationsSerializer
from ..permission_classes import PermissionVerify

class Exercice_configuration_view:
    @api_view(['POST'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def createOrUpdateDocumentConfiguration(request):
        if not PermissionVerify.has_permission(request, 'exercice_configurations_create'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        configurations = request.data
        response_data = []

        for configuration_data in configurations:
            config_id = configuration_data.get('id')

            if config_id is None:
                document_id = configuration_data.get('document')
                document = Documents.objects.get(id=document_id)
                apply_all = configuration_data.get('apply_all', False)
                if apply_all and document.periodicity != 'Annuel':
                    group_number = document.group_number

                    related_documents = Documents.objects.filter(group_number=group_number)
                    configuration_data['emails'] = ','.join(map(str, configuration_data['emails']))
                    configuration_data['number_day_send'] = ','.join(map(str, configuration_data['number_day_send']))
                    for related_document in related_documents:
                        configuration_data['document'] = related_document.id
                        # Convertir la liste d'e-mails en chaîne de caractères avant la sérialisation
                        serializer = ExerciceConfigurationsSerializer(data=configuration_data)
                        if serializer.is_valid():
                            config = serializer.save()
                            response_data.append(serializer.data)
                        else:
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Convertir la liste d'e-mails en chaîne de caractères avant la sérialisation
                    configuration_data['emails'] = ','.join(map(str, configuration_data['emails']))
                    configuration_data['number_day_send'] = ','.join(map(str, configuration_data['number_day_send']))
                    serializer = ExerciceConfigurationsSerializer(data=configuration_data)
                    if serializer.is_valid():
                        config = serializer.save()
                        response_data.append(serializer.data)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    config = Exercice_configurations.objects.get(id=config_id)
                except Exercice_configurations.DoesNotExist:
                    return Response({'message': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)

                configuration_data['emails'] = ','.join(map(str, configuration_data['emails']))
                configuration_data['number_day_send'] = ','.join(map(str, configuration_data['number_day_send']))
                serializer = ExerciceConfigurationsSerializer(instance=config, data=configuration_data)
                if serializer.is_valid():
                    config = serializer.save()
                    response_data.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(response_data, status=status.HTTP_201_CREATED)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def retrieveConfigurationByDocuments(request, document_id):
        if not PermissionVerify.has_permission(request, 'exercice_configurations_view'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            document = Documents.objects.get(id=document_id)
            configurations = Exercice_configurations.objects.filter(document=document)
            
            response_data = []
            for configuration in configurations:
                configuration_data = ExerciceConfigurationsSerializer(configuration).data
                # Désérialiser la liste d'e-mails en tant que liste de chaînes de caractères
                serialized_emails = configuration_data.get('emails', [])
                serialized_number_day_sends = configuration_data.get('number_day_send', [])
                configuration_data['emails'] = serialized_emails.split(',') if serialized_emails else []
                configuration_data['number_day_send'] = serialized_number_day_sends.split(',') if serialized_number_day_sends else []
                response_data.append(configuration_data)
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Documents.DoesNotExist:
            return Response({'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exercice_configurations.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)


    @api_view(['DELETE'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def deleteDocumentConfiguration(request, configuration_id):
        if not PermissionVerify.has_permission(request, 'exercice_configurations_delete'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            configuration = Exercice_configurations.objects.get(id=configuration_id)
            configuration.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exercice_configurations.DoesNotExist:
            return Response({'message': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def listDocumentConfigurations(request):
        if not PermissionVerify.has_permission(request, 'exercice_configurations_view_all'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        configurations = Exercice_configurations.objects.all()
        serializer = ExerciceConfigurationsSerializer(configurations, many=True)
        response_data = serializer.data
        
        # Désérialiser la liste d'e-mails pour chaque configuration en tant que liste de chaînes de caractères
        for data in response_data:
            serialized_emails = data.get('email', '')
            data['emails'] = serialized_emails.split(',') if serialized_emails else []
            serialized_number_day_sends = data.get('number_day_send', '')
            data['number_day_send'] = serialized_number_day_sends.split(',') if serialized_number_day_sends else []
        
        return Response(response_data, status=status.HTTP_200_OK)