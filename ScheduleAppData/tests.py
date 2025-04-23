from django.test import override_settings
from django.test import TestCase, Client
from django.urls import reverse
from ScheduleAppData.models import Courses as CoursesModel # Rename to avoid conflict with Courses view
from ScheduleAppData.models import User
from django.urls import resolve
from django.urls import Resolver404
# Create your tests here.

from django.test import TestCase
from .models import Courses  # Assuming the class is in course_module.py

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
        self.assertEqual(initial_response['Location'], '/adminDashboard')
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

class TestCourses(TestCase):

    def test_valid_course(self):
        # Arrange
        name = "Introduction to AI"
        semester = "Fall"
        year = 2025

        # Act
        course = Courses(name, semester, year)

        # Assert
        self.assertEqual(course.CourseName, name)
        self.assertEqual(course.Semester, semester)
        self.assertEqual(course.Year, year)

    def test_invalid_name_empty(self):
        # Arrange
        name = ""
        semester = "Fall"
        year = 2025

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            Courses(name, semester, year)
        self.assertEqual(str(context.exception), "Name must be a non-empty string.")

    def test_invalid_name_non_string(self):
        # Arrange
        name = 12345  # Non-string name
        semester = "Fall"
        year = 2025

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            Courses(name, semester, year)
        self.assertEqual(str(context.exception), "Name must be a non-empty string.")

    def test_invalid_semester(self):
        # Arrange
        name = "Introduction to AI"
        semester = "Autumn"  # Invalid semester
        year = 2025

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            Courses(name, semester, year)
        self.assertEqual(str(context.exception), "Semester must be one of: Spring, Summer, Fall, Winter.")

    def test_invalid_year_too_low(self):
        # Arrange
        name = "Introduction to AI"
        semester = "Fall"
        year = 2014  # Year below valid range

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            Courses(name, semester, year)
        self.assertEqual(str(context.exception), "Year must be between 2000 and 2100.")

    def test_invalid_year_too_high(self):
        # Arrange
        name = "Introduction to AI"
        semester = "Fall"
        year = 2031  # Year above valid range

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            Courses(name, semester, year)
        self.assertEqual(str(context.exception), "Year must be between 2000 and 2100.")

    def test_edge_case_year_lower_bound(self):
        # Arrange
        name = "Introduction to AI"
        semester = "Fall"
        year = 2015  # Lower bound of valid range

        # Act
        course = Courses(name, semester, year)

        # Assert
        self.assertEqual(course.Year, year)

    def test_edge_case_year_upper_bound(self):
        # Arrange
        name = "Introduction to AI"
        semester = "Fall"
        year = 2030  # Upper bound of valid range

        # Act
        course = Courses(name, semester, year)

        # Assert
        self.assertEqual(course.Year, year)

if __name__ == '__main__':
    unittest.main()

