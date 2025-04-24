from django.test import TestCase, Client
from django.urls import reverse
from ScheduleAppData.models import User
from ScheduleAppData.models import Courses as CoursesModel


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
    #TODO
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