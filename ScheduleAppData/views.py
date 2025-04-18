from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.db import IntegrityError

from ScheduleAppData.models import User, Courses


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