from django.test import TestCase

# Create your tests here.

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase


class AdminLoginTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username="testadmin",
            email="admin@example.com",
            password="TestPassword123!",
            is_staff=True,
        )

    def test_staff_user_can_login_to_admin(self):
        url = reverse("admin-login")

        response = self.client.post(
            url,
            {
                "username": "testadmin",
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertTrue(response.data["is_staff"])
