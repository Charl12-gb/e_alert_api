from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
# from my_api.Utils.cron import start_cron

# start_cron()

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return Response({
        'message': 'Welcome to the alert API.',
        'version': '1.0.0',
        'authors': 'Charles GBOYOU',
        'address': 'gboyoucharles22@gmail.com',
        'example': {
            'notice': '_______________________________________',
            'url': request.build_absolute_uri() + '____________'
        }
    }, status=201)
