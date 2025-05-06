from django.test import TestCase
from unittest.mock import patch, MagicMock
from ScheduleAppData.views import AuthenticateUser, create_course
from ScheduleAppData.models import User, Courses
from django.http import JsonResponse

class AuthenticationMockTests(TestCase):
    def setUp(self):
        # We don't need to create actual users in the database for these tests
        pass

    @patch('ScheduleAppData.views.User.objects.get')
    @patch('ScheduleAppData.views.check_password')
    def test_authenticate_user_success(self, mock_check_password, mock_user_get):
        # Setup mocks
        mock_user = MagicMock()
        mock_user.Password = 'hashed_password'
        mock_user.Email = 'test@example.com'
        mock_user_get.return_value = mock_user
        mock_check_password.return_value = True

        # Call the function
        result = AuthenticateUser('test@example.com', 'correct_password')

        # Assertions
        mock_user_get.assert_called_once_with(Email='test@example.com')
        mock_check_password.assert_called_once_with('correct_password', 'hashed_password')
        self.assertEqual(result, mock_user)

    @patch('ScheduleAppData.views.User.objects.get')
    @patch('ScheduleAppData.views.check_password')
    def test_authenticate_user_wrong_password(self, mock_check_password, mock_user_get):
        # Setup mocks
        mock_user = MagicMock()
        mock_user.Password = 'hashed_password'
        mock_user_get.return_value = mock_user
        mock_check_password.return_value = False

        # Call the function
        result = AuthenticateUser('test@example.com', 'wrong_password')

        # Assertions
        mock_user_get.assert_called_once_with(Email='test@example.com')
        mock_check_password.assert_called_once_with('wrong_password', 'hashed_password')
        self.assertFalse(result)

    @patch('ScheduleAppData.views.User.objects.get')
    def test_authenticate_user_nonexistent(self, mock_user_get):
        # Setup mock to raise exception
        mock_user_get.side_effect = User.DoesNotExist()

        # Call the function
        result = AuthenticateUser('nonexistent@example.com', 'any_password')

        # Assertions
        mock_user_get.assert_called_once_with(Email='nonexistent@example.com')
        self.assertFalse(result)

class CourseCreationMockTests(TestCase):
    def setUp(self):
        # We don't need to create actual courses in the database for these tests
        pass

    @patch('ScheduleAppData.models.Courses.objects.create')
    def test_create_course_success(self, mock_create):
        # Setup mock
        mock_create.return_value = MagicMock()

        # Call the function
        result = create_course('Test Course', 'Fall', '2023')

        # Assertions
        mock_create.assert_called_once_with(
            CourseName='Test Course',
            Semester='Fall',
            Year='2023'
        )
        self.assertTrue(result)

    @patch('ScheduleAppData.models.Courses.objects.create')
    def test_create_course_integrity_error(self, mock_create):
        # Setup mock to raise IntegrityError
        from django.db import IntegrityError
        mock_create.side_effect = IntegrityError()

        # Call the function
        result = create_course('Existing Course', 'Fall', '2023')

        # Assertions
        mock_create.assert_called_once()
        self.assertIsInstance(result, JsonResponse)
        self.assertEqual(result.status_code, 400)

    def test_create_course_validation_error(self):
        # No mocking needed for validation errors

        # Call the function with invalid data
        result = create_course('', 'Fall', '2023')

        # Assertions
        self.assertIsInstance(result, JsonResponse)
        self.assertEqual(result.status_code, 400)

        # Convert content to Python dict
        import json
        content = json.loads(result.content.decode('utf-8'))

        self.assertIn('errors', content)
        self.assertIn('Title', content['errors'])
