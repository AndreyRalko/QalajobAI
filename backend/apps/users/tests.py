from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile
from apps.users.services.preset_users import load_preset_users

User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user(self):
        """Test creating a normal user with username, email and password."""
        user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='password123'
        )
        UserProfile.objects.create(user=user, role='student')
        self.assertEqual(user.email, 'normal@example.com')
        self.assertTrue(user.check_password('password123'))
        self.assertEqual(len(user.password), 32)
        self.assertEqual(user.profile.role, 'student')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='password123'
        )
        UserProfile.objects.create(user=admin_user, role='admin')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.profile.role, 'admin')


class AuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='Тестов_Пользователь',
            password='password123',
            first_name='Пользователь',
            last_name='Тестов',
        )
        UserProfile.objects.create(user=self.user, role='student')

    def test_login_successful(self):
        url = reverse('users:login')
        response = self.client.post(url, {
            'login': 'Тестов_Пользователь',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertEqual(response.data['data']['user']['login'], 'Тестов_Пользователь')

    def test_login_failed_invalid_credentials(self):
        url = reverse('users:login')
        response = self.client.post(url, {
            'login': 'Тестов_Пользователь',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_removed(self):
        response = self.client.post('/api/v1/auth/register/', {
            'email': 'new@example.com',
            'password': 'Password1',
            'name': 'New User',
            'role': 'student',
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_preset_student_login(self):
        load_preset_users()
        url = reverse('users:login')
        response = self.client.post(url, {
            'login': 'Иванов_Иван',
            'password': 'Student123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['user']['role'], 'student')
        self.assertEqual(response.data['data']['user']['login'], 'Иванов_Иван')
        self.assertEqual(response.data['data']['user']['student_id'], '48958')
