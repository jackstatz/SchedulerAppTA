from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock


class LoginViewMockTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')

        # Create a mock user for testing
        self.mock_supervisor = MagicMock()
        self.mock_supervisor.Role = 'Supervisor'
        self.mock_supervisor.Id = 1

        self.mock_instructor = MagicMock()
        self.mock_instructor.Role = 'Instructor'
        self.mock_instructor.Id = 2

        self.mock_ta = MagicMock()
        self.mock_ta.Role = 'TA'
        self.mock_ta.Id = 3

    @patch('ScheduleAppData.views.AuthenticateUser')
    def test_login_supervisor_redirect(self, mock_authenticate):
        # Setup mock to return a supervisor user
        mock_authenticate.return_value = self.mock_supervisor

        # Perform login
        response = self.client.post(self.login_url, {
            'email': 'supervisor@example.com',
            'password': 'password'
        })

        # Verify authentication was called with correct parameters
        mock_authenticate.assert_called_once_with('supervisor@example.com', 'password')

        # Verify redirect to admin dashboard
        self.assertRedirects(response, '/adminDashboard/', fetch_redirect_response=False)

    @patch('ScheduleAppData.views.AuthenticateUser')
    def test_login_instructor_redirect(self, mock_authenticate):
        # Setup mock to return an instructor user
        mock_authenticate.return_value = self.mock_instructor

        # Perform login
        response = self.client.post(self.login_url, {
            'email': 'instructor@example.com',
            'password': 'password'
        })

        # Verify authentication was called with correct parameters
        mock_authenticate.assert_called_once_with('instructor@example.com', 'password')

        # Verify redirect to instructor dashboard
        self.assertRedirects(response, reverse('instructor_dashboard', args=[self.mock_instructor.Id]),
                             fetch_redirect_response=False)

    @patch('ScheduleAppData.views.AuthenticateUser')
    def test_login_ta_redirect(self, mock_authenticate):
        # Setup mock to return a TA user
        mock_authenticate.return_value = self.mock_ta

        # Perform login
        response = self.client.post(self.login_url, {
            'email': 'ta@example.com',
            'password': 'password'
        })

        # Verify authentication was called with correct parameters
        mock_authenticate.assert_called_once_with('ta@example.com', 'password')

        # Verify redirect to TA dashboard
        self.assertRedirects(response, reverse('TA_dashboard', args=[self.mock_ta.Id]),
                             fetch_redirect_response=False)

    @patch('ScheduleAppData.views.AuthenticateUser')
    def test_login_failed_authentication(self, mock_authenticate):
        # Setup mock to return False (authentication failed)
        mock_authenticate.return_value = False

        # Perform login
        response = self.client.post(self.login_url, {
            'email': 'invalid@example.com',
            'password': 'wrong_password'
        })

        # Verify authentication was called with correct parameters
        mock_authenticate.assert_called_once_with('invalid@example.com', 'wrong_password')

        # Verify response status code (should stay on login page)
        self.assertEqual(response.status_code, 200)

        # Verify template used (should be login page)
        self.assertTemplateUsed(response, 'LoginPage.html')
