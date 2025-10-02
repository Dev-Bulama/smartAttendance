from django.db import models

from django.contrib.auth.models import User


def user_directory_path(instance, filename): 
    name, ext = filename.split(".")
    name = instance.firstname + instance.lastname
    filename = name +'.'+ ext 
    return 'Faculty_Images/{}'.format(filename)

class Faculty(models.Model):

    user = models.OneToOneField(User, null = True, blank = True, on_delete= models.CASCADE)
    firstname = models.CharField(max_length=200, null=True, blank=True)
    lastname = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(upload_to=user_directory_path ,null=True, blank=True)

    def __str__(self):
        return str(self.firstname + " " + self.lastname)


def student_directory_path(instance, filename): 
    name, ext = filename.split(".")
    name = instance.registration_id # + "_" + instance.branch + "_" + instance.year + "_" + instance.section
    filename = name +'.'+ ext 
    return 'Student_Images/{}/{}/{}/{}'.format(instance.branch,instance.year,instance.section,filename)

class Student(models.Model):

    BRANCH = (
        ('CSE','CSE'),
        ('IT','IT'),
        ('ECE','ECE'),
        ('CHEM','CHEM'),
        ('MECH','MECH'),
        ('EEE','EEE'),
    )
    YEAR = (
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
    )
    SECTION = (
        ('A','A'),
        ('B','B'),
        ('C','C'),
    )

    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=200, null=True, blank=True)
    lastname = models.CharField(max_length=200, null=True, blank=True)
    registration_id = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    branch = models.CharField(max_length=100, null=True, choices=BRANCH)
    year = models.CharField(max_length=100, null=True, choices=YEAR)
    section = models.CharField(max_length=100, null=True, choices=SECTION)
    profile_pic = models.ImageField(upload_to=student_directory_path, null=True, blank=True)


    def __str__(self):
        return str(self.registration_id)

class Attendence(models.Model):
    # faculty = models.ForeignKey(Faculty, null = True, on_delete= models.SET_NULL)
    # student = models.ForeignKey(Student, null = True, on_delete= models.SET_NULL)
    Faculty_Name = models.CharField(max_length=200, null=True, blank=True)
    Student_ID = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateField(auto_now_add = True, null = True)
    time = models.TimeField(auto_now_add=True, null = True)
    branch = models.CharField(max_length=200, null = True)
    year = models.CharField(max_length=200, null = True)
    section = models.CharField(max_length=200, null = True)
    period = models.CharField(max_length=200, null = True)
    status = models.CharField(max_length=200, null = True, default='Absent')

    def __str__(self):
        return str(self.Student_ID + "_" + str(self.date)+ "_" + str(self.period))
class Course(models.Model):
    """Model for managing courses"""
    
    BRANCH = (
        ('CSE','CSE'),
        ('IT','IT'),
        ('ECE','ECE'),
        ('CHEM','CHEM'),
        ('MECH','MECH'),
        ('EEE','EEE'),
    )
    YEAR = (
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
    )
    SECTION = (
        ('A','A'),
        ('B','B'),
        ('C','C'),
    )
    
    course_name = models.CharField(max_length=200, null=False, blank=False)
    course_code = models.CharField(max_length=50, unique=True, null=False, blank=False)
    credits = models.IntegerField(default=3, null=True, blank=True)
    branch = models.CharField(max_length=100, null=True, choices=BRANCH)
    year = models.CharField(max_length=100, null=True, choices=YEAR)
    section = models.CharField(max_length=100, null=True, choices=SECTION)
    lecturer = models.ForeignKey(Faculty, null=True, blank=True, on_delete=models.SET_NULL, related_name='courses')
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.course_code} - {self.course_name}"
    
    class Meta:
        ordering = ['course_code']


class Session(models.Model):
    """Model for managing class sessions"""
    
    STATUS_CHOICES = (
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions')
    lecturer = models.ForeignKey(Faculty, null=True, on_delete=models.SET_NULL, related_name='sessions')
    date = models.DateField(null=False, blank=False)
    period = models.CharField(max_length=50, null=False, blank=False)
    topic = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Scheduled')
    attendance_marked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.course.course_code} - {self.date} - Period {self.period}"
    
    class Meta:
        ordering = ['-date', 'period']
        unique_together = ['course', 'date', 'period']  # Prevent duplicate sessions
class Grade(models.Model):
    """Model for managing student grades"""

    ASSESSMENT_TYPES = (
        ('Quiz', 'Quiz/Test'),
        ('Assignment', 'Assignment'),
        ('Midterm', 'Midterm Exam'),
        ('Final', 'Final Exam'),
        ('Project', 'Project'),
    )

    SEMESTER_CHOICES = (
        ('Fall', 'Fall Semester'),
        ('Spring', 'Spring Semester'),
    )

    GRADE_LETTERS = (
        ('A+', 'A+ (90-100)'),
        ('A', 'A (85-89)'),
        ('B+', 'B+ (80-84)'),
        ('B', 'B (75-79)'),
        ('C+', 'C+ (70-74)'),
        ('C', 'C (65-69)'),
        ('D', 'D (60-64)'),
        ('F', 'F (0-59)'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    lecturer = models.ForeignKey(Faculty, null=True, on_delete=models.SET_NULL, related_name='grades_given')

    assessment_type = models.CharField(max_length=50, choices=ASSESSMENT_TYPES)
    assessment_name = models.CharField(max_length=200, null=True, blank=True, help_text="e.g., Quiz 1, Assignment 2")

    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    grade_letter = models.CharField(max_length=2, choices=GRADE_LETTERS, editable=False)

    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES)
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")

    remarks = models.TextField(null=True, blank=True)
    date_recorded = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate percentage
        if self.max_marks > 0:
            self.percentage = (self.marks_obtained / self.max_marks) * 100
        else:
            self.percentage = 0
        
        # Determine grade letter based on percentage
        if self.percentage >= 90:
            self.grade_letter = 'A+'
        elif self.percentage >= 85:
            self.grade_letter = 'A'
        elif self.percentage >= 80:
            self.grade_letter = 'B+'
        elif self.percentage >= 75:
            self.grade_letter = 'B'
        elif self.percentage >= 70:
            self.grade_letter = 'C+'
        elif self.percentage >= 65:
            self.grade_letter = 'C'
        elif self.percentage >= 60:
            self.grade_letter = 'D'
        else:
            self.grade_letter = 'F'
        
        super(Grade, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.registration_id} - {self.course.course_code} - {self.assessment_type}: {self.grade_letter}"

    class Meta:
        ordering = ['-date_recorded']
        unique_together = ['student', 'course', 'assessment_type', 'assessment_name', 'semester', 'academic_year']


class CourseGrade(models.Model):
    """Model for final course grades (calculated from all assessments)"""

    GRADE_LETTERS = (
        ('A+', 'A+ (90-100)'),
        ('A', 'A (85-89)'),
        ('B+', 'B+ (80-84)'),
        ('B', 'B (75-79)'),
        ('C+', 'C+ (70-74)'),
        ('C', 'C (65-69)'),
        ('D', 'D (60-64)'),
        ('F', 'F (0-59)'),
    )

    SEMESTER_CHOICES = (
        ('Fall', 'Fall Semester'),
        ('Spring', 'Spring Semester'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='final_grades')
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES)
    academic_year = models.CharField(max_length=20)

    final_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_letter = models.CharField(max_length=2, choices=GRADE_LETTERS)

    quiz_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    assignment_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    midterm_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    project_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    remarks = models.TextField(null=True, blank=True)
    date_calculated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.registration_id} - {self.course.course_code} - {self.semester} {self.academic_year}: {self.grade_letter}"

    class Meta:
        ordering = ['-academic_year', '-semester']
        unique_together = ['student', 'course', 'semester', 'academic_year']