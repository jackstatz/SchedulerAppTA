from django.test import TestCase, Client
from django.urls import reverse
# If you need redirect for assertions:
# from django.shortcuts import redirect

# Import your models using the full path from the app
from ScheduleAppData.models import User
# Use the alias if you are also testing the Courses model in this file
from ScheduleAppData.models import Courses as CoursesModel

class AdminLoginTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = '/'

        # test admin user
        if User:
            self.admin_email = 'supervisor@uwm.edu'
            self.admin_password = 'password'
            self.admin_user = User.objects.create(
                Email=self.admin_email,
                Password=self.admin_password,
                Role='Supervisor'
            )
    def test_valid_admin_login(self):

        # Perform the login POST
        initial_response = self.client.post(self.login_url, {'email': self.admin_email,'password': self.admin_password,})

        #Assert the redirect is correct
        self.assertEqual(initial_response.status_code, 302)
        self.assertEqual(initial_response['Location'], '/adminDashboard/')
        final_response = self.client.get('/adminDashboard/', follow=True)
        self.assertEqual(final_response.status_code, 200)

    def test_invalid_password_admin_login(self):
        response = self.client.post(self.login_url, {'email': self.admin_email,'password': 'wrongpassword',})
        self.assertEqual(response.status_code, 200) # Should return, showing the login page
        self.assertTemplateUsed(response, 'LoginPage.html')

    def test_no_password_admin_login(self):
        response = self.client.post(self.login_url, { 'email': self.admin_email, 'password': '',})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'LoginPage.html')

    def test_empty(self):
        response = self.client.post('/', {"username": "", "password": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'LoginPage.html')

    def test_wrong_username(self):
        response = self.client.post('/', {"username": "wrong", "password": "password"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'LoginPage.html')

    def test_wrong_password(self):
        response = self.client.post('/', {"username": self.admin_email, "password": "Super wrong!!!"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'LoginPage.html')