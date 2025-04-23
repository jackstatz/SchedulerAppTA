from django.test import TestCase, Client
from django.urls import reverse
from ScheduleAppData.models import Courses as CoursesModel # Rename to avoid conflict with Courses view
from ScheduleAppData.models import User
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

class AdminDashboardTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.dashboard_url = '/adminDashboard/'
        self.test_user = User.objects.create(
            Email='someuser@test.com', Password='pw', Role='TA',
            FirstName='Setup', LastName='User', Phone='1112223333'
        )


    def test_create_course(self):
        initial_course_count = CoursesModel.objects.count()

        course_name = "Test"
        course_semester = "Spring"
        course_year = 2025

        payload = {
            "action": "create_course",
            "title": course_name,
            "semester": course_semester,
            "year": course_year,
        }

        response = self.client.post(self.dashboard_url, payload)
        self.assertEqual(CoursesModel.objects.count(), initial_course_count + 1)
        try:
            new_course = CoursesModel.objects.get(CourseName=course_name, Year=course_year)
            self.assertEqual(new_course.CourseName, course_name)
            self.assertEqual(new_course.Semester, course_semester)
            self.assertEqual(new_course.Year, course_year)
        except CoursesModel.DoesNotExist:
            self.fail(f"Course with name '{course_name}' and year {course_year} was not created.")

    #Add more tests for courses yet

    def test_create_account(self):
        payload = {
            "action": "create_account",
            "firstName": "Test",
            "lastName": "User",
            "email": "abc@uwm.edu",  # Empty email
            "password": "efg",
            "phone": "1112223333",
            "role": "TA",
        }
        response = self.client.post(self.dashboard_url, payload)
        user_created = User.objects.filter(Email="abc@uwm.edu").exists()
        self.assertTrue(user_created)


    def test_create_course_no_name(self):
        initial_course_count = CoursesModel.objects.count()

        payload = {
            "action": "create_course",
            "title": "",  # Empty name
            "semester": "Spring",
            "year": 2025,
        }
        response = self.client.post(self.dashboard_url, payload)
        self.assertFalse(CoursesModel.objects.filter(CourseName="").exists())
        self.assertEqual(CoursesModel.objects.count(), initial_course_count)

    def test_create_account_no_email(self):
        initial_user_count = User.objects.count()

        payload = {
            "action": "create_account",
            "firstName": "Test",
            "lastName": "User",
            "email": "",  # Empty email
            "password": "efg",
            "phone": "1112223333",
            "role": "TA",
        }
        self.assertFalse(User.objects.filter(Email="").exists())
        self.assertEqual(User.objects.count(), initial_user_count)

    def test_create_account_no_firstname(self):
        payload = {
            "action": "create_account",
            "firstName": "", #No first name
            "lastName": "User",
            "email": "abc@uwm.edu",
            "password": "efg",
            "phone": "1112223333",
            "role": "TA",
        }

        # Check if user was actually created
        response = self.client.post(self.dashboard_url, payload)
        user_created = User.objects.filter(Email="abc@uwm.edu").exists()
        self.assertFalse(user_created)

    def test_create_account_no_lastname(self):
        payload = {
            "action": "create_account",
            "firstName": "Test",
            "lastName": "", #No last name
            "email": "abc@abc@uwm.edu",
            "password": "efg",
            "phone": "1112223333",
            "role": "TA",
        }
        user_created = User.objects.filter(Email="abc@uwm.edu").exists()
        self.assertFalse(user_created)

    def test_create_account_no_password(self):
        payload = {
            "action": "create_account",
            "firstName": "Test",
            "lastName": "User",
            "email": "abc@abc@uwm.edu",
            "password": "", #No password
            "phone": "1112223333",
            "role": "TA",
        }
        user_created = User.objects.filter(Email="abc@uwm.edu").exists()
        self.assertFalse(user_created)

    def test_create_account_wrong_phone_length(self):
        payload = {
            "action": "create_account",
            "firstName": "Test",
            "lastName": "User",
            "email": "abc@abc@uwm.edu",
            "password": "efg",
            "phone": "11111", #Not 10 numbers
            "role": "TA",
        }
        user_created = User.objects.filter(Email="abc@uwm.edu").exists()
        self.assertFalse(user_created)

    def test_create_account_letters_in_phone(self):
        payload = {
            "action": "create_account",
            "firstName": "Test",
            "lastName": "User",
            "email": "abc@abc@uwm.edu",
            "password": "efg",
            "phone": "abcdefghij", #Not numbers, but right length
            "role": "TA",
        }
        user_created = User.objects.filter(Email="abc@uwm.edu").exists()
        self.assertFalse(user_created)






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

