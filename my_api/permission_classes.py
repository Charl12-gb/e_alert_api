from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Permissions, User_permissions
from rest_framework import exceptions

def extract_user_id_from_token(request):
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(' ')[1]
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(auth_token)
            return validated_token['user_id']
        else:
            raise exceptions.AuthenticationFailed('Authorization header missing')
    except Exception as e:
        raise exceptions.AuthenticationFailed('Invalid token')
    
class PermissionVerify:
    def has_permission(request, permission_key):
        user_id = extract_user_id_from_token(request)
        try:
            user_permissions = User_permissions.objects.filter(user_id=user_id, permission__permission_key=permission_key)
            if user_permissions.exists():
                return True
        except User_permissions.DoesNotExist:
            pass
        return False