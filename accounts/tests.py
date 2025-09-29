from django.test import TestCase

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class SignupTests(APITestCase):
    def test_signup_ok(self):
        url = "/auth/signup"
        data = {"email": "t1@example.com", "password": "Test12345", "role": "job_seeker"}
        r = self.client.post(url, data, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", r.data)

    def test_signup_duplicate_email(self):
        User.objects.create_user(username="t2@example.com", email="t2@example.com", password="Xx12345678")
        url = "/auth/signup"
        data = {"email": "T2@example.com", "password": "Test12345", "role": "job_seeker"}  # שימי לב לאותיות גדולות
        r = self.client.post(url, data, format="json")
        self.assertEqual(r.status_code, status.HTTP_409_CONFLICT)

    def test_signup_bad_email(self):
        url = "/auth/signup"
        data = {"email": "not-an-email", "password": "Test12345", "role": "job_seeker"}
        r = self.client.post(url, data, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_short_password(self):
        url = "/auth/signup"
        data = {"email": "t3@example.com", "password": "123", "role": "job_seeker"}
        r = self.client.post(url, data, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

