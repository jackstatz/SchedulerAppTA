from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password

from ScheduleAppData.models import User, Courses, Sections, Days


# Create your views here.
def create_course(title, semester, year):
    from ScheduleAppData.models import Courses

    errors = {}
    if not title:
        errors["Title"] = f"Title cannot be empty."
    if not semester:
        errors["Semester"] = f"Semester cannot be empty."
    if not year:
        errors["Year"] = f"Year cannot be empty."
    if not year.isdigit():
        errors["Year"] = "Year must contain only digits."
    if errors:
        return JsonResponse({"errors": errors}, status=400)

    try:
        # Create a new course
        Courses.objects.create(
            CourseName=title,
            Semester=semester,
            Year=year
        )
        return True
    except IntegrityError:
        return JsonResponse({"error": "A course with this name already exists."}, status=400)


def add_section(request, course):
    """Helper method to handle adding a section."""
    section_num = request.POST.get("section_num")
    scheduledDays = request.POST.getlist("selectedDays")
    instructor_email = request.POST.get("instructor_email")
    instructor = User.objects.filter(Email=instructor_email).first()
    startTime = request.POST.get("startTime")
    endTime = request.POST.get("endTime")
    if instructor:
        section = Sections.objects.create(SectionNum=section_num, ScheduledDays=",".join(scheduledDays), CourseId=course, ScheduledStartTime=startTime, ScheduledEndTime=endTime)
        section.Instructors.add(instructor)

def edit_section(request):
    instructor_email = request.POST.get("instructor_email_add")
    instructor = User.objects.filter(Email=instructor_email).first()
    if instructor:
        sectionID = request.POST.get("section_id_add")
        section = Sections.objects.filter(Id=sectionID).first()
        section.Instructors.add(instructor)


def create_account(first_name, last_name, email, password, phone, role):
    errors = {}
    if not first_name:
        errors['firstName'] = "First name cannot be empty."
    if not last_name:
        errors['lastName'] = "Last name cannot be empty."
    if not email:
        errors['email'] = "Email cannot be empty."
    if not password:
        errors['password'] = "Password cannot be empty."
    if not phone:
        errors['phone'] = "Phone number cannot be empty."
    if not phone.isdigit():
        errors['phone'] = "Phone number must contain only digits."
    if len(phone) != 10:
        errors['phone'] = "Phone number must be 9 digits."

    if errors:
        return JsonResponse({"errors": errors}, status=400)

    try:
        # Create a new user
        User.objects.create(
            FirstName=first_name,
            LastName=last_name,
            Email=email,
            Password=make_password(password),
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
        if check_password(password, user.Password):
            return user
        else:
            return False
    except User.DoesNotExist:
        return False


def update_account(request, instructor):
    """Helper method to update the instructor's account information."""
    instructor.FirstName = request.POST.get("firstName")
    instructor.LastName = request.POST.get("lastName")
    instructor.Email = request.POST.get("email")
    instructor.Phone = request.POST.get("phone")
    instructor.save()


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
                return JsonResponse(
                    {"message": "Account created successfully! Use back button to get back to dashboard."})
            case "create_course":
                title = request.POST.get("title")
                semester = request.POST.get("semester")
                year = request.POST.get("year")

                create_course(title, semester, year)
                return JsonResponse(
                    {"message": "Course created successfully! Use back button to get back to dashboard."})
            case _:
                return JsonResponse({"error": "Invalid action."}, status=400)


class Accounts(View):
    def get(self, request):
        AllAccounts = User.objects.all().values("FirstName", "LastName", "Email", "Phone", "Role", "Id")
        return render(request, "Accounts.html", {'accounts': AllAccounts})

    def post(self, request):
        action = request.POST.get("action")
        if action == "delete_account":
            account_id = request.POST.get("account_id")
            deleteAccount(account_id)
            return JsonResponse(
                {"message": "Account deleted successfully! Use back button to get back to All Accounts"})

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
                    return redirect('/adminDashboard/')
                case 'Instructor':
                    return redirect('instructor_dashboard', instructor_id=validUser.Id)
                case 'TA':
                    return redirect('TA_dashboard', TA_id=validUser.Id)
        else:
            return render(request, 'LoginPage.html')


# Instructor Dashboard
class InstructorDashboard(View):
    def get(self, request, instructor_id):
        instructor = User.objects.get(Id=instructor_id)
        return render(request, "InstructorDashboard.html", {'instructor': instructor})


class InstructorProfile(View):
    def get(self, request, instructor_id):
        instructor = User.objects.get(Id=instructor_id)
        return render(request, "InstructorProfile.html", {'instructor': instructor})

    def post(self, request, instructor_id):
        instructor = User.objects.get(Id=instructor_id)

        # Update the instructor's information
        instructor.FirstName = request.POST.get("firstName")
        instructor.LastName = request.POST.get("lastName")
        instructor.Email = request.POST.get("email")
        instructor.Phone = request.POST.get("phone")

        # Update password if provided
        new_password = request.POST.get("password")
        if new_password:
            instructor.Password = new_password

        instructor.save()

        return redirect('instructor_dashboard', instructor_id=instructor.Id)


class InstructorCourses(View):
    def get(self, request, instructor_id):
        from ScheduleAppData.models import Courses
        instructor = User.objects.get(Id=instructor_id)
        courses = Courses.objects.filter(sections__Instructors=instructor).distinct()
        return render(request, "InstructorCourses.html", {'courses': courses, 'instructor': instructor})

    def post(self, request, instructor_id):
        from ScheduleAppData.models import Courses
        action = request.POST.get("action")
        if action == "edit_course":
            course_id = request.POST.get("course_id")
            course_name = request.POST.get("course_name")

            course = Courses.objects.get(Id=course_id)
            course.CourseName = course_name
            course.save()

        return redirect('instructor_courses', instructor_id=instructor_id)


class TADashboard(View):
    def get(self, request, TA_id):
        from ScheduleAppData.models import Courses, Sections
        # Retrieve the instructor's account information
        TA = User.objects.get(pk=TA_id)

        # Retrieve all courses assigned to the instructor
        courses = Courses.objects.filter(sections__Instructors=TA).distinct()

        Sections = Sections.objects.filter(Instructors=TA)

        return render(request, 'TADashboard.html', {
            'TA': TA,
            'courses': courses,
            'sections': Sections
        })

    def post(self, request, TA_id):
        # Retrieve the instructor's account information
        TA = User.objects.get(pk=TA_id)

        if "update_account" in request.POST:
            update_account(request, TA)

        # Redirect to the same page to reflect changes
        return self.get(request, TA_id)


class CoursePage(View):
    def get(self, request, course_id):
        from ScheduleAppData.models import Courses
        # Retrieve the course using the course_id from the URL
        course = Courses.objects.get(Id=course_id)
        sections = Sections.objects.filter(CourseId=course)
        # Render the page with course, assignments, and sections
        return render(request, 'CoursePage.html', {
            'course': course,
            'sections': sections,
            'days':Days.choices
        })

    def post(self, request, course_id):
        from ScheduleAppData.models import Courses, Sections
        # Retrieve the course using the course_id from the URL
        course = Courses.objects.get(Id=course_id)

        if "add_section" in request.POST:
            add_section(request, course)
        elif "edit_section" in request.POST:
            edit_section(request)
        # Fetch updated assignments and sections after the POST operation
        sections = Sections.objects.filter(CourseId=course)

        # Re-render the page with updated data
        return render(request, 'CoursePage.html', {
            'course': course,
            'sections': sections,
            'days': Days.choices
        })


class AccountPage(View):
    def get(self, request, account_id):
        # Retrieve the account using the account_id
        account = User.objects.get(Id=account_id)
        return render(request, 'AccountPage.html', {'account': account})

    def post(self, request, account_id):
        # Retrieve the account using the account_id
        account = User.objects.get(Id=account_id)

        # Handle account updates (example: updating phone number)
        if "update_account" in request.POST:
            account.Phone = request.POST.get("phone")
            account.save()

        return render(request, 'AccountPage.html', {'account': account})
