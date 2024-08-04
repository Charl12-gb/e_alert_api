from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from my_api.models import Exercises, Documents, Users, Collaborations, Exercice_configurations
from my_api.Utils.serializers import ExercisesSerializer, ExercisesSerializerAdd, DocumentsSerializer, UsersSerializer, CollaborationsSerializer, PartnerDocumentsSerializer
from my_api.Utils.permission_classes import PermissionVerify
from django.db import transaction
from my_api.Utils.helpers import generateNumero
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from datetime import date
import datetime


class Exercice_view:
    @api_view(['POST'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def addExercice(request):
        if not PermissionVerify.has_permission(request, 'exercises_create'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        year = request.data.get('year')
        start_date = date(year, 1, 1)  # Premier jour de l'année
        end_date = date(year, 12, 31)  # Dernier jour de l'année

        request.data['start_date'] = start_date
        request.data['end_date'] = end_date

        serializer = ExercisesSerializerAdd(data=request.data)
        if serializer.is_valid():
            exercice = serializer.save()
            exercice.numero = generateNumero()
            exercice.save()  
            return Response({'message': 'Exercise added successfully', 'exercice': serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def listPartnerAndExerciceWhereDocumentNotSent(request, manager_id, period):
        if not PermissionVerify.has_permission(request, 'exercises_view_all'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            if manager_id == 'all':
                partners = Users.objects.filter(type='Partner', exercises_partnered__documents__status='Not Sent')
            else:
                manager = Users.objects.get(id=manager_id)
                partners = Users.objects.filter(type='Partner', exercises_managed__manager=manager, exercises_managed__documents__status='Not Sent')
                
            if period.isdigit():
                # Filtrage par mois
                partners = partners.filter(exercises_partnered__documents__deadline__month=int(period))
            else:
                # Filtrage par intervalle de dates
                try:
                    start_date, end_date = period.split(',')
                    start_date = datetime.strptime(start_date.strip(), '%d/%m/%Y').date()
                    end_date = datetime.strptime(end_date.strip(), '%d/%m/%Y').date()
                    partners = partners.filter(exercises_partnered__documents__deadline__range=[start_date, end_date])
                except ValueError:
                    return Response({'message': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

            # Récupération du service lié au document pour chaque partenaire
            partner_data = []
            for partner in partners:
                documents = Documents.objects.filter(partner=partner, status='Not Sent')
                service = [document.type for document in documents]
                partner_data.append({'user': partner, 'service': service})

            # Sérialisation des données
            serializer = PartnerDocumentsSerializer(partner_data, many=True)

            return Response(serializer.data)
        except Users.DoesNotExist:
            return Response({'message': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def updateExercice(request, exercice_id):
        if not PermissionVerify.has_permission(request, 'exercises_update'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            exercice = Exercises.objects.get(id=exercice_id)
        except Exercises.DoesNotExist:
            return Response({'message': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExercisesSerializerAdd(exercice, data=request.data, partial=True)
        if serializer.is_valid():
            exercice = serializer.save()
            return Response({'message': 'Exercise updated successfully', 'exercice': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def exercice(request, exercice_id):
        if not PermissionVerify.has_permission(request, 'exercises_view'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            exercice = Exercises.objects.get(id=exercice_id)
        except Exercises.DoesNotExist:
            return Response({'message': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)

        exercice_serializer = ExercisesSerializer(exercice)

        if request.user.type == 'User':
            if request.user.role.name == 'Admin' or PermissionVerify.has_permission(request, 'can_see_all_document_in_exercice'):
                documents = Documents.objects.filter(exercise=exercice)
            else:
                partner_ids = Collaborations.objects.filter(manager=request.user).values_list('partner_id', flat=True)
                documents = Documents.objects.filter(exercise=exercice, partner_id__in=partner_ids)
        elif request.user.type == 'Partner':
            documents = Documents.objects.filter(exercise=exercice, partner=request.user)
        
        year_param = request.query_params.get('year')
        if year_param:
            documents = documents.filter(exercise__year=year_param)
        
        partner_ids = documents.values_list('partner_id', flat=True)
        partners = Users.objects.filter(id__in=partner_ids)
        managers = Users.objects.filter(collaborations_partnered__partner_id__in=partner_ids)
        users = partners.union(managers)

        documents_serializer = DocumentsSerializer(documents, many=True)
        users_serializer = UsersSerializer(users, many=True)

        response_data = {
            'exercice': exercice_serializer.data,
            'documents': documents_serializer.data,
            'users': users_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def exercices(request):
        if not PermissionVerify.has_permission(request, 'exercises_view_all'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        exercices = Exercises.objects.all()
        serializer = ExercisesSerializer(exercices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @api_view(['DELETE'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def deleteExercice(request, exercice_id):
        if not PermissionVerify.has_permission(request, 'exercises_delete'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            exercice = Exercises.objects.get(id=exercice_id)
        except Exercises.DoesNotExist:
            return Response({'message': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)

        exercice.delete()
        return Response({'message': 'Exercise deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def openOrCloseExercice(request, exercice_id):
        if not PermissionVerify.has_permission(request, 'exercices_update_open_close'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            exercice = Exercises.objects.get(id=exercice_id)
        except Exercises.DoesNotExist:
            return Response({'message': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)

        exercice.is_closed = not exercice.is_closed
        exercice.save()
        return Response({'message': 'Exercise opened successfully'}, status=status.HTTP_200_OK)

    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def getDetailData(request, user_id):
        if request.user and request.user.id != user_id:
            if not PermissionVerify.has_permission(request, 'users_view_details'):
                return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(Users, id=user_id)

        exercises_set = set()
        documents_list = []
        num_documents_status = []
        manage = {}
        exerciceFilter = Q()
        docFilter = Q()
        year_param = request.query_params.get('year')
        if year_param:
            exerciceFilter &= Q(year=year_param)
            docFilter &= Q(exercise__year=year_param)

        if user.role.name == "Admin":
            documents_list = Documents.objects.filter(docFilter)
            exercises_set = Exercises.objects.filter(exerciceFilter)
            collaborations = Collaborations.objects.filter(manager=user)

            num_documents_status = Documents.objects.all().values('status').annotate(count=Count('status'))
        else:
            if user.type == 'User':
                collaborations = Collaborations.objects.filter(manager=user)

                for collab in collaborations:
                    docFilter &= Q(partner=collab.partner)
                    exerciceFilter &= Q(documents__in=partner_documents)

                    partner_documents = Documents.objects.filter(docFilter)
                    partner_exercises = Exercises.objects.filter(exerciceFilter).distinct()
                    exercises_set.update(partner_exercises)
                    documents_list.extend(partner_documents)

                num_documents_status = Documents.objects.filter(
                    Q(partner__in=[collab.partner for collab in collaborations])
                ).values('status').annotate(count=Count('status'))

            elif user.type == 'Partner':
                docFilter &= Q(partner=user)
                exerciceFilter &= Q(documents__in=documents_list)
                documents_list = Documents.objects.filter(docFilter)
                exercises_set = Exercises.objects.filter(exerciceFilter).distinct()

                managerDetail = Collaborations.objects.get(partner=user.id)
                manage = CollaborationsSerializer(managerDetail)
                if manage is not None:
                    manage = manage.data

                num_documents_status = Documents.objects.filter(
                    Q(partner=user)
                ).values('status').annotate(count=Count('status'))

        num_exercises = len(exercises_set) 
        num_documents = len(documents_list)
        num_exercises_closed = sum(1 for exer in exercises_set if exer.is_closed)
        num_exercises_open = sum(1 for exer in exercises_set if not exer.is_closed)
        partners_list = []
        num_collaborators = 0
        if user.type == 'User':
            partners_list = [collab.partner for collab in collaborations]
            num_collaborators = len(partners_list)

        exercises_serializer = ExercisesSerializer(exercises_set, many=True)
        documents_serializer = DocumentsSerializer(documents_list, many=True)
        user_serializer = UsersSerializer(user)
        patner_lists_serializer = UsersSerializer(partners_list, many=True)

        data = {
            'user': user_serializer.data,
            'num_exercises': num_exercises,
            'num_documents': num_documents,
            'num_exercises_closed': num_exercises_closed,
            'num_exercises_open': num_exercises_open,
            'num_documents_status': num_documents_status,
            'partners_list': patner_lists_serializer.data,
            'num_collaborators': num_collaborators,
            'exercises': exercises_serializer.data,
            'documents': documents_serializer.data,
            'manage': manage
        }
        return Response(data, status=status.HTTP_200_OK)


    @api_view(['POST'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def setExerciceDate(request, exercice_id):
        if not PermissionVerify.has_permission(request, 'exercices_update_date'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            exercice = Exercises.objects.get(id=exercice_id)
        except Exercises.DoesNotExist:
            return Response({'message': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)

        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        if start_date is None or end_date is None:
            return Response({'message': 'Invalid start_date or end_date'}, status=status.HTTP_400_BAD_REQUEST)

        exercice.start_date = start_date
        exercice.end_date = end_date
        exercice.save()

        return Response({'message': 'Exercise dates set successfully'}, status=status.HTTP_200_OK)

    @api_view(['POST'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def renewForYear(request):
        if not PermissionVerify.has_permission(request, 'renew_exercise'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        exercise_id = request.data.get('exercise_id')
        with_document = request.data.get('with_document', False)
        with_configuration = request.data.get('with_configuration', False)
        
        try:
            exercise = Exercises.objects.get(id=exercise_id)
        except Exercises.DoesNotExist:
            return Response({'message': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_year = exercise.year + 1
        
        # Check if an exercise with the same name already exists for the new year
        if Exercises.objects.filter(name=exercise.name, year=new_year).exists():
            return Response({'message': f"An exercise with the same name already exists for the year {new_year}"}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Create a new exercise with the incremented year
            new_exercise = Exercises.objects.create(
                name=exercise.name,
                numero=generateNumero(),
                description=exercise.description,
                start_date=date(new_year, 1, 1),  # Premier jour de l'année
                end_date=date(new_year, 12, 31),  # Dernier jour de l'année
                year=new_year,
                is_closed=False,
                is_archive=False,
            )
            
            if with_document:
                # Copy documents associated with the old exercise to the new exercise
                documents = exercise.documents_set.all()
                for document in documents:
                    new_document = Documents.objects.create(
                        name=document.name,
                        deadline=document.deadline.replace(year=new_year),
                        is_active=document.is_active,
                        group_number=document.group_number,
                        periodicity=document.periodicity,
                        status="Not Sent",
                        exercise=new_exercise,
                        partner=document.partner,
                        numero=generateNumero('DOC-E')
                    )
                    
                    if with_configuration:
                        configurations = document.exercice_configurations_set.all()
                        for configuration in configurations:
                            Exercice_configurations.objects.create(
                                name=configuration.name,
                                moment=configuration.moment,
                                niveau=configuration.niveau,
                                emails=configuration.emails,
                                content_mail=configuration.content_mail,
                                number_day_send=configuration.number_day_send,
                                type=configuration.type,
                                document=new_document,
                            )
            
        return Response({'message': 'Exercise renewed successfully'}, status=status.HTTP_200_OK)