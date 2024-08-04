from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from my_api.models import Contacts
from my_api.Utils.serializers import ContactsSerializer, ContactsSerializerAdd
from my_api.Utils.permission_classes import PermissionVerify

class Contact_view:
    @api_view(['POST'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def addContact(request):
        if not PermissionVerify.has_permission(request, 'contacts_create'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        contact_data = request.data
        serializer = ContactsSerializerAdd(data=contact_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def contact(request, contact_id):
        if not PermissionVerify.has_permission(request, 'contacts_view'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            contact = Contacts.objects.get(id=contact_id)
            serializer = ContactsSerializer(contact)
            return Response(serializer.data)
        except Contacts.DoesNotExist:
            return Response({'message': 'Contact not found'}, status=404)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def contacts(request):
        if not PermissionVerify.has_permission(request, 'contacts_view_all'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        contacts = Contacts.objects.all()
        serializer = ContactsSerializer(contacts, many=True)
        return Response(serializer.data)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def activeContacts(request):
        if not PermissionVerify.has_permission(request, 'contacts_view_all'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        contacts = Contacts.objects.filter(is_active=True)
        serializer = ContactsSerializer(contacts, many=True)
        return Response(serializer.data)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def activeOrInactiveContact(request, contact_id):
        if not PermissionVerify.has_permission(request, 'contacts_update'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            contact = Contacts.objects.get(id=contact_id)
        except Contacts.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        contact.is_active = not contact.is_active
        contact.save()
        return Response({'message': 'Contact updated'}, status=status.HTTP_200_OK)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def updateContact(request, contact_id):
        if not PermissionVerify.has_permission(request, 'contacts_update'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            contact = Contacts.objects.get(id=contact_id)
            serializer = ContactsSerializerAdd(instance=contact, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Contacts.DoesNotExist:
            return Response({'message': 'Contact not found'}, status=404)

    @api_view(['POST'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def addOrUpdateContact(request):
        if not PermissionVerify.has_permission(request, 'contacts_update'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
        contact_data = request.data
        contact_id = contact_data.get('id')
        if contact_id:
            contact = Contacts.objects.get(id=contact_id)
            serializer = ContactsSerializerAdd(instance=contact, data=contact_data, partial=True)
        else:
            serializer = ContactsSerializerAdd(data=contact_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    