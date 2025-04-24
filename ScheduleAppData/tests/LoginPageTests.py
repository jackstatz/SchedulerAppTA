from django.test import TestCase, Client
from django.urls import reverse
from ScheduleAppData.models import Courses as Courses
from ScheduleAppData.models import User


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