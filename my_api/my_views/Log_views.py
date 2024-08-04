from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from ..serializers import LogsSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import Logs

class Log_view:
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def createLog(request, user_id, action):
        if not PermissionVerify.has_permission(request, 'logs_create'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        log = Logs(user_id=user_id, action=action)
        log.save()

        serializer = LogsSerializer(log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def retrieveLog(request, log_id):
        if not PermissionVerify.has_permission(request, 'logs_view'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            log = Logs.objects.get(id=log_id)
        except Logs.DoesNotExist:
            return Response({'message': 'Log not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LogsSerializer(log)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def updateLog(request, log_id, action):
        if not PermissionVerify.has_permission(request, 'logs_update'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            log = Logs.objects.get(id=log_id)
        except Logs.DoesNotExist:
            return Response({'message': 'Log not found'}, status=status.HTTP_404_NOT_FOUND)

        log.action = action
        log.save()

        serializer = LogsSerializer(log)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def deleteLog(request, log_id):
        if not PermissionVerify.has_permission(request, 'logs_delete'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            log = Logs.objects.get(id=log_id)
        except Logs.DoesNotExist:
            return Response({'message': 'Log not found'}, status=status.HTTP_404_NOT_FOUND)

        log.delete()
        return Response({'message': 'Log deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def listLogs(request):
        if not PermissionVerify.has_permission(request, 'logs_view_all'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        logs = Logs.objects.all()
        serializer = LogsSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
