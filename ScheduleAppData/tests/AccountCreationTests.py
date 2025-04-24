from django.test import TestCase, Client
from django.urls import reverse
from ScheduleAppData.models import Courses as Courses
from ScheduleAppData.models import User

class AccountCreationTest(TestCase):
    def setUp(self):
        # Set up valid data for account creation
        self.valid_data = {
            "action": "create_account",
            "firstName": "John",
            "lastName": "Doe",
            "role": "Instructor",
            "email": "johndoe@example.com",
            "password": "securepassword",
            "phone": "1234567890"
        }
        self.invalid_data = {
            "action": "create_account",
            "firstName": "John",
            "lastName": "Doe",
            "role": "Instructor",
            "email": "",
            "password": "securepassword",
            "phone": "1234567890"
        }

    def test_valid_account_creation(self):
        response = self.client.post(reverse('adminDashboard'), self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(Email="johndoe@example.com").exists())
    def test_invalid_account_creation(self):
        response = self.client.post(reverse('adminDashboard'), self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(Email="").exists())