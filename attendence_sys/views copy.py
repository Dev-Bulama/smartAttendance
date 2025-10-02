from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import *
from .models import Student, Attendence, Faculty
from .filters import AttendenceFilter

# from django.views.decorators import gzip

from .recognizer import Recognizer
from datetime import date
import os

def landing(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'attendence_sys/landing.html')
def registerPage(request):
    """Combined Student and Lecturer registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    # Get user_type from GET or POST, default to lecturer
    user_type = request.GET.get('user_type', request.POST.get('user_type', 'lecturer'))
    
    if user_type == 'student':
        form = StudentRegistrationForm()
    else:
        form = LecturerRegistrationForm()
    
    if request.method == 'POST':
        user_type = request.POST.get('user_type', 'lecturer')
        
        if user_type == 'student':
            form = StudentRegistrationForm(request.POST, request.FILES)
            
            if form.is_valid():
                # Check if registration ID already exists
                reg_id = form.cleaned_data.get('registration_id')
                if Student.objects.filter(registration_id=reg_id).exists():
                    messages.error(request, f'Student with Registration ID {reg_id} already exists.')
                else:
                    # Create user
                    user = form.save()
                    
                    # Create Student profile
                    student = Student.objects.create(
                        user=user,
                        firstname=form.cleaned_data.get('firstname'),
                        lastname=form.cleaned_data.get('lastname'),
                        email=form.cleaned_data.get('email'),
                        phone=form.cleaned_data.get('phone'),
                        registration_id=reg_id,
                        branch=form.cleaned_data.get('branch'),
                        year=form.cleaned_data.get('year'),
                        section=form.cleaned_data.get('section'),
                        profile_pic=form.cleaned_data.get('profile_pic')
                    )
                    
                    username = form.cleaned_data.get('username')
                    messages.success(request, f'Student account created successfully for {username}! You can now login.')
                    return redirect('login')
            else:
                # Show form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
        
        else:  # Lecturer registration
            form = LecturerRegistrationForm(request.POST, request.FILES)
            
            if form.is_valid():
                # Create user
                user = form.save()
                
                # Create Faculty profile
                faculty = Faculty.objects.create(
                    user=user,
                    firstname=form.cleaned_data.get('firstname'),
                    lastname=form.cleaned_data.get('lastname'),
                    email=form.cleaned_data.get('email'),
                    phone=form.cleaned_data.get('phone'),
                    profile_pic=form.cleaned_data.get('profile_pic')
                )
                
                username = form.cleaned_data.get('username')
                messages.success(request, f'Lecturer account created successfully for {username}! You can now login.')
                return redirect('login')
            else:
                # Show form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
    
    context = {
        'form': form,
        'user_type': user_type
    }
    return render(request, 'attendence_sys/register.html', context)

# def registerPage(request):
#     """Lecturer registration view"""
#     if request.user.is_authenticated:
#         return redirect('home')
    
#     form = LecturerRegistrationForm()
    
#     if request.method == 'POST':
#         form = LecturerRegistrationForm(request.POST, request.FILES)
        
#         if form.is_valid():
#             # Create user
#             user = form.save()
            
#             # Create Faculty profile
#             faculty = Faculty.objects.create(
#                 user=user,
#                 firstname=form.cleaned_data.get('firstname'),
#                 lastname=form.cleaned_data.get('lastname'),
#                 email=form.cleaned_data.get('email'),
#                 phone=form.cleaned_data.get('phone'),
#                 profile_pic=form.cleaned_data.get('profile_pic')
#             )
            
#             username = form.cleaned_data.get('username')
#             messages.success(request, f'Account created successfully for {username}! You can now login.')
#             return redirect('login')
#         else:
#             # Show form errors
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f'{field}: {error}')
    
#     context = {'form': form}
#     return render(request, 'attendence_sys/register.html', context)
@login_required(login_url='login')
def home(request):
    """Legacy home redirect - redirects to appropriate dashboard"""
    try:
        faculty = Faculty.objects.get(user=request.user)
        return redirect('lecturer_dashboard')
    except Faculty.DoesNotExist:
        try:
            student = Student.objects.get(user=request.user)
            return redirect('student_dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'No profile found for your account.')
            return redirect('login')


@login_required(login_url='login')
def lecturer_dashboard(request):
    """Lecturer Dashboard with modern UI"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    studentForm = CreateStudentForm()

    if request.method == 'POST':
        studentForm = CreateStudentForm(data=request.POST, files=request.FILES)
        stat = False 
        try:
            student = Student.objects.get(registration_id=request.POST['registration_id'])
            stat = True
        except:
            stat = False
        if studentForm.is_valid() and (stat == False):
            studentForm.save()
            name = studentForm.cleaned_data.get('firstname') + " " + studentForm.cleaned_data.get('lastname')
            messages.success(request, 'Student ' + name + ' was successfully added.')
            return redirect('lecturer_dashboard')
        else:
            messages.error(request, 'Student with Registration Id ' + request.POST['registration_id'] + ' already exists.')
            return redirect('lecturer_dashboard')

    # Get statistics for dashboard
    total_students = Student.objects.all().count()
    today_attendance = Attendence.objects.filter(date=str(date.today())).count()
    total_attendance_records = Attendence.objects.all().count()
    
    context = {
        'studentForm': studentForm,
        'faculty': faculty,
        'total_students': total_students,
        'today_attendance': today_attendance,
        'total_attendance_records': total_attendance_records,
    }
    return render(request, 'attendence_sys/lecturer_dashboard.html', context)


@login_required(login_url='login')
def student_dashboard(request):
    """Student Dashboard with attendance overview"""
    try:
        student = request.user.student
    except:
        messages.error(request, 'You do not have student access.')
        return redirect('login')
    
    # Get student's attendance records
    my_attendance = Attendence.objects.filter(Student_ID=student.registration_id).order_by('-date')
    
    # Calculate attendance statistics
    total_classes = my_attendance.count()
    present_count = my_attendance.filter(status='Present').count()
    absent_count = my_attendance.filter(status='Absent').count()
    
    if total_classes > 0:
        attendance_percentage = round((present_count / total_classes) * 100, 2)
    else:
        attendance_percentage = 0
    
    # Get recent attendance (last 10 records)
    recent_attendance = my_attendance[:10]
    
    context = {
        'student': student,
        'total_classes': total_classes,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': attendance_percentage,
        'recent_attendance': recent_attendance,
    }
    return render(request, 'attendence_sys/student_dashboard.html', context)

# @login_required(login_url='login')
@login_required(login_url='login')
def student_mark_attendance(request):
    """Allow students to mark their own attendance via face recognition"""
    try:
        student = request.user.student
    except:
        messages.error(request, 'You do not have student access.')
        return redirect('login')
    
    if request.method == 'POST':
        period = request.POST.get('period')
        face_verified = request.POST.get('face_verified')
        
        if not period:
            messages.error(request, 'Please select a period.')
            return redirect('student_mark_attendance')
        
        # Check if attendance already marked for today and this period
        existing_attendance = Attendence.objects.filter(
            Student_ID=student.registration_id,
            date=str(date.today()),
            period=period
        )
        
        if existing_attendance.exists():
            messages.warning(request, f'Attendance for Period {period} has already been marked today.')
            return redirect('student_dashboard')
        
        # Check if face was verified (from JavaScript)
        if face_verified == 'true':
            # Mark attendance as Present
            attendance = Attendence.objects.create(
                Faculty_Name='Self-Service (Face Verified)',
                Student_ID=student.registration_id,
                period=period,
                branch=student.branch,
                year=student.year,
                section=student.section,
                status='Present'
            )
            messages.success(request, f'✅ Attendance marked successfully for Period {period}!')
            return redirect('student_dashboard')
        else:
            messages.error(request, '❌ Face verification failed. Please try again.')
            return redirect('student_mark_attendance')
    
    context = {
        'student': student,
        'has_profile_pic': bool(student.profile_pic)
    }
    return render(request, 'attendence_sys/student_mark_attendance.html', context)
# def student_mark_attendance(request):
#     """Allow students to mark their own attendance via face recognition"""
#     try:
#         student = request.user.student
#     except:
#         messages.error(request, 'You do not have student access.')
#         return redirect('login')
    
#     if request.method == 'POST':
#         period = request.POST.get('period')
        
#         if not period:
#             messages.error(request, 'Please select a period.')
#             return redirect('student_dashboard')
        
#         # Check if attendance already marked for today and this period
#         existing_attendance = Attendence.objects.filter(
#             Student_ID=student.registration_id,
#             date=str(date.today()),
#             period=period
#         )
        
#         if existing_attendance.exists():
#             messages.warning(request, f'Attendance for Period {period} has already been marked today.')
#             return redirect('student_dashboard')
        
#         # Check if student has profile picture for verification
#         if not student.profile_pic:
#             messages.error(request, 'You need to upload a profile picture before using facial recognition. Please contact your administrator.')
#             return redirect('student_dashboard')
        
#         # Prepare details for face recognition
#         details = {
#             'branch': student.branch,
#             'year': student.year,
#             'section': student.section,
#         }
        
#         try:
#             # Run face recognizer for the entire class
#             import cv2
#             import face_recognition
#             import numpy as np
            
#             # Load student's registered face
#             base_dir = os.getcwd()
#             image_path = os.path.join(base_dir, student.profile_pic.url.replace('/images/', 'static/images/'))
            
#             if not os.path.exists(image_path):
#                 messages.error(request, 'Profile picture file not found. Please re-upload your profile picture.')
#                 return redirect('student_dashboard')
            
#             # Load and encode the registered face
#             registered_image = face_recognition.load_image_file(image_path)
#             registered_encodings = face_recognition.face_encodings(registered_image)
            
#             if len(registered_encodings) == 0:
#                 messages.error(request, 'Could not detect a face in your profile picture. Please upload a clear face photo.')
#                 return redirect('student_dashboard')
            
#             registered_encoding = registered_encodings[0]
            
#             # Open camera for live verification
#             video = cv2.VideoCapture(0)
#             face_detected = False
#             attempts = 0
#             max_attempts = 100  # Process up to 100 frames
            
#             messages.info(request, 'Camera opened! Position your face clearly and wait for recognition...')
            
#             while attempts < max_attempts:
#                 check, frame = video.read()
#                 if not check:
#                     break
                
#                 attempts += 1
                
#                 # Resize frame for faster processing
#                 small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
#                 rgb_small_frame = small_frame[:, :, ::-1]
                
#                 # Find faces in frame
#                 face_locations = face_recognition.face_locations(rgb_small_frame)
                
#                 if len(face_locations) > 0:
#                     # Encode faces found in frame
#                     face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                    
#                     for face_encoding in face_encodings:
#                         # Compare with registered face
#                         matches = face_recognition.compare_faces([registered_encoding], face_encoding, tolerance=0.6)
                        
#                         if matches[0]:
#                             face_detected = True
                            
#                             # Draw rectangle around face
#                             for (top, right, bottom, left) in face_locations:
#                                 top *= 2
#                                 right *= 2
#                                 bottom *= 2
#                                 left *= 2
#                                 cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
#                                 cv2.putText(frame, f"{student.firstname}", (left, top - 10), 
#                                           cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 0), 2)
                            
#                             cv2.imshow("Attendance - Face Recognized! Press 'S' to confirm", frame)
                            
#                             # Wait for 'S' key to confirm
#                             if cv2.waitKey(1) == ord('s'):
#                                 video.release()
#                                 cv2.destroyAllWindows()
                                
#                                 # Mark attendance
#                                 attendance = Attendence.objects.create(
#                                     Faculty_Name='Self-Service',
#                                     Student_ID=student.registration_id,
#                                     period=period,
#                                     branch=student.branch,
#                                     year=student.year,
#                                     section=student.section,
#                                     status='Present'
#                                 )
#                                 messages.success(request, f'✅ Attendance marked successfully for Period {period}!')
#                                 return redirect('student_dashboard')
#                             break
                
#                 # Show frame
#                 if not face_detected:
#                     cv2.imshow("Attendance - Looking for your face...", frame)
                
#                 if cv2.waitKey(1) == ord('q'):
#                     break
            
#             video.release()
#             cv2.destroyAllWindows()
            
#             if not face_detected:
#                 messages.error(request, '❌ Face not recognized. Please ensure good lighting and try again.')
            
#         except ImportError as e:
#             messages.error(request, f'Required libraries not available: {str(e)}')
#         except Exception as e:
#             messages.error(request, f'Error during face recognition: {str(e)}. Please try again.')
        
#         return redirect('student_dashboard')
    
#     context = {'student': student}
#     return render(request, 'attendence_sys/student_mark_attendance.html', context)
# def student_mark_attendance(request):
#     """Allow students to mark their own attendance via face recognition"""
#     try:
#         student = request.user.student
#     except:
#         messages.error(request, 'You do not have student access.')
#         return redirect('login')
    
#     if request.method == 'POST':
#         period = request.POST.get('period')
        
#         if not period:
#             messages.error(request, 'Please select a period.')
#             return redirect('student_dashboard')
        
#         # Check if attendance already marked for today and this period
#         existing_attendance = Attendence.objects.filter(
#             Student_ID=student.registration_id,
#             date=str(date.today()),
#             period=period
#         )
        
#         if existing_attendance.exists():
#             messages.warning(request, f'Attendance for Period {period} has already been marked today.')
#             return redirect('student_dashboard')
        
#         # Prepare details for face recognition
#         details = {
#             'branch': student.branch,
#             'year': student.year,
#             'section': student.section,
#             'student_id': student.registration_id
#         }
        
#         try:
#             # Run face recognizer
#             recognized_students = Recognizer(details)
            
#             # Check if this student was recognized
#             if student.registration_id in recognized_students:
#                 # Mark attendance as Present
#                 attendance = Attendence.objects.create(
#                     Faculty_Name='Self-Service',
#                     Student_ID=student.registration_id,
#                     period=period,
#                     branch=student.branch,
#                     year=student.year,
#                     section=student.section,
#                     status='Present'
#                 )
#                 messages.success(request, f'✅ Attendance marked successfully for Period {period}!')
#             else:
#                 # Face not recognized, mark as attempt but don't mark present
#                 messages.error(request, '❌ Face not recognized. Please ensure proper lighting and face the camera directly.')
#         except Exception as e:
#             messages.error(request, f'Error during face recognition: {str(e)}. Please try again.')
        
#         return redirect('student_dashboard')
    
#     context = {'student': student}
#     return render(request, 'attendence_sys/student_mark_attendance.html', context)
# ==================== COURSE MANAGEMENT VIEWS ====================

@login_required(login_url='login')
def manage_courses(request):
    """View and manage all courses for lecturer"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    # Get courses taught by this lecturer
    my_courses = Course.objects.filter(lecturer=faculty)
    
    # Get all courses (for admin/reference)
    all_courses = Course.objects.all()
    
    context = {
        'my_courses': my_courses,
        'all_courses': all_courses,
        'faculty': faculty,
    }
    return render(request, 'attendence_sys/manage_courses.html', context)


@login_required(login_url='login')
def add_course(request):
    """Add a new course"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    form = CourseForm()
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        
        if form.is_valid():
            course = form.save(commit=False)
            # Automatically assign current lecturer if not specified
            if not course.lecturer:
                course.lecturer = faculty
            course.save()
            
            messages.success(request, f'Course "{course.course_name}" added successfully!')
            return redirect('manage_courses')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    context = {
        'form': form,
        'faculty': faculty,
    }
    return render(request, 'attendence_sys/add_course.html', context)


@login_required(login_url='login')
def edit_course(request, course_id):
    """Edit an existing course"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        messages.error(request, 'Course not found.')
        return redirect('manage_courses')
    
    form = CourseForm(instance=course)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.course_name}" updated successfully!')
            return redirect('manage_courses')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    context = {
        'form': form,
        'course': course,
        'faculty': faculty,
    }
    return render(request, 'attendence_sys/edit_course.html', context)


@login_required(login_url='login')
def delete_course(request, course_id):
    """Delete a course"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    try:
        course = Course.objects.get(id=course_id)
        course_name = course.course_name
        course.delete()
        messages.success(request, f'Course "{course_name}" deleted successfully!')
    except Course.DoesNotExist:
        messages.error(request, 'Course not found.')
    
    return redirect('manage_courses')


# ==================== SESSION MANAGEMENT VIEWS ====================

@login_required(login_url='login')
def manage_sessions(request):
    """View and manage all sessions for lecturer"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    # Get sessions for this lecturer
    my_sessions = Session.objects.filter(lecturer=faculty).select_related('course')
    
    # Separate upcoming and past sessions
    from datetime import date as date_module
    today = date_module.today()
    
    upcoming_sessions = my_sessions.filter(date__gte=today, status='Scheduled').order_by('date', 'period')
    past_sessions = my_sessions.filter(date__lt=today).order_by('-date', 'period')
    
    context = {
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
        'faculty': faculty,
    }
    return render(request, 'attendence_sys/manage_sessions.html', context)


@login_required(login_url='login')
def add_session(request):
    """Add a new session"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    form = SessionForm(lecturer=faculty)
    
    if request.method == 'POST':
        form = SessionForm(request.POST, lecturer=faculty)
        
        if form.is_valid():
            session = form.save(commit=False)
            session.lecturer = faculty
            
            try:
                session.save()
                messages.success(request, f'Session for "{session.course.course_name}" added successfully!')
                return redirect('manage_sessions')
            except Exception as e:
                messages.error(request, f'Error: A session already exists for this course, date, and period.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    context = {
        'form': form,
        'faculty': faculty,
    }
    return render(request, 'attendence_sys/add_session.html', context)


@login_required(login_url='login')
def edit_session(request, session_id):
    """Edit an existing session"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        messages.error(request, 'Session not found.')
        return redirect('manage_sessions')
    
    form = SessionForm(instance=session, lecturer=faculty)
    
    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session, lecturer=faculty)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Session updated successfully!')
            return redirect('manage_sessions')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    context = {
        'form': form,
        'session': session,
        'faculty': faculty,
    }
    return render(request, 'attendence_sys/edit_session.html', context)


@login_required(login_url='login')
def delete_session(request, session_id):
    """Delete a session"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    try:
        session = Session.objects.get(id=session_id)
        session_info = f"{session.course.course_name} - {session.date}"
        session.delete()
        messages.success(request, f'Session "{session_info}" deleted successfully!')
    except Session.DoesNotExist:
        messages.error(request, 'Session not found.')
    
    return redirect('manage_sessions')
# ==================== GRADE MANAGEMENT VIEWS ====================

@login_required(login_url='login')
def manage_grades(request):
    """View and manage all grades for lecturer"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    # Get courses taught by this lecturer
    my_courses = Course.objects.filter(lecturer=faculty)
    
    # Get all grades for lecturer's courses
    my_grades = Grade.objects.filter(lecturer=faculty).select_related('student', 'course')
    
    # Filter by course if specified
    selected_course = request.GET.get('course')
    if selected_course:
        my_grades = my_grades.filter(course_id=selected_course)
    
    # Filter by semester if specified
    selected_semester = request.GET.get('semester')
    if selected_semester:
        my_grades = my_grades.filter(semester=selected_semester)
    
    context = {
        'my_grades': my_grades,
        'my_courses': my_courses,
        'selected_course': selected_course,
        'selected_semester': selected_semester,
        'faculty': faculty,
    }
    return render(request, 'attendence_sys/manage_grades.html', context)


@login_required(login_url='login')
def add_grade(request):
    """Add a single grade for a student"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    form = GradeForm(lecturer=faculty)
    
    if request.method == 'POST':
        form = GradeForm(request.POST, lecturer=faculty)
        
        if form.is_valid():
            try:
                grade = form.save(commit=False)
                grade.lecturer = faculty
                grade.save()
                
                student = grade.student
                course = grade.course
                messages.success(request, f'Grade added for {student.firstname} {student.lastname} in {course.course_name}!')
                return redirect('manage_grades')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}. This grade entry might already exist.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    context = {
        'form': form,
        'faculty': faculty,
    }
    return render(request, 'attendence_sys/add_grade.html', context)


@login_required(login_url='login')
def bulk_grade_entry(request):
    """Bulk grade entry for a course"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    form = BulkGradeForm(lecturer=faculty)
    students = []
    course = None
    
    if request.method == 'POST':
        # Check if it's the initial form submission or grade submission
        if 'load_students' in request.POST:
            form = BulkGradeForm(request.POST, lecturer=faculty)
            
            if form.is_valid():
                course = form.cleaned_data['course']
                
                # Get all students in this course
                students = Student.objects.filter(
                    branch=course.branch,
                    year=course.year,
                    section=course.section
                )
                
                if not students.exists():
                    messages.warning(request, 'No students found for this course.')
        
        elif 'submit_grades' in request.POST:
            # Process submitted grades
            course_id = request.POST.get('course_id')
            assessment_type = request.POST.get('assessment_type')
            assessment_name = request.POST.get('assessment_name')
            max_marks = request.POST.get('max_marks')
            semester = request.POST.get('semester')
            academic_year = request.POST.get('academic_year')
            
            try:
                course = Course.objects.get(id=course_id)
                grades_added = 0
                
                students = Student.objects.filter(
                    branch=course.branch,
                    year=course.year,
                    section=course.section
                )
                
                for student in students:
                    marks_key = f'marks_{student.id}'
                    marks_obtained = request.POST.get(marks_key)
                    
                    if marks_obtained and marks_obtained.strip():
                        try:
                            # Check if grade already exists
                            existing_grade = Grade.objects.filter(
                                student=student,
                                course=course,
                                assessment_type=assessment_type,
                                assessment_name=assessment_name,
                                semester=semester,
                                academic_year=academic_year
                            ).first()
                            
                            if existing_grade:
                                # Update existing grade
                                existing_grade.marks_obtained = float(marks_obtained)
                                existing_grade.max_marks = float(max_marks)
                                existing_grade.save()
                            else:
                                # Create new grade
                                Grade.objects.create(
                                    student=student,
                                    course=course,
                                    lecturer=faculty,
                                    assessment_type=assessment_type,
                                    assessment_name=assessment_name,
                                    marks_obtained=float(marks_obtained),
                                    max_marks=float(max_marks),
                                    semester=semester,
                                    academic_year=academic_year
                                )
                            grades_added += 1
                        except Exception as e:
                            messages.error(request, f'Error adding grade for {student.registration_id}: {str(e)}')
                
                if grades_added > 0:
                    messages.success(request, f'Successfully added/updated {grades_added} grades!')
                    return redirect('manage_grades')
                else:
                    messages.warning(request, 'No grades were entered.')
                    
            except Course.DoesNotExist:
                messages.error(request, 'Course not found.')
    
    context = {
        'form': form,
        'students': students,
        'course': course,
        'faculty': faculty,
    }
    return render(request, 'attendence_sys/bulk_grade_entry.html', context)


@login_required(login_url='login')
def edit_grade(request, grade_id):
    """Edit an existing grade"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    try:
        grade = Grade.objects.get(id=grade_id, lecturer=faculty)
    except Grade.DoesNotExist:
        messages.error(request, 'Grade not found or you do not have permission to edit it.')
        return redirect('manage_grades')
    
    form = GradeForm(instance=grade, lecturer=faculty)
    
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade, lecturer=faculty)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade updated successfully!')
            return redirect('manage_grades')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    context = {
        'form': form,
        'grade': grade,
        'faculty': faculty,
    }
    return render(request, 'attendence_sys/edit_grade.html', context)


@login_required(login_url='login')
def delete_grade(request, grade_id):
    """Delete a grade"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    try:
        grade = Grade.objects.get(id=grade_id, lecturer=faculty)
        grade_info = f"{grade.student.registration_id} - {grade.course.course_code} - {grade.assessment_type}"
        grade.delete()
        messages.success(request, f'Grade "{grade_info}" deleted successfully!')
    except Grade.DoesNotExist:
        messages.error(request, 'Grade not found or you do not have permission to delete it.')
    
    return redirect('manage_grades')


@login_required(login_url='login')
def course_gradebook(request, course_id):
    """View gradebook for a specific course"""
    try:
        faculty = request.user.faculty
    except:
        messages.error(request, 'You do not have lecturer access.')
        return redirect('login')
    
    try:
        course = Course.objects.get(id=course_id, lecturer=faculty)
    except Course.DoesNotExist:
        messages.error(request, 'Course not found or you do not have permission to view it.')
        return redirect('manage_grades')
    
    # Get all students in this course
    students = Student.objects.filter(
        branch=course.branch,
        year=course.year,
        section=course.section
    )
    
    # Get selected semester and year from query params
    semester = request.GET.get('semester', 'Fall')
    academic_year = request.GET.get('academic_year', '2024-2025')
    
    # Prepare gradebook data
    gradebook_data = []
    
    for student in students:
        student_grades = Grade.objects.filter(
            student=student,
            course=course,
            semester=semester,
            academic_year=academic_year
        )
        
        # Organize grades by assessment type
        grades_dict = {
            'student': student,
            'quiz': student_grades.filter(assessment_type='Quiz'),
            'assignment': student_grades.filter(assessment_type='Assignment'),
            'midterm': student_grades.filter(assessment_type='Midterm').first(),
            'final': student_grades.filter(assessment_type='Final').first(),
            'project': student_grades.filter(assessment_type='Project'),
        }
        
        # Calculate average percentage
        total_percentage = 0
        count = 0
        for grade in student_grades:
            total_percentage += float(grade.percentage)
            count += 1
        
        grades_dict['average'] = round(total_percentage / count, 2) if count > 0 else 0
        grades_dict['total_assessments'] = count
        
        gradebook_data.append(grades_dict)
    
    context = {
        'course': course,
        'gradebook_data': gradebook_data,
        'semester': semester,
        'academic_year': academic_year,
        'faculty': faculty,
    }
    return render(request, 'attendence_sys/course_gradebook.html', context)
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Check if user is a student or faculty
            try:
                # Try to get Faculty profile
                faculty = Faculty.objects.get(user=user)
                return redirect('lecturer_dashboard')
            except Faculty.DoesNotExist:
                try:
                    # Try to get Student profile
                    student = Student.objects.get(user=user)
                    return redirect('student_dashboard')
                except Student.DoesNotExist:
                    # User has no profile, redirect to home
                    messages.warning(request, 'Your account is not properly configured. Please contact admin.')
                    return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {}
    return render(request, 'attendence_sys/login.html', context)

@login_required(login_url = 'login')
def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url = 'login')
def updateStudentRedirect(request):
    context = {}
    if request.method == 'POST':
        try:
            reg_id = request.POST['reg_id']
            branch = request.POST['branch']
            student = Student.objects.get(registration_id = reg_id, branch = branch)
            updateStudentForm = CreateStudentForm(instance=student)
            context = {'form':updateStudentForm, 'prev_reg_id':reg_id, 'student':student}
        except:
            messages.error(request, 'Student Not Found')
            return redirect('home')
    return render(request, 'attendence_sys/student_update.html', context)

@login_required(login_url = 'login')
def updateStudent(request):
    if request.method == 'POST':
        context = {}
        try:
            student = Student.objects.get(registration_id = request.POST['prev_reg_id'])
            updateStudentForm = CreateStudentForm(data = request.POST, files=request.FILES, instance = student)
            if updateStudentForm.is_valid():
                updateStudentForm.save()
                messages.success(request, 'Updation Success')
                return redirect('home')
        except:
            messages.error(request, 'Updation Unsucessfull')
            return redirect('home')
    return render(request, 'attendence_sys/student_update.html', context)


@login_required(login_url = 'login')
def takeAttendence(request):
    if request.method == 'POST':
        details = {
            'branch':request.POST['branch'],
            'year': request.POST['year'],
            'section':request.POST['section'],
            'period':request.POST['period'],
            # 'faculty':request.user.faculty
            }
        if Attendence.objects.filter(date = str(date.today()),branch = details['branch'], year = details['year'], section = details['section'],period = details['period']).count() != 0 :
            messages.error(request, "Attendence already recorded.")
            return redirect('home')
        else:
            students = Student.objects.filter(branch = details['branch'], year = details['year'], section = details['section'])
            names = Recognizer(details)
            for student in students:
                if str(student.registration_id) in names:
                    attendence = Attendence(Faculty_Name = request.user.faculty, 
                    Student_ID = str(student.registration_id), 
                    period = details['period'], 
                    branch = details['branch'], 
                    year = details['year'], 
                    section = details['section'],
                    status = 'Present')
                    attendence.save()
                else:
                    attendence = Attendence(Faculty_Name = request.user.faculty, 
                    Student_ID = str(student.registration_id), 
                    period = details['period'],
                    branch = details['branch'], 
                    year = details['year'], 
                    section = details['section'])
                    attendence.save()
            attendences = Attendence.objects.filter(date = str(date.today()),branch = details['branch'], year = details['year'], section = details['section'],period = details['period'])
            context = {"attendences":attendences, "ta":True}
            messages.success(request, "Attendence taking Success")
            return render(request, 'attendence_sys/attendence.html', context)        
    context = {}
    return render(request, 'attendence_sys/home.html', context)

def searchAttendence(request):
    attendences = Attendence.objects.all()
    myFilter = AttendenceFilter(request.GET, queryset=attendences)
    attendences = myFilter.qs
    context = {'myFilter':myFilter, 'attendences': attendences, 'ta':False}
    return render(request, 'attendence_sys/attendence.html', context)


def facultyProfile(request):
    faculty = request.user.faculty
    form = FacultyForm(instance = faculty)
    context = {'form':form}
    return render(request, 'attendence_sys/facultyForm.html', context)



# class VideoCamera(object):
#     def __init__(self):
#         self.video = cv2.VideoCapture(0)
#     def __del__(self):
#         self.video.release()

#     def get_frame(self):
#         ret,image = self.video.read()
#         ret,jpeg = cv2.imencode('.jpg',image)
#         return jpeg.tobytes()


# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield(b'--frame\r\n'
#         b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# @gzip.gzip_page
# def videoFeed(request):
#     try:
#         return StreamingHttpResponse(gen(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
#     except:
#         print("aborted")

# def getVideo(request):
#     return render(request, 'attendence_sys/videoFeed.html')