from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import *

class CreateStudentForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(CreateStudentForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    
class FacultyForm(ModelForm):
    class Meta:
        model = Faculty
        fields = '__all__'
        exclude = ['user']
    def __init__(self, *args, **kwargs):
        super(FacultyForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class LecturerRegistrationForm(UserCreationForm):
    firstname = forms.CharField(
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    lastname = forms.CharField(
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        max_length=200, 
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    phone = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    profile_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(LecturerRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
class StudentRegistrationForm(UserCreationForm):
    firstname = forms.CharField(
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    lastname = forms.CharField(
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        max_length=200, 
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    phone = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    registration_id = forms.CharField(
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registration/student ID'
        })
    )
    branch = forms.ChoiceField(
        choices=[
            ('', 'Select Branch'),
            ('CSE', 'CSE'),
            ('IT', 'IT'),
            ('ECE', 'ECE'),
            ('CHEM', 'CHEM'),
            ('MECH', 'MECH'),
            ('EEE', 'EEE'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    year = forms.ChoiceField(
        choices=[
            ('', 'Select Year'),
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    section = forms.ChoiceField(
        choices=[
            ('', 'Select Section'),
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    profile_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(StudentRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['course_name', 'course_code', 'credits', 'branch', 'year', 'section', 'lecturer', 'description']
        widgets = {
            'course_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Data Structures and Algorithms'
            }),
            'course_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CS201'
            }),
            'credits': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 3'
            }),
            'branch': forms.Select(attrs={
                'class': 'form-control'
            }),
            'year': forms.Select(attrs={
                'class': 'form-control'
            }),
            'section': forms.Select(attrs={
                'class': 'form-control'
            }),
            'lecturer': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the course (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        # Make lecturer field show full name
        self.fields['lecturer'].queryset = Faculty.objects.all()
        self.fields['lecturer'].label_from_instance = lambda obj: f"{obj.firstname} {obj.lastname}"


class SessionForm(ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    class Meta:
        model = Session
        fields = ['course', 'date', 'period', 'topic', 'description', 'status']
        widgets = {
            'course': forms.Select(attrs={
                'class': 'form-control'
            }),
            'period': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', 'Select Period'),
                ('1', 'Period 1'),
                ('2', 'Period 2'),
                ('3', 'Period 3'),
                ('4', 'Period 4'),
                ('5', 'Period 5'),
                ('6', 'Period 6'),
                ('7', 'Period 7'),
            ]),
            'topic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Introduction to Linked Lists'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Session details (optional)'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        lecturer = kwargs.pop('lecturer', None)
        super(SessionForm, self).__init__(*args, **kwargs)
        
        # Filter courses by lecturer
        if lecturer:
            self.fields['course'].queryset = Course.objects.filter(lecturer=lecturer)
        
        # Set default status to Scheduled
        if not self.instance.pk:
            self.initial['status'] = 'Scheduled'
class GradeForm(ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'course', 'assessment_type', 'assessment_name', 
                  'marks_obtained', 'max_marks', 'semester', 'academic_year', 'remarks']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control'
            }),
            'course': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assessment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assessment_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Quiz 1, Assignment 2'
            }),
            'marks_obtained': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 85',
                'step': '0.01'
            }),
            'max_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 100',
                'step': '0.01'
            }),
            'semester': forms.Select(attrs={
                'class': 'form-control'
            }),
            'academic_year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2024-2025'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional remarks'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        lecturer = kwargs.pop('lecturer', None)
        course = kwargs.pop('course', None)
        super(GradeForm, self).__init__(*args, **kwargs)
        
        # Filter courses by lecturer
        if lecturer:
            self.fields['course'].queryset = Course.objects.filter(lecturer=lecturer)
        
        # If course is pre-selected, filter students by course branch/year/section
        if course:
            self.fields['student'].queryset = Student.objects.filter(
                branch=course.branch,
                year=course.year,
                section=course.section
            )
            self.fields['course'].initial = course
            self.fields['course'].widget = forms.HiddenInput()
        else:
            self.fields['student'].queryset = Student.objects.all()


class BulkGradeForm(forms.Form):
    """Form for bulk grade entry for a course"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Course"
    )
    assessment_type = forms.ChoiceField(
        choices=Grade.ASSESSMENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Assessment Type"
    )
    assessment_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Quiz 1, Midterm'
        }),
        label="Assessment Name"
    )
    max_marks = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 100'
        }),
        label="Maximum Marks"
    )
    semester = forms.ChoiceField(
        choices=Grade.SEMESTER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Semester"
    )
    academic_year = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2024-2025'
        }),
        label="Academic Year"
    )
    
    def __init__(self, *args, **kwargs):
        lecturer = kwargs.pop('lecturer', None)
        super(BulkGradeForm, self).__init__(*args, **kwargs)
        
        # Filter courses by lecturer
        if lecturer:
            self.fields['course'].queryset = Course.objects.filter(lecturer=lecturer)