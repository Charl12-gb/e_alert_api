from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Users(AbstractUser):
    type_choices = [
        ('User', 'User'),
        ('Partner', 'Partner'),
        ('Other', 'Other')
    ]
    type = models.CharField(max_length=20, choices=type_choices)
    is_external = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    phone = models.CharField(max_length=20, unique=True, null=True)
    logo = models.ImageField(upload_to='partners/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    role = models.ForeignKey('Roles', on_delete=models.CASCADE)
    sigle = models.CharField(max_length=100, null=True)
    token = models.CharField(max_length=255, null=True, blank=True)  # Champ pour le jeton d'actualisation actuel
    is_token_revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Exercises(models.Model):
    name = models.CharField(max_length=200)
    numero = models.CharField(max_length=25, unique=True, null=True)
    description = models.TextField(null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    year = models.IntegerField(null=True)
    is_closed = models.BooleanField(default=False)
    is_archive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Documents(models.Model):
    status_choices = [
        ('Sent', 'Sent'),
        ('Rejected', 'Rejected'),
        ('Not Sent', 'Not Sent'),
        ('Validated', 'Validated')
    ]
    periodicity_choices = [
        ('Annuel', 'Annuel'),
        ('Trimestriel', 'Trimestriel'),
        ('Semestriel', 'Semestriel'),
        ('Mensuel', 'Mensuel')
    ]
    numero = models.CharField(max_length=25, unique=True, null=True)
    name = models.CharField(max_length=100)
    deadline = models.DateField()
    send_date = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    group_number = models.CharField(max_length=255)
    periodicity = models.CharField(max_length=20, choices=periodicity_choices, default="Annuel")
    status = models.CharField(max_length=20, choices=status_choices)
    exercise = models.ForeignKey('Exercises', on_delete=models.CASCADE)
    month = models.IntegerField(null=True)
    partner = models.ForeignKey('Users', on_delete=models.CASCADE, related_name="documents_partnered", null=True)
    permalink = models.ImageField(upload_to='documents/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Contacts(models.Model):
    name = models.CharField(max_length=255, null=True)
    profession = models.CharField(max_length=255, null=True)
    email = models.EmailField(verbose_name='partner_contact_email', max_length=255)
    phone = models.CharField(max_length=20, null=True)
    partner = models.ForeignKey('Users', on_delete=models.CASCADE, related_name="partner_contact", null=True)
    created_by = models.ForeignKey('Users', on_delete=models.CASCADE, related_name="user_contact", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

class Collaborations(models.Model):
    partner = models.ForeignKey('Users', on_delete=models.CASCADE, related_name="collaborations_partnered")
    manager = models.ForeignKey('Users', on_delete=models.CASCADE, related_name="collaborations_managered")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Exercice_configurations(models.Model):
    types_choices = [
        ('Escalade', 'Escalade'),
        ('Report', 'Report'),
        ('Others', 'Others')
    ]
    moments_choices = [
        ('Before', 'Before'),
        ('After', 'After'),
    ]
    name = models.CharField(max_length=255)
    moment = models.CharField(max_length=20, choices=moments_choices, default='Before')
    niveau = models.IntegerField(null=True)
    emails = models.TextField()
    send_mail_to_partner = models.BooleanField(default=False)
    content_mail = models.TextField()
    number_day_send = models.TextField(null=True)
    type = models.CharField(max_length=20, choices=types_choices, default='Escalade')
    document = models.ForeignKey('Documents', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Logs(models.Model):
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Roles(models.Model):
    type_choices = [
        ('User', 'User'),
        ('Partner', 'Partner')
    ]
    type = models.CharField(max_length=20, choices=type_choices, default='User')
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Permissions(models.Model):
    permission_name = models.CharField(max_length=255, unique=True)
    permission_key = models.CharField(max_length=255, unique=True)
    categorie = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Permission_roles(models.Model):
    role = models.ForeignKey('Roles', on_delete=models.CASCADE)
    permission = models.ForeignKey('Permissions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class User_permissions(models.Model):
    permission = models.ForeignKey('Permissions', on_delete=models.CASCADE)
    user = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='user_permissions_set')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Configurations(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
