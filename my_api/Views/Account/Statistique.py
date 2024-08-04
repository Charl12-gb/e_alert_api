from django.db.models import Count, Q, F
from datetime import datetime
from rest_framework import status
from django.db.models.functions import ExtractMonth
import calendar
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from my_api.models import Exercises, Documents, Users, Collaborations, Exercice_configurations, Contacts
from my_api.Utils.serializers import DocumentsSerializer, UsersSerializer
from my_api.Utils.permission_classes import PermissionVerify

# Exemple de vue pour la répartition des exercices par statut
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def exerciseStatusDistribution(request):
    if not PermissionVerify.has_permission(request, 'exercise_status_distribution'):
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    # Récupérer les paramètres de requête pour la période de date, l'année et l'exercice
    start_date = datetime.strptime(request.query_params['startDate'], "%d-%m-%Y").date()
    end_date = datetime.strptime(request.query_params['endDate'], "%d-%m-%Y").date()
    exercise_id = request.query_params.get('exercise_id', None)

    exercises = Exercises.objects.filter(created_at__range=(start_date, end_date))
    if exercise_id:
        exercises = exercises.filter(id=exercise_id)

    exercise_status_count = exercises.values('is_closed').annotate(count=Count('id'))
    
    labels = ['Fermé', 'Ouvert']
    values = [0, 0]
    
    for item in exercise_status_count:
        if item['is_closed']:
            values[0] = item['count']
        else:
            values[1] = item['count']
    
    data = {
        'labels': labels,
        'values': values
    }
    
    return Response(data)

# Exemple de vue pour le nombre total de documents par périodicité
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def documentsPerPeriodicity(request):
    if not PermissionVerify.has_permission(request, 'documents_per_periodicity'):
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    # Récupérer les paramètres de requête pour la période de date, l'année et l'exercice
    start_date = datetime.strptime(request.query_params['startDate'], "%d-%m-%Y").date()
    end_date = datetime.strptime(request.query_params['endDate'], "%d-%m-%Y").date()
    exercise_id = request.query_params.get('exercise_id', None)

    documents = Documents.objects.filter(created_at__range=(start_date, end_date))
    if exercise_id:
        documents = documents.filter(exercise_id=exercise_id)

    all_periodicities = ['Annuel', 'Trimestriel', 'Semestriel', 'Mensuel']
    documents_per_periodicity = documents.values('periodicity').annotate(count=Count('id'))
    
    labels = all_periodicities
    values = [0, 0, 0, 0] 
    
    for item in documents_per_periodicity:
        periodicity = item['periodicity']
        index = all_periodicities.index(periodicity)
        values[index] = item['count']
    
    data = {
        'labels': labels,
        'values': values
    }
    
    return Response(data)

# Exemple de vue pour le nombre total de collaborations par mois de création
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def collaborationsPerMonth(request):
    if not PermissionVerify.has_permission(request, 'collaborations_per_month'):
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    start_date = datetime.strptime(request.query_params['startDate'], "%d-%m-%Y").date()
    end_date = datetime.strptime(request.query_params['endDate'], "%d-%m-%Y").date()

    collaborations = Collaborations.objects.filter(created_at__range=(start_date, end_date))

    collaborations_per_month = collaborations.annotate(
        month_created=ExtractMonth('created_at')
    ).values('month_created').annotate(count=Count('id'))

    labels = [calendar.month_name[i] for i in range(1, 13)] 
    values = [0] * 12

    for item in collaborations_per_month:
        month = item['month_created']
        values[month - 1] = item['count'] 

    data = {
        'labels': labels,
        'values': values
    }

    return Response(data)

# Exemple de vue pour la répartition des documents par statut
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def documentStatusDistribution(request):
    if not PermissionVerify.has_permission(request, 'document_status_distribution'):
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    start_date = datetime.strptime(request.query_params['startDate'], "%d-%m-%Y").date()
    end_date = datetime.strptime(request.query_params['endDate'], "%d-%m-%Y").date()
    exercise_id = request.query_params.get('exercise_id', None)

    documents = Documents.objects.filter(created_at__range=(start_date, end_date))
    if exercise_id:
        documents = documents.filter(exercise_id=exercise_id)

    status_choices = ['Sent', 'Rejected', 'Not Sent', 'Validated'] 
    document_status_count = documents.values('status').annotate(count=Count('id'))
    labels = status_choices  
    values = [0] * len(status_choices)
    
    for item in document_status_count:
        status_index = status_choices.index(item['status'])
        values[status_index] = item['count']
    
    data = {
        'labels': labels,
        'values': values
    }
    
    return Response(data)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getStatistics(request):
    if not PermissionVerify.has_permission(request, 'get_statistics'):
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    # Récupérer les paramètres de requête pour la période de date, l'année et l'exercice
    start_date = datetime.strptime(request.query_params['startDate'], "%d-%m-%Y").date()
    end_date = datetime.strptime(request.query_params['endDate'], "%d-%m-%Y").date()
    exercise_id = request.query_params.get('exercise_id', None)

    documents = Documents.objects.filter(created_at__range=(start_date, end_date))
    exercises = Exercises.objects.filter(created_at__range=(start_date, end_date))
    contacts = Contacts.objects.filter(created_at__range=(start_date, end_date))
    collaborations = Collaborations.objects.filter(created_at__range=(start_date, end_date))
    configurations = Exercice_configurations.objects.filter(created_at__range=(start_date, end_date))

    if exercise_id:
        documents = documents.filter(exercise_id=exercise_id)
        exercises = exercises.filter(id=exercise_id)

    total_documents = documents.count()
    total_exercises = exercises.count()
    total_collaborations = collaborations.count()
    total_documents_sent = documents.filter(status='Sent').count()
    total_documents_not_sent = documents.filter(status='Not Sent').count()
    total_documents_validated = documents.filter(status='Validated').count()
    total_documents_rejected = documents.filter(status='Rejected').count()
    total_contacts = contacts.count()
    total_configurations = configurations.count()

    data = {
        'total_documents': total_documents,
        'total_exercises': total_exercises,
        'total_collaborations': total_collaborations,
        'total_documents_sent': total_documents_sent,
        'total_documents_not_sent': total_documents_not_sent,
        'total_documents_validated': total_documents_validated,
        'total_documents_rejected': total_documents_rejected,
        'total_contacts': total_contacts,
        'total_configurations': total_configurations,
    }
    
    return Response(data)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getReports(request):
    if not PermissionVerify.has_permission(request, 'get_report'):
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    # Récupérer les paramètres de requête
    start_date = datetime.strptime(request.query_params['startDate'], "%d-%m-%Y").date()
    end_date = datetime.strptime(request.query_params['endDate'], "%d-%m-%Y").date()
    exercise_id = request.query_params.get('exercise_id', None)
    user_partner = request.query_params.get('user_partner', None)
    user_collaborateur = request.query_params.get('user_collaborateur', None)

    documents = Documents.objects.filter(created_at__range=(start_date, end_date))
    if exercise_id:
        documents = documents.filter(exercise_id=exercise_id)
    if user_partner:
        documents = documents.filter(partner_id=user_partner)
    if user_collaborateur:
        collaborations = Collaborations.objects.filter(manager_id=user_collaborateur)
        documents = documents.filter(partner__in=collaborations.values('partner'))

    on_time_documents = documents.filter(status='Validated', deadline__gte=F('send_date'))
    late_documents = documents.filter(status='Sent', deadline__lt=F('send_date'))
    not_sent_documents = documents.filter(Q(status='Rejected') | Q(status='Not Sent'))

    # Sérialisez les objets avec les serializers appropriés
    on_time_documents_data = DocumentsSerializer(on_time_documents, many=True).data
    late_documents_data = DocumentsSerializer(late_documents, many=True).data
    not_sent_documents_data = DocumentsSerializer(not_sent_documents, many=True).data

    on_time_partners = Users.objects.filter(id__in=on_time_documents.values_list('partner', flat=True))
    late_partners = Users.objects.filter(id__in=late_documents.values_list('partner', flat=True))
    not_sent_partners = Users.objects.filter(id__in=not_sent_documents.values_list('partner', flat=True))

    # Sérialisez les objets avec les serializers appropriés pour les partenaires
    on_time_partners_data = UsersSerializer(on_time_partners, many=True).data
    not_sent_partners_data = UsersSerializer(not_sent_partners, many=True).data
    late_partners_data = UsersSerializer(late_partners, many=True).data

    # Construisez la structure du rapport souhaitée avec les données appropriées
    report = [
        
    ]

    # Liste de tous les partenaires
    all_partners = list(set(list(on_time_partners) + list(late_partners) + list(not_sent_partners)))

    for partner in all_partners:
        partner_data = UsersSerializer(partner).data

        partner_documents_on_time = [doc for doc in on_time_documents_data if doc['partner'] == partner_data]
        partner_documents_late = [doc for doc in late_documents_data if doc['partner'] == partner_data]
        partner_documents_not_sent = [doc for doc in not_sent_documents_data if doc['partner'] == partner_data]

        partner_info = {
            'partenaire': partner_data,
            'document_send_a_late': partner_documents_late,
            'document_send_on_time': partner_documents_on_time,
            'document_not_send': partner_documents_not_sent,
        }

        report.append(partner_info)

    return Response(report)