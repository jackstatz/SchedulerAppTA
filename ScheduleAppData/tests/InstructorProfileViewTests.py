from django.test import TestCase, Client
from django.urls import reverse
from ScheduleAppData.models import Courses as CoursesModel
from ScheduleAppData.models import User, Courses as CoursesModel, Sections, Assignments, LabAssignment
from datetime import date, timedelta

class InstructorViewTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create Instructors
        cls.instructor_password = 'instr_password'
        cls.instructor = User.objects.create(
            Email='main_instructor@test.com', Password=cls.instructor_password, Role='Instructor',
            FirstName='Main', LastName='Instructor', Phone='9876543210'
        )
        cls.other_instructor = User.objects.create(
            Email='other_instructor@test.com', Password='pw', Role='Instructor',
            FirstName='Other', LastName='Prof', Phone='1112223334'
        )
        # Create TAs
        cls.ta1 = User.objects.create(
            Email='ta1@test.com', Password='pw', Role='TA',
            FirstName='Teaching', LastName='Assistant1', Phone='5550001111'
        )
        cls.ta2 = User.objects.create(
            Email='ta2@test.com', Password='pw', Role='TA',
            FirstName='Teaching', LastName='Assistant2', Phone='5550002222'
        )
        # Create Courses
        cls.course1 = CoursesModel.objects.create(
            CourseName='Instructor Course 1', Semester='Fall', Year=2024
        )
        cls.course2 = CoursesModel.objects.create(
            CourseName='Instructor Course 2', Semester='Spring', Year=2025
        )
        cls.other_course = CoursesModel.objects.create( # Course not assigned to main instructor
            CourseName='Unrelated Course', Semester='Fall', Year=2024
        )
        # Create Sections linking instructor to courses
        # Lecture Section for Course 1
        cls.section_c1_lec = Sections.objects.create(
            CourseId=cls.course1, SectionNum='001', Schedule='MW 10:00', InstructorId=cls.instructor, SectionType="Lecture" # Assuming SectionType exists
        )
        # Lab Section for Course 1
        cls.section_c1_lab = Sections.objects.create(
            CourseId=cls.course1, SectionNum='801', Schedule='F 10:00', InstructorId=cls.instructor, SectionType="Lab" # Assuming SectionType exists
        )
         # Lecture Section for Course 2
        cls.section_c2_lec = Sections.objects.create(
            CourseId=cls.course2, SectionNum='001', Schedule='TR 11:00', InstructorId=cls.instructor, SectionType="Lecture"
        )
        # Section for other course/instructor
        cls.section_other = Sections.objects.create(
            CourseId=cls.other_course, SectionNum='001', Schedule='TR 1:00', InstructorId=cls.other_instructor, SectionType="Lecture"
        )
        # Create Assignments
        cls.assignment_c1_1 = Assignments.objects.create(
            CourseId=cls.course1, AssignmentName='C1 Homework 1', DueDate=date.today() + timedelta(days=7)
        )
        cls.assignment_c1_2 = Assignments.objects.create(
            CourseId=cls.course1, AssignmentName='C1 Quiz 1', DueDate=date.today() + timedelta(days=14)
        )
        cls.assignment_c2_1 = Assignments.objects.create(
            CourseId=cls.course2, AssignmentName='C2 Project Proposal', DueDate=date.today() + timedelta(days=21)
        )
        cls.assignment_other = Assignments.objects.create(
            CourseId=cls.other_course, AssignmentName='Other Course HW', DueDate=date.today() + timedelta(days=5)
        )
        # Create Lab Assignments (Linking TAs to Lab Sections)
        cls.lab_assignment = LabAssignment.objects.create(
            SectionId=cls.section_c1_lab, # Link to the lab section
            TAId=cls.ta1                  # Assign TA1
        )

    def setUp(self):
        self.client = Client()
        self.client.login(email=self.instructor.Email, password=self.instructor_password)

class InstructorProfileViewTests(InstructorViewTestBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.profile_url = reverse('instructor_profile', kwargs={'instructor_id': cls.instructor.Id})
        cls.bad_profile_url = reverse('instructor_profile', kwargs={'instructor_id': 99998})

    def test_get_profile_page_loads(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'InstructorProfile.html')

    def test_get_profile_context_data(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.context['instructor'], self.instructor)

    def test_get_profile_displays_data(self):
        response = self.client.get(self.profile_url)
        self.assertContains(response, self.instructor.Email)
        self.assertContains(response, self.instructor.FirstName)

    def test_get_profile_invalid_instructor_id(self):
        with self.assertRaises(User.DoesNotExist):
            self.client.get(self.bad_profile_url)

    def test_post_update_profile_success(self):
        new_email = "update@uwm.edu"
        payload = {
            'email': new_email,
        }
        dashboard_url = reverse('instructor_dashboard', kwargs={'instructor_id': self.instructor.id})

        response = self.client.post(self.profile_url, payload)

        # Check database
        self.instructor.refresh_from_db()
        self.assertEqual(self.instructor.Email, new_email)