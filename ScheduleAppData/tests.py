from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from .models import Courses  # Assuming the class is in course_module.py

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

