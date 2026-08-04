from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile

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
            username='testuser@example.com',
            email='testuser@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        UserProfile.objects.create(user=self.user, role='student')

    def test_login_successful(self):
        """Test that a user can login with valid credentials."""
        url = reverse('users:login')
        response = self.client.post(url, {
            'email': 'testuser@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], 'testuser@example.com')

    def test_login_failed_invalid_credentials(self):
        """Test that login fails with invalid credentials."""
        url = reverse('users:login')
        response = self.client.post(url, {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
