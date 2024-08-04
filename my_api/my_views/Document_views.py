import os
from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from my_api.models import Documents, Users, Collaborations
from my_api.serializers import DocumentsSerializer, DocumentsSerializerAdd, Exercice_configurations
from my_api.permission_classes import PermissionVerify
from my_api.my_views.helpers import generateNumero, generateUniqueUuid
from django.shortcuts import get_object_or_404
from django.conf import settings
from datetime import datetime
from django.http import HttpResponse
from my_api.mail_config import MailConfig

def create_documents_for_all_partners(item, deadline, doc_status, periodicity, exercise_id, month, uniqueNumberGroupe):
    created_documents = []
    partners = Users.objects.filter(type='Partner')
    for partner in partners:
        document = create_document(item, deadline, doc_status, periodicity, exercise_id, partner, month, uniqueNumberGroupe)
        created_documents.append(document)
        send_email_to_partner(partner, document)
    return created_documents

def create_documents_for_specific_partners(item, deadline, doc_status, periodicity, exercise_id, month, uniqueNumberGroupe, partner_ids):
    created_documents = []
    if not partner_ids:
        document = create_document(item, deadline, doc_status, periodicity, exercise_id, None, month, uniqueNumberGroupe)
        created_documents.append(document)
        send_email_to_partner(None, document, partner_ids)
    else:
        partner_ids = list(set(partner_ids))  # Remove duplicates if any
        for userId in partner_ids:
            user = Users.objects.filter(id=userId, type='Partner').first()
            if user:
                document = create_document(item, deadline, doc_status, periodicity, exercise_id, user, month, uniqueNumberGroupe)
                created_documents.append(document)
                send_email_to_partner(user, document)
    return created_documents


def create_document(item, deadline, doc_status, periodicity, exercise_id, partner, month, uniqueNumberGroupe):
    document = Documents(
        name=item['name'],
        deadline=deadline,
        status=doc_status,
        periodicity=periodicity,
        exercise_id=exercise_id,
        partner=partner,
        month=month,
        group_number=uniqueNumberGroupe,
        numero=generateNumero('DOC-E'),  # Generate the document number directly
    )
    document.save()
    return document

def send_email_to_partner(partner, document, partner_ids=None):
    try:
        if partner:
            send_partner_notification_email(partner, document)
        else:
            send_partner_notification_email(None, document, partner_ids)
    except Exception as e:
        # Log the exception or handle it as necessary
        print(f"Failed to send email to partner: {e}")


def send_partner_notification_email(partner, document, partner_ids=None):

    subject = 'Notification: Nouveau document à envoyer'
    message = f'Cher partenaire,\n\nVous avez un nouveau document à envoyer: {document.name}\nDate limite: {document.deadline}\n'
    
    if partner:
        recipient_list = [partner.email]
    elif partner_ids:
        # Si vous avez plusieurs partenaires à notifier, utilisez la liste des e-mails ici
        recipient_list = [Users.objects.filter(id=userId).first().email for userId in partner_ids]
    else:
        recipient_list = []
    MailConfig.sendDocumentEmail(recipient_list, subject, message)

def send_partner_notification_email_status(partner, document, old_status, new_status):
    subject = f'Notification: Document {new_status}'
    message = f'Cher partenaire,\n\nLe statut de votre document "{document.name}" a été changé de "{old_status}" à "{new_status}".\n'
    
    if new_status == 'Rejected':
        message += f'Votre document a été rejeté. Veuillez le corriger et le renvoyer.'
    elif new_status == 'Validated':
        message += f'Félicitations ! Votre document a été validé avec succès.'
    MailConfig.sendDocumentEmail([partner.email], subject, message)

class Document_view:
    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def download_document(request, document_id):
        if not PermissionVerify.has_permission(request, 'download_document'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        document = get_object_or_404(Documents, id=document_id)
        if document.permalink:
            file_path = document.permalink.name
            absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(absolute_path):
                with open(absolute_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(absolute_path)
                    return response
            else:
                return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def getListDocForManagerPartner(request, manager_id):
        try:
            manager = Users.objects.get(id=manager_id)
        except Users.DoesNotExist:
            return Response({'message': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)

        if manager.role.name == "Admin":
            if not PermissionVerify.has_permission(request, 'documents_view_all'):
                return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

            all_documents = Documents.objects.all()
            serializer = DocumentsSerializer(all_documents, many=True)
        else:
            if not PermissionVerify.has_permission(request, 'documents_view'):
                return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

            partner_ids = Collaborations.objects.filter(manager_id=manager_id).values_list('partner_id', flat=True)
            partner_documents = Documents.objects.filter(partner_id__in=partner_ids)
            serializer = DocumentsSerializer(partner_documents, many=True)
        
        for document in serializer.data:
            if document.get('permalink'):
                file_url = request.build_absolute_uri(document['permalink'])
                document['file_url'] = file_url

        return Response(serializer.data, status=status.HTTP_200_OK)

    @api_view(['POST'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def addDocument(request):
        if not PermissionVerify.has_permission(request, 'documents_create'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        created_documents = []

        for item in data:
            uniqueNumberGroupe = generateUniqueUuid()
            sub_docs = item.get('sub_period', [])
            exercise_id = item.get('exercise', None)
            periodicity = item.get('periodicity', 'Annuel')
            doc_status = item.get('status', 'Not Sent')

            for sub_doc in sub_docs:
                deadline = sub_doc.get('deadline', None)
                date_object = datetime.strptime(deadline, "%Y-%m-%d")
                month = date_object.month

                all_emails = sub_doc.get('all', False)
                partner_ids = sub_doc.get('partner', [])

                if all_emails:
                    created_documents.extend(create_documents_for_all_partners(item, deadline, doc_status, periodicity, exercise_id, month, uniqueNumberGroupe))
                else:
                    created_documents.extend(create_documents_for_specific_partners(item, deadline, doc_status, periodicity, exercise_id, month, uniqueNumberGroupe, partner_ids))
                                
        # Return the serialized data of the created documents
        serializer = DocumentsSerializer(created_documents, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def updateDocument(request, document_id):
        if not PermissionVerify.has_permission(request, 'documents_update'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            document = Documents.objects.get(id=document_id)
        except Documents.DoesNotExist:
            return Response({'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)


        serializer = DocumentsSerializerAdd(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def document(request, document_id):
        if not PermissionVerify.has_permission(request, 'documents_view'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            document = Documents.objects.get(id=document_id)
        except Documents.DoesNotExist:
            return Response({'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        # Construire l'URL absolue pour voir le document
        document_url = request.build_absolute_uri(document.permalink.url)

        # Ajouter l'URL au serializer
        serializer = DocumentsSerializer(document)
        serialized_data = serializer.data
        serialized_data['document_url'] = document_url

        return Response(serialized_data)

    @api_view(['DELETE'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def deleteDocument(request, document_id):
        if not PermissionVerify.has_permission(request, 'documents_delete'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            document = Documents.objects.get(id=document_id)
        except Documents.DoesNotExist:
            return Response({'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            ex_config = Exercice_configurations.objects.get(document=document)
            ex_config.delete()
        except Exercice_configurations.DoesNotExist:
            pass 

        document.delete()
        return Response({'message': 'Document and related Exercice_configuration deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def setDocumentStatus(request, document_id):
        try:
            document = Documents.objects.get(id=document_id)
        except Documents.DoesNotExist:
            return Response({'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')

        if new_status == 'Rejected':
            if not PermissionVerify.has_permission(request, 'rejete_documents'):
                return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif new_status == 'Validated':
            if not PermissionVerify.has_permission(request, 'validate_document'):
                return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        old_status = document.status

        serializer = DocumentsSerializerAdd(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Envoyer un e-mail au partenaire
            send_partner_notification_email_status(document.partner, document, old_status, new_status)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def activeOrUnactiveDocument(request, document_id):
        if not PermissionVerify.has_permission(request, 'documents_active_unactive'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            document = Documents.objects.get(id=document_id)
        except Documents.DoesNotExist:
            return Response({'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)


        document.is_active = not document.is_active
        document.save()
        return Response({'message': 'Document status updated successfully'}, status=status.HTTP_200_OK)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def getPartnerDocuments(request, partner_id):
        if not PermissionVerify.has_permission(request, 'documents_view_partner'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            documents = Documents.objects.filter(partner_id=partner_id)
            serializer = DocumentsSerializer(documents, many=True)

            for document in serializer.data:
                if document.get('permalink'):
                    file_url = request.build_absolute_uri(document['permalink'])
                    document['file_url'] = file_url

            return Response(serializer.data)
        except Documents.DoesNotExist:
            return Response({'message': 'Documents not found'}, status=status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def assignDocumentToPartner(request):
        if not PermissionVerify.has_permission(request, 'documents_update_assign'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        document_id = request.data.get('document_id')
        partner_id = request.data.get('partner_id')

        try:
            document = Documents.objects.get(id=document_id)
        except Documents.DoesNotExist:
            return Response({'message': 'Document non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        try:
            partner = Users.objects.get(id=partner_id)
        except Users.DoesNotExist:
            return Response({'message': 'Partenaire non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        docGroup = Documents.objects.filter(partner=partner.id, group_number=document.group_number).first()
        if docGroup:
            return Response({'message': 'Ce partenaire a déjà été ajouté à ce document'}, status=status.HTTP_400_BAD_REQUEST)

        document.partner = partner
        document.save()
        return Response({'message': 'Document assigné au partenaire avec succès.'}, status=status.HTTP_200_OK)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def updateDocumentFile(request, document_id):
        if not PermissionVerify.has_permission(request, 'documents_update_file'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            document = Documents.objects.get(id=document_id)
        except Documents.DoesNotExist:
            return Response({'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        # Supprimer le fichier existant s'il en existe un
        if document.permalink:
            # Supprimer le fichier physique
            if os.path.exists(document.permalink.path):
                os.remove(document.permalink.path)
            # Supprimer l'URL du fichier dans le modèle
            document.permalink.delete(save=False)

        if 'document' in request.FILES:
            file = request.FILES['document']
            fs = FileSystemStorage(location='/e_alert/storage/documents/')
            filename = fs.save(file.name, file)
            document.permalink = '/e_alert/storage/documents/' + fs.url(filename)
            document.status = 'Sent'
            document.send_date = datetime.now().date()
            document.save()

            partner_id = document.partner.id if document.partner else None
            try:
                collaboration = Collaborations.objects.get(partner_id=partner_id)
                manager_email = collaboration.manager.email
            except Collaborations.DoesNotExist:
                manager_email = None

            if not manager_email:
                admin_user = Users.objects.filter(groups__name='Admin').first()
                if admin_user:
                    manager_email = admin_user.email

            if manager_email:
                subject = 'Document Envoyé pour Validation'
                message = f'Le document {document.name} de l\'exercice {document.exercise.name} a été envoyé pour validation. Veuillez le vérifier et le valider.'
                recipient_list = [manager_email]
                MailConfig.sendDocumentEmail(recipient_list, subject, message)

            return Response({'message': 'Document file updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No document file found'}, status=status.HTTP_400_BAD_REQUEST)