from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.urls import reverse

from .models import Courses, User  # Assuming the class is in course_module.py

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

class LoginPageTest(TestCase):
    def setUp(self):
        # Create test users for each role
        self.supervisor = User.objects.create(
            FirstName="Supervisor",
            LastName="User",
            Email="supervisor@example.com",
            Password="supervisorpassword",
            Phone="1234567890",
            Role="Supervisor"
        )
        self.instructor = User.objects.create(
            FirstName="Instructor",
            LastName="User",
            Email="instructor@example.com",
            Password="instructorpassword",
            Phone="1234567890",
            Role="Instructor"
        )
        self.ta = User.objects.create(
            FirstName="TA",
            LastName="User",
            Email="ta@example.com",
            Password="tapassword",
            Phone="1234567890",
            Role="TA"
        )

    def test_login_page_loads_correctly(self):
        """Test that the login page loads successfully."""
        response = self.client.get(reverse('login'))  # Ensure the login URL is named 'login'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TA Scheduler App")  # Check if the page contains the title

    def test_valid_login_redirects_supervisor(self):
        """Test that a supervisor is redirected to the admin dashboard."""
        response = self.client.post(reverse('login'), {
            'email': self.supervisor.Email,
            'password': self.supervisor.Password
        })

        self.assertRedirects(response, '/adminDashboard/')

    def test_valid_login_redirects_instructor(self):
        """Test that an instructor is redirected to the instructor dashboard."""
        response = self.client.post(reverse('login'), {
            'email': self.instructor.Email,
            'password': self.instructor.Password
        })
        self.assertRedirects(response, reverse('instructor_dashboard', args=[self.instructor.Id]))

    def test_valid_login_redirects_ta(self):
        """Test that a TA is redirected to the TA dashboard."""
        response = self.client.post(reverse('login'), {
            'email': self.ta.Email,
            'password': self.ta.Password
        })
        self.assertRedirects(response, reverse('TA_dashboard', args=[self.ta.Id]))

    def test_invalid_login(self):
        """Test that login fails with invalid credentials."""
        response = self.client.post(reverse('login'), {
            'email': "invalid@example.com",
            'password': "wrongpassword"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TA Scheduler App")  # Check if the page reloads

class CourseCreationTest(TestCase):
    def setUp(self):
        # Set up any initial data if needed
        self.valid_data = {
            "action": "create_course",
            "title": "Introduction to Python",
            "semester": "Fall",
            "year": "2025"
        }
        self.invalid_data_missing_fields = {
            "action": "create_course",
            "title": "",
            "semester": "Fall",
            "year": "2025"
        }
        self.invalid_data_invalid_year = {
            "action": "create_course",
            "title": "Advanced Python",
            "semester": "Spring",
            "year": "invalid_year"
        }

    def test_valid_course_creation(self):
        """Test that a course is successfully created with valid data."""
        response = self.client.post(reverse('adminDashboard'), self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Courses.objects.filter(CourseName="Introduction to Python", Semester="Fall", Year=2025).exists())

    def test_duplicate_course(self):
        """Test that the form fails when attempting to create a duplicate course."""
        # Create the course first
        Courses.objects.create(CourseName="Introduction to Python", Semester="Fall", Year=2025)

        # Attempt to create the same course again
        response = self.client.post(reverse('adminDashboard'), self.valid_data)
        self.assertEqual(response.status_code, 400)  # Assuming the view returns 400 for duplicates
        self.assertEqual(Courses.objects.filter(CourseName="Introduction to Python", Semester="Fall", Year=2025).count(), 1)

from django.test import TestCase
from django.urls import reverse
from ScheduleAppData.models import User  # Adjust the import path based on your project structure

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

    def test_valid_account_creation(self):
        """Test that an account is successfully created with valid data."""
        response = self.client.post(reverse('adminDashboard'), self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(Email="johndoe@example.com").exists())

    def test_duplicate_account(self):
        """Test that the form fails when attempting to create a duplicate account."""
        # Create the account first
        User.objects.create(
            FirstName="John",
            LastName="Doe",
            Email="johndoe@example.com",
            Password="securepassword",
            Phone="1234567890",
            Role="Instructor"
        )

        # Attempt to create the same account again
        response = self.client.post(reverse('adminDashboard'), self.valid_data)
        self.assertEqual(response.status_code, 400)  # Assuming the view returns 400 for duplicates
        self.assertEqual(User.objects.filter(Email="johndoe@example.com").count(), 1)

if __name__ == '__main__':
    unittest.main()

