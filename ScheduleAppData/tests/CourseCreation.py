from django.test import TestCase, Client
from django.urls import reverse
from ScheduleAppData.models import User
from ScheduleAppData.models import Courses as Courses

class CourseCreationTest(TestCase):
    def setUp(self):
        # Set up any initial data if needed
        self.valid_data = {
            "action": "create_course",
            "title": "Introduction to Python",
            "semester": "Fall",
            "year": "2025"
        }
        self.valid_data_upper = {
            "action": "create_course",
            "title": "Introduction to Python",
            "semester": "Fall",
            "year": "2030"
        }
        self.valid_data_lower = {
            "action": "create_course",
            "title": "Introduction to Python",
            "semester": "Fall",
            "year": "2015"
        }
        self.invalid_data_too_low = {
            "action": "create_course",
            "title": "Introduction to Python",
            "semester": "Fall",
            "year": "2000"
        }
        self.invalid_data_too_high = {
            "action": "create_course",
            "title": "Introduction to Python",
            "semester": "Fall",
            "year": "3000"
        }
        self.invalid_data_missing_title = {
            "action": "create_course",
            "title": "",
            "semester": "Fall",
            "year": "2025"
        }
        self.invalid_data_invalid_year = {
            "action": "create_course",
            "title": "Advanced Python",
            "semester": "Spring",
            "year": "invalid"
        }
        self.invalid_data_missing_semester = {
            "action": "create_course",
            "title": "Introduction to Python",
            "semester": "",
            "year": "2025"
        }

    def test_valid_course_creation(self):
        response = self.client.post(reverse('adminDashboard'), self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Courses.objects.filter(CourseName="Introduction to Python", Semester="Fall", Year=2025).exists())

    def test_invalid_course_creation_year(self):
        response = self.client.post(reverse('adminDashboard'), self.invalid_data_missing_title)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Courses.objects.filter(CourseName="", Semester="Fall", Year=2025).exists())
    def test_invalid_course_creation_semester(self):
        response = self.client.post(reverse('adminDashboard'), self.invalid_data_missing_semester)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Courses.objects.filter(CourseName="Introduction to Python", Semester="", Year=2025).exists())

    def test_invalid_course_creation_with_year(self):
        response = self.client.post(reverse('adminDashboard'), self.invalid_data_invalid_year)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Courses.objects.filter(CourseName="Introduction to Python", Semester="Fall", Year=1).exists())
    def test_invalid_course_too_high(self):
        response = self.client.post(reverse('adminDashboard'), self.invalid_data_too_high)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Courses.objects.filter(CourseName="Introduction to Python", Semester="Fall", Year=3000).exists())
    def test_invalid_course_too_low(self):
        response = self.client.post(reverse('adminDashboard'), self.invalid_data_too_low)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Courses.objects.filter(CourseName="Introduction to Python", Semester="Fall", Year=2000).exists())
    def test_valid_course_lower(self):
        response = self.client.post(reverse('adminDashboard'), self.valid_data_lower)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Courses.objects.filter(CourseName="Introduction to Python", Semester="Fall", Year=2015).exists())
    def test_valid_course_upper(self):
        response = self.client.post(reverse('adminDashboard'), self.valid_data_upper)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Courses.objects.filter(CourseName="Introduction to Python", Semester="Fall", Year=2030).exists())
