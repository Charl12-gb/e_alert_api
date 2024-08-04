from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from my_api.models import Documents, Collaborations
from my_api.Utils.serializers import DocumentsSerializer, CollaborationsSerializer, CollaborationsSerializerAdd
from my_api.Utils.permission_classes import PermissionVerify

class Collaboration_view:
    @api_view(['POST'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def associatePartnerToManager(request):
        if not PermissionVerify.has_permission(request, 'collaborations_create'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CollaborationsSerializerAdd(data=request.data, many=True)
        if serializer.is_valid():
            collaborations_data = serializer.validated_data
            created_collaborations = []

            for data in collaborations_data:
                partner = data['partner']
                manager = data['manager']

                with transaction.atomic():
                    # Remove the existing collaboration if partner was associated with a manager
                    existing_collaboration = Collaborations.objects.filter(partner=partner)
                    if existing_collaboration.exists():
                        existing_collaboration.delete()

                    # Create a new collaboration
                    collaboration, created = Collaborations.objects.get_or_create(partner=partner, manager=manager)

                    if created:
                        created_collaborations.append(collaboration)

            # Serialize the created collaborations and return the response
            serializer = CollaborationsSerializer(created_collaborations, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @api_view(['DELETE'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def removeManagerPartner(request, collaboration_id):
        if not PermissionVerify.has_permission(request, 'collaborations_delete'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            collaboration = Collaborations.objects.get(id=collaboration_id)
            collaboration.delete()
            return Response({'message': 'Collaboration removed successfully'}, status=status.HTTP_200_OK)
        except Collaborations.DoesNotExist:
            return Response({'message': 'Collaboration not found'}, status=status.HTTP_404_NOT_FOUND)


    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def managerPartnerLists(request, manager_id):
        if not PermissionVerify.has_permission(request, 'collaborations_view'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        if manager_id == 'all':
            collaborations = Collaborations.objects.all()
        else:
            collaborations = Collaborations.objects.filter(manager_id=manager_id)

        serializer = CollaborationsSerializer(collaborations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def getManagerPartnerDocuments(request, manager_id, partner_id):
        if not PermissionVerify.has_permission(request, 'documents_view'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        documents = Documents.objects.filter(exercise__manager_id=manager_id, partner_id=partner_id)
        serializer = DocumentsSerializer(documents, many=True)
        
        for document in serializer.data:
            if document.get('permalink'):
                file_url = request.build_absolute_uri(document['permalink'])
                document['file_url'] = file_url

        return Response(serializer.data, status=status.HTTP_200_OK)


    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def getPartnerDocuments(request, partner_id):
        if not PermissionVerify.has_permission(request, 'documents_view'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        documents = Documents.objects.filter(partner_id=partner_id)
        serializer = DocumentsSerializer(documents, many=True)
        for document in serializer.data:
            if document.get('permalink'):
                file_url = request.build_absolute_uri(document['permalink'])
                document['file_url'] = file_url

        return Response(serializer.data, status=status.HTTP_200_OK)


    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def getManagerPartnerDocumentsByService(request, manager_id, partner_id, service_id):
        if not PermissionVerify.has_permission(request, 'documents_view'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        documents = Documents.objects.filter(exercise__manager_id=manager_id, partner_id=partner_id, service_id=service_id)
        serializer = DocumentsSerializer(documents, many=True)
        for document in serializer.data:
            if document.get('permalink'):
                file_url = request.build_absolute_uri(document['permalink'])
                document['file_url'] = file_url

        return Response(serializer.data, status=status.HTTP_200_OK)


    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def getPartnerDocumentsByService(request, partner_id, service_id):
        if not PermissionVerify.has_permission(request, 'documents_view'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        documents = Documents.objects.filter(partner_id=partner_id, service_id=service_id)
        serializer = DocumentsSerializer(documents, many=True)
        for document in serializer.data:
            if document.get('permalink'):
                file_url = request.build_absolute_uri(document['permalink'])
                document['file_url'] = file_url
                
        return Response(serializer.data, status=status.HTTP_200_OK)
