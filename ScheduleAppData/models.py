from datetime import time

from django.db import models

class Days(models.TextChoices):
    Sunday="U"
    Monday="M"
    Tuesday="T"
    Wednesday="W"
    Thursday="R"
    Friday="F"
    Saturday="S"

# Create your models here.
class User(models.Model):
    ## Creating a role enumeration
    class Role(models.TextChoices):
        Supervisor = "Supervisor"
        Instructor = "Instructor"
        TA = "TA"
    Id = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=120)
    LastName = models.CharField(max_length=120)
    Email = models.CharField(max_length=120)
    Password = models.CharField(max_length=120)
    Phone = models.CharField(max_length=120)
    Role = models.CharField(choices=Role.choices, max_length=20)

class Courses(models.Model):
    Id = models.AutoField(primary_key=True)
    CourseName = models.CharField(max_length=120)
    Semester = models.CharField(max_length=120)
    Year = models.IntegerField()

class Sections(models.Model):
    class SectionType(models.TextChoices):
        Lab = "Lab"
        Lecture = "Lecture"
    Id = models.AutoField(primary_key=True)
    ## The ID of the course this section is a part of
    CourseId = models.ForeignKey(Courses, on_delete=models.CASCADE)
    SectionNum = models.CharField(max_length=120)
    ScheduledDays = models.CharField(
        max_length=20,  # Adjust length based on the number of days
        choices=Days.choices,
        blank=True,
        help_text="Comma-separated list of scheduled days (e.g., M,T,W).")
    ScheduledStartTime = models.TimeField(default=time(9,0))
    ScheduledEndTime = models.TimeField(default=time(10,0))
    SectionType = models.CharField(choices=SectionType.choices, max_length=20)
    ## The User ID of the instructor for this section
    Instructors = models.ManyToManyField(User)