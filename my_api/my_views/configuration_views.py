from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from ..models import Configurations
from ..serializers import ConfigurationsSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

class Configuration_view:

    @api_view(['PUT'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def updateConfigurations(request, config_id, value):
        if not PermissionVerify.has_permission(request, 'configurations_update'):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            config = Configurations.objects.get(id=config_id)
        except Configurations.DoesNotExist:
            return Response({'message': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)

        config.value = value

        # Handle special types
        if config.type == 'image':
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                fs = FileSystemStorage(location='/e_alert/storage/images/')
                image_filename = fs.save(image_file.name, image_file)
                image_path = '/e_alert/storage/images/' + fs.url(image_filename)
                config.value = image_path

        elif config.type == 'serialize':
            # Convert value to text
            config.value = ','.join(value)

        config.save()

        serializer = ConfigurationsSerializer(config)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @api_view(['GET'])
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    @transaction.atomic
    def configuration(request, config_id):
        try:
            config = Configurations.objects.get(id=config_id)
        except Configurations.DoesNotExist:
            return Response({'message': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConfigurationsSerializer(config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @api_view(['GET'])
    def configurations(request):
        configs = Configurations.objects.all()
        serialized_data = ConfigurationsSerializer(configs, many=True).data
        
        transformed_data = {}
        for config in serialized_data:
            if config["type"] == "serialized":
                config["value"] = config["value"].split(",")  # Convertit la valeur en tableau en utilisant "," comme séparateur
            transformed_data[config["key"]] = config["value"]
        
        return Response(transformed_data, status=status.HTTP_200_OK)
