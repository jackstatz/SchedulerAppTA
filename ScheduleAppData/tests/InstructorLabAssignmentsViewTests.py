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
        #create Assignments
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
        #create Lab Assignments (Linking TAs to Lab Sections)
        cls.lab_assignment = LabAssignment.objects.create(
            SectionId=cls.section_c1_lab, # Link to the lab section
            TAId=cls.ta1                  # Assign TA1
        )

    def setUp(self):
        self.client = Client()
        self.client.login(email=self.instructor.Email, password=self.instructor_password)

class InstructorLabAssignmentsViewTests(InstructorViewTestBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.lab_assign_url = reverse('instructor_lab_assignments', kwargs={'instructor_id': cls.instructor.Id})
        cls.bad_lab_assign_url = reverse('instructor_lab_assignments', kwargs={'instructor_id': 9999})

    def test_get_lab_assignments_page_loads(self):
        response = self.client.get(self.lab_assign_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'InstructorLabAssignments.html')

    def test_get_lab_assignments_assigned(self):
        response = self.client.get(self.lab_assign_url)
        self.assertEqual(response.context['instructor'], self.instructor)
        #check courses (should only be courses linked to instructor)
        self.assertIn(self.course1, response.context['courses'])
        self.assertIn(self.course2, response.context['courses'])
        self.assertNotIn(self.other_course, response.context['courses'])
        #check sections (should only be LAB sections linked to instructor)
        self.assertIn(self.section_c1_lab, response.context['sections'])
        self.assertNotIn(self.section_c1_lec, response.context['sections'])
        self.assertNotIn(self.section_c2_lec, response.context['sections'])
        #check TAs (should list all available TAs)
        self.assertIn(self.ta1, response.context['tas'])
        self.assertIn(self.ta2, response.context['tas'])
        # check existing assignments
        self.assertIn(self.lab_assignment, response.context['assignments'])

    def test_get_lab_assignments_displays_data(self):
        response = self.client.get(self.lab_assign_url)
        self.assertContains(response, self.course1.CourseName) #course dropdown
        self.assertContains(response, f'Section {self.section_c1_lab.SectionNum}') # section dropdown/list
        self.assertContains(response, f'{self.ta1.FirstName} {self.ta1.LastName}') #TA dropdown/list
        self.assertContains(response, 'action="assign_ta"') #form action

    def test_get_lab_assignments_invalid_instructor_id(self):
        with self.assertRaises(User.DoesNotExist):
            self.client.get(self.bad_lab_assign_url)

    def test_post_assign_ta_success_new(self):
        #assign ta2 to section_c1_lab (ta1 is already assigned, view updates)
        payload = {
            'action': 'assign_ta',
            'section_id': self.section_c1_lab.id,
            'ta_id': self.ta2.id, # Assign a different TA
        }
        response = self.client.post(self.lab_assign_url, payload)

        self.assertRedirects(response, self.lab_assign_url, status_code=302, target_status_code=200)

        self.lab_assignment.refresh_from_db()
        self.assertEqual(self.lab_assignment.TAId, self.ta2)

    def test_post_assign_ta_success_update(self):
        initial_ta = self.lab_assignment.TAId
        self.assertNotEqual(initial_ta, self.ta2) #ensure we're changing the TA

        payload = {
            'action': 'assign_ta',
            'section_id': self.section_c1_lab.id,
            'ta_id': self.ta2.id, #assign 2nd TA
        }
        response = self.client.post(self.lab_assign_url, payload)
        self.assertRedirects(response, self.lab_assign_url)
        self.lab_assignment.refresh_from_db()
        self.assertEqual(self.lab_assignment.TAId, self.ta2) #verify update worked

    def test_assign_invalid_id(self):
        payload = {
            'action': 'assign_ta',
            'section_id': 9999, #invalid ID
            'ta_id': self.ta1.id,
        }
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            self.client.post(self.lab_assign_url, payload)

    def test_post_assign_ta_invalid_ta_id(self):

        payload = {
            'action': 'assign_ta',
            'section_id': self.section_c1_lab.id,
            'ta_id': 9999, #ta_id instead of section id
        }
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            self.client.post(self.lab_assign_url, payload)