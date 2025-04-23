from django.test import TestCase, Client
from django.urls import reverse
from ScheduleAppData.models import Courses as CoursesModel # Rename to avoid conflict with Courses view
from ScheduleAppData.models import User
# Create your tests here.

from django.test import TestCase
from django.urls import reverse

from .models import Courses, User  # Assuming the class is in course_module.py

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

