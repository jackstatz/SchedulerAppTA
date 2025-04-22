"""
URL configuration for ScheduleApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from ScheduleAppData.views import AdminDashboard, Accounts, Courses, InstructorDashboard, InstructorProfile, \
    InstructorCourses, InstructorLabAssignments, InstructorAssignments, Login, TADashboard, AccountPage, CoursePage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Login.as_view()),
    path('adminDashboard/', AdminDashboard.as_view()),
    path('accounts/', Accounts.as_view()),
    path('courses/', Courses.as_view()),
    path('course/<int:course_id>/', CoursePage.as_view(), name='course_page'),
    path('account/<int:account_id>/', AccountPage.as_view(), name='account_page'),
    path('instructor/<int:instructor_id>/', InstructorDashboard.as_view(), name='instructor_dashboard'),
    path('instrcutor/profile/<int:instructor_id>/', InstructorProfile.as_view(), name='instructor_profile'),
    path('instrcutor/courses/<int:instructor_id>/', InstructorCourses.as_view(), name='instructor_courses'),
    path('instrcutor/lab-assignments/<int:instructor_id>/', InstructorLabAssignments.as_view(), name='instructor_lab_assignments'),
    path('instrcutor/assignments/<int:instructor_id>/', InstructorAssignments.as_view(), name='instructor_assignments'),
    path('TADashboard/', TADashboard.as_view()),path('TADashboard/<int:TA_id>/', TADashboard.as_view(), name='TA_dashboard'),

]
