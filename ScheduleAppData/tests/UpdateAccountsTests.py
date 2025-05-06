from django.http import QueryDict
from django.test import TestCase
from unittest.mock import Mock, patch
from datetime import time
from ScheduleAppData.models import User  # Replace 'your_app' with the actual app name
from ScheduleAppData.views import update_account  # Replace 'your_app.views' with the actual module

class UpdateAccountTests(TestCase):
    def setUp(self):
        # Create a mock instructor object
        self.instructor = Mock(spec=User)
        self.instructor.FirstName = "John"
        self.instructor.LastName = "Doe"
        self.instructor.Email = "john.doe@example.com"
        self.instructor.Phone = "1234567890"
        self.instructor.HomeAddress = "123 Main St"
        self.instructor.OfficeHourDays = "M,T,W"
        self.instructor.OfficeHourStartTime = time(9, 0)
        self.instructor.OfficeHourEndTime = time(10, 0)
        self.instructor.Password = "hashed_password"

    @patch('ScheduleAppData.views.make_password')  # Mock the password hashing function
    def test_update_all_fields(self, mock_make_password):
        mock_make_password.return_value = "new_hashed_password"
        request = Mock()
        request.POST = QueryDict(mutable=True)
        request.POST.update = {
            "firstName": "Jane",
            "lastName": "Smith",
            "email": "jane.smith@example.com",
            "phone": "0987654321",
            "homeAddress": "456 Elm St",
            "selectedDays": ["T", "R"],
            "officeHourStartTime": "10:00",
            "officeHourEndTime": "11:00",
            "password": "new_password"
        }

        update_account(request, self.instructor)

        self.assertEqual(self.instructor.FirstName, "Jane")
        self.assertEqual(self.instructor.LastName, "Smith")
        self.assertEqual(self.instructor.Email, "jane.smith@example.com")
        self.assertEqual(self.instructor.Phone, "0987654321")
        self.assertEqual(self.instructor.HomeAddress, "456 Elm St")
        self.assertEqual(self.instructor.OfficeHourDays, "T,Th")
        self.assertEqual(self.instructor.OfficeHourStartTime, "10:00")
        self.assertEqual(self.instructor.OfficeHourEndTime, "11:00")
        self.assertEqual(self.instructor.Password, "new_hashed_password")
        self.instructor.save.assert_called_once()

    def test_missing_optional_fields(self):
        request = Mock()
        request.POST = QueryDict(mutable=True)
        request.POST.update = {
            "firstName": "Jane",
            "lastName": "Smith",
            "email": "jane.smith@example.com",
            "phone": "0987654321",
            "homeAddress": "456 Elm St",
            "selectedDays": ["T", "R"]
        }

        update_account(request, self.instructor)

        self.assertEqual(self.instructor.FirstName, "Jane")
        self.assertEqual(self.instructor.LastName, "Smith")
        self.assertEqual(self.instructor.Email, "jane.smith@example.com")
        self.assertEqual(self.instructor.Phone, "0987654321")
        self.assertEqual(self.instructor.HomeAddress, "456 Elm St")
        self.assertEqual(self.instructor.OfficeHourDays, "T,Th")
        self.assertEqual(self.instructor.OfficeHourStartTime, time(9, 0))  # Unchanged
        self.assertEqual(self.instructor.OfficeHourEndTime, time(10, 0))  # Unchanged
        self.instructor.save.assert_called_once()

    def test_no_password_update(self):
        request = Mock()
        request.POST = QueryDict(mutable=True)
        request.POST.update = {
            "firstName": "Jane",
            "lastName": "Smith",
            "email": "jane.smith@example.com",
            "phone": "0987654321",
            "homeAddress": "456 Elm St",
            "selectedDays": ["T", "R"],
            "officeHourStartTime": "10:00",
            "officeHourEndTime": "11:00"
        }

        update_account(request, self.instructor)

        self.assertEqual(self.instructor.Password, "hashed_password")  # Unchanged
        self.instructor.save.assert_called_once()

    def test_invalid_data(self):
        request = Mock()
        request.POST = QueryDict(mutable=True)
        request.POST.update = {
            "firstName": "",
            "lastName": "",
            "email": "invalid_email",
            "phone": "not_a_phone_number",
            "homeAddress": "",
            "selectedDays": [],
            "officeHourStartTime": None,
            "officeHourEndTime": None
        }

        update_account(request, self.instructor)

        self.assertEqual(self.instructor.FirstName, "")  # Invalid but updated
        self.assertEqual(self.instructor.LastName, "")  # Invalid but updated
        self.assertEqual(self.instructor.Email, "invalid_email")  # Invalid but updated
        self.assertEqual(self.instructor.Phone, "not_a_phone_number")  # Invalid but updated
        self.assertEqual(self.instructor.HomeAddress, "")  # Invalid but updated
        self.assertEqual(self.instructor.OfficeHourDays, "")  # Invalid but updated
        self.assertIsNone(self.instructor.OfficeHourStartTime)  # Invalid but updated
        self.assertIsNone(self.instructor.OfficeHourEndTime)  # Invalid but updated
        self.instructor.save.assert_called_once()
