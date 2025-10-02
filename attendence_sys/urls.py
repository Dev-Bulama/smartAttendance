from django.urls import path

from . import views

urlpatterns = [
    # Landing & Authentication
    path('', views.landing, name='landing'),
    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    
    # Dashboards
  # Dashboards
    path('home/', views.home, name='home'),
    path('lecturer/dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/mark-attendance/', views.student_mark_attendance, name='student_mark_attendance'),
    
    # Lecturer Features
    path('searchattendence/', views.searchAttendence, name='searchattendence'),
    path('account/', views.facultyProfile, name='account'),
    path('updateStudentRedirect/', views.updateStudentRedirect, name='updateStudentRedirect'),
    path('updateStudent/', views.updateStudent, name='updateStudent'),
    path('attendence/', views.takeAttendence, name='attendence'),
    # Course Management
    path('courses/', views.manage_courses, name='manage_courses'),
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    
    # Session Management
    path('sessions/', views.manage_sessions, name='manage_sessions'),
    path('sessions/add/', views.add_session, name='add_session'),
    path('sessions/edit/<int:session_id>/', views.edit_session, name='edit_session'),
    path('sessions/delete/<int:session_id>/', views.delete_session, name='delete_session'),
    # Grade Management
    path('grades/', views.manage_grades, name='manage_grades'),
    path('grades/add/', views.add_grade, name='add_grade'),
    path('grades/bulk/', views.bulk_grade_entry, name='bulk_grade_entry'),
    path('grades/edit/<int:grade_id>/', views.edit_grade, name='edit_grade'),
    path('grades/delete/<int:grade_id>/', views.delete_grade, name='delete_grade'),
    path('grades/gradebook/<int:course_id>/', views.course_gradebook, name='course_gradebook'),
    # Student Grades Views
    path('student/grades/', views.student_grades, name='student_grades'),
    path('student/transcript/', views.student_transcript, name='student_transcript'),
    # Commented out video features
    # path('video_feed/', views.videoFeed, name='video_feed'),
    # path('videoFeed/', views.getVideo, name='videoFeed'),
]