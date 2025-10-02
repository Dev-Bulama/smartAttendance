from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Faculty)
admin.site.register(Student)
admin.site.register(Attendence)
admin.site.register(Course)
admin.site.register(Session)
admin.site.register(Grade)
admin.site.register(CourseGrade)