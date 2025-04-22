from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db import IntegrityError

from ScheduleAppData.models import User, Courses, Assignments, Sections


# Create your views here.
def create_course(title, semester, year):
    from ScheduleAppData.models import Courses
    # Handle course creation
    try:
        # Create a new course
        Courses.objects.create(
            CourseName=title,
            Semester=semester,
            Year=year
        )
    except IntegrityError:
        return JsonResponse({"error": "A course with this name already exists."}, status=400)

def add_assignment(request, course):
    """Helper method to handle adding an assignment."""
    assignment_name = request.POST.get("assignment_name")
    due_date = request.POST.get("due_date")
    Assignments.objects.create(AssignmentName=assignment_name, DueDate=due_date, CourseId=course)

def add_section(request, course):
    """Helper method to handle adding a section."""
    section_num = request.POST.get("section_num")
    schedule = request.POST.get("schedule")
    instructor_email = request.POST.get("instructor_email")
    instructor = User.objects.filter(Email=instructor_email).first()
    if instructor:
        Sections.objects.create(SectionNum=section_num, Schedule=schedule, InstructorId=instructor, CourseId=course)


def create_account(first_name, last_name, email, password, phone, role):
    try:
        # Create a new user
        User.objects.create(
            FirstName=first_name,
            LastName=last_name,
            Email=email,
            Password=password,
            Phone=phone,
            Role=role
        )
    except IntegrityError:
        return JsonResponse({"error": "An account with this email already exists."}, status=400)

def deleteAccount(account_id=None):
    try:
        # Delete the account with the given ID
        User.objects.filter(Id=account_id).delete()
        return redirect("/accounts/")  # Redirect back to the accounts page
    except User.DoesNotExist:
        return JsonResponse({"error": "Account not found."}, status=404)

def deleteCourse(course_id=None):
    from ScheduleAppData.models import Courses
    try:
        # Delete the course with the given ID
        Courses.objects.filter(Id=course_id).delete()
        return redirect("/courses/")  # Redirect back to the accounts page
    except User.DoesNotExist:
        return JsonResponse({"error": "Account not found."}, status=404)

def AuthenticateUser(email=None, password=None):
    if email is None or password is None:
        return False

    try:
        # Fetch the user with the given email
        user = User.objects.get(Email=email)

        # Compare the provided password with the stored password
        if password == user.Password:
            return user
        else:
            return False
    except User.DoesNotExist:
        return False

class AdminDashboard(View):
    def get(self, request):
        return render(request, "AdminDashboard.html")
    def post(self, request):
        action = request.POST.get("action")

        match action:
            case "create_account":
                # Handle account creation
                first_name = request.POST.get("firstName")
                last_name = request.POST.get("lastName")
                email = request.POST.get("email")
                password = request.POST.get("password")
                phone = request.POST.get("phone")
                role = request.POST.get("role")

                create_account(first_name, last_name, email, password, phone, role)
                return JsonResponse({"message": "Account created successfully! Use back button to get back to dashboard."})
            case "create_course":
                title = request.POST.get("title")
                semester = request.POST.get("semester")
                year = request.POST.get("year")

                create_course(title, semester, year)
                return JsonResponse({"message": "Course created successfully! Use back button to get back to dashboard."})
            case _:
                return JsonResponse({"error": "Invalid action."}, status=400)


class InstructorDashboard(View):
    def get(self, request):
        return render(request, "InstructorDashboard.html")
    def post(self, request):
        pass

class TADashboard(View):
    def get(self, request):
        return render(request, "TADashboard.html")
    def post(self, request):
        pass

class Accounts(View):
    def get(self, request):
        AllAccounts = User.objects.all().values("FirstName", "LastName", "Email", "Phone", "Role", "Id")
        return render(request, "Accounts.html", {'accounts': AllAccounts})
    def post(self, request):
        action = request.POST.get("action")
        if action == "delete_account":
            account_id = request.POST.get("account_id")
            deleteAccount(account_id)
            return JsonResponse({"message": "Account deleted successfully! Use back button to get back to All Accounts"})

        return self.get(request)

class Courses(View):
    def get(self, request):
        from ScheduleAppData.models import Courses
        Courses = Courses.objects.all().values("CourseName", "Semester", "Year", "Id")
        return render(request, "Courses.html", {'Courses': Courses})

    def post(self, request):
        action = request.POST.get("action")
        if action == "delete_course":
            course_id = request.POST.get("course_id")
            deleteCourse(course_id)
            return JsonResponse({"message": "Course deleted successfully! Use back button to get back to All Courses."})
        return self.get(request)


class Login(View):
    def get(self, request):
        return render(request, 'LoginPage.html')
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        validUser = AuthenticateUser(email, password)

        if validUser:
            match validUser.Role:
                case 'Supervisor':
                    return redirect('/adminDashboard')
                case 'Instructor':
                    return redirect('/InstructorDashboard')
                case 'TA':
                    return redirect('/TADashboard')
        else:
            return JsonResponse('Login failed.')

class CoursePage(View):
    def get(self, request, course_id):
        from ScheduleAppData.models import Courses
        # Retrieve the course using the course_id from the URL
        course = Courses.objects.get(Id=course_id)
        assignments = Assignments.objects.filter(CourseId=course)
        sections = Sections.objects.filter(CourseId=course)

        # Render the page with course, assignments, and sections
        return render(request, 'CoursePage.html', {
            'course': course,
            'assignments': assignments,
            'sections': sections
        })

    def post(self, request, course_id):
        from ScheduleAppData.models import Assignments, Courses, Sections
        # Retrieve the course using the course_id from the URL
        course = Courses.objects.get(Id=course_id)

        if "add_assignment" in request.POST:
            add_assignment(request, course)

        elif "add_section" in request.POST:
            add_section(request, course)

        # Fetch updated assignments and sections after the POST operation
        assignments = Assignments.objects.filter(CourseId=course)
        sections = Sections.objects.filter(CourseId=course)

        # Re-render the page with updated data
        return render(request, 'CoursePage.html', {
            'course': course,
            'assignments': assignments,
            'sections': sections
        })

class AccountPage(View):
    def get(self, request, account_id):
        # Retrieve the account using the account_id
        account = get_object_or_404(User, pk=account_id)
        return render(request, 'AccountPage.html', {'account': account})

    def post(self, request, account_id):
        # Retrieve the account using the account_id
        account = get_object_or_404(User, pk=account_id)

        # Handle account updates (example: updating phone number)
        if "update_account" in request.POST:
            account.Phone = request.POST.get("phone")
            account.save()

        return render(request, 'AccountPage.html', {'account': account})