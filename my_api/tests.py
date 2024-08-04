from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Roles

class RoleAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.role = Roles.objects.create(name='Admin', description='Administrator role')

    def test_get_roles(self):
        response = self.client.get(reverse('roles'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.role.name)

    def test_get_role(self):
        url = reverse('role', kwargs={'role_id': self.role.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.role.name)
        self.assertEqual(response.data['description'], self.role.description)

    def test_create_role(self):
        data = {'name': 'Editor', 'description': 'Editor role'}
        response = self.client.post(reverse('add_role'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Roles.objects.count(), 2)
        self.assertEqual(Roles.objects.latest('created_at').name, 'Editor')

    def test_update_role(self):
        url = reverse('update_role', kwargs={'role_id': self.role.id})
        data = {'name': 'SuperAdmin', 'description': 'Super admin role'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.role.refresh_from_db()
        self.assertEqual(self.role.name, 'SuperAdmin')
        self.assertEqual(self.role.description, 'Super admin role')

    def test_delete_role(self):
        url = reverse('delete_role', kwargs={'role_id': self.role.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Roles.objects.filter(id=self.role.id).exists())
