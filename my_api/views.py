import django
from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from ldap3 import Server, Connection, SIMPLE, SUBTREE
from rest_framework.decorators import api_view, permission_classes
from my_api.Utils.serializers import UsersSerializer
from django.contrib.auth.hashers import make_password
from jwt import encode
from my_api.models import Users, Roles, Permission_roles, User_permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from django.contrib.auth import logout
import logging

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


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

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UsersSerializer

    def get_local_user(self, email_or_phone):
        """Tente de récupérer un utilisateur local par email ou téléphone."""
        try:
            return Users.objects.get(Q(email=email_or_phone) | Q(phone=email_or_phone))
        except Users.DoesNotExist:
            return None

    def ldap_authentication(self, email, password):
        """Tente l'authentification LDAP et récupère l'utilisateur correspondant dans la base locale."""
        server = Server('ldap://10.200.1.59:389')
        conn = Connection(server, user=email, password=password, authentication=SIMPLE)

        if not conn.bind():
            return None
        else:
            conn.search('OU=DGPED,OU=FINANCE,DC=FINANCES,DC=BJ', '(mail={})'.format(email), SUBTREE, attributes=['*'])
            if len(conn.entries) == 1:
                user = conn.entries[0]
                local_user = self.get_local_user(email)
                if not local_user:
                    is_active = True
                    role, created = Roles.objects.get_or_create(name='Collaborateur', defaults={'description': 'Collaborateur rôle'})
                    password = make_password(password+email)
                    new_user = Users.objects.create(
                        email=email, 
                        username=email,
                        password=password, 
                        is_external=True, 
                        role=role, 
                        name=user.name, 
                        is_active=is_active
                    )
                    role_permissions = Permission_roles.objects.filter(role=role)
                    for permission_role in role_permissions:
                        permission = permission_role.permission
                        User_permissions.objects.create(
                            user=new_user,
                            permission=permission
                        )
                    return new_user
                else:
                    return local_user
            else:
                # Aucun utilisateur trouvé avec cet e-mail dans LDAP
                # logger.error("Multiple users found with email: {}".format(email))
                return None

    def post(self, request):
        email_or_phone = request.data.get('email_or_phone')
        password = request.data.get('password')

        if not email_or_phone:
            return Response({'message': 'Please provide an email or phone number.'}, status=status.HTTP_400_BAD_REQUEST)

        user = self.get_local_user(email_or_phone)
        if user and not user.check_password(password):
            user = None

        if not user:
            user = self.ldap_authentication(email_or_phone, password)

        if not user:
            return Response({'message': 'Incorrect email/phone or password!'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({'message': 'Inactive user account. Please contact the administrator if you think this is an error.'}, status=status.HTTP_400_BAD_REQUEST)

        return self.generate_response(user)

    def generate_response(self, user):
        """Génère la réponse de succès avec les tokens et les données de l'utilisateur."""
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Welcome! Successfully connected.',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': self.serializer_class(user).data
        }, status=status.HTTP_200_OK)  
            
class LogoutView(GenericAPIView):

    def post(self, request):
        logout(request)
        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)

class TokenRefreshView(GenericAPIView):
    serializer_class = UsersSerializer

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                user = Users.objects.get(id=refresh.payload['user_id'])
                new_refresh = refresh.access_token
                response = {
                    'message': 'Token rafraîchi avec succès',
                    'refresh': str(new_refresh),
                    'access': str(refresh),
                    'user': self.serializer_class(user).data
                }
                return Response(response, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message': 'Token invalide ou expiré'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'message': 'Le jeton de rafraîchissement n\'a pas été fourni'}, status=status.HTTP_400_BAD_REQUEST)