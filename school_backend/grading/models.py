from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from accounts.models import User

class GradingScale(models.Model):
    """Grading scale for the school"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    min_score = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    max_score = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    grade = models.CharField(max_length=10)
    grade_points = models.DecimalField(max_digits=3, decimal_places=2)  # FIXED: Changed accounts.User to grade_points
    remark = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='grading_scales')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['min_score']
        unique_together = ['name', 'grade']
    
    def __str__(self):
        return f"{self.name} - {self.grade} ({self.min_score}-{self.max_score})"

class GradingPeriod(models.Model):
    """Grading periods/terms"""
    TERM_CHOICES = [
        ('term_1', 'Term 1'),
        ('term_2', 'Term 2'),
        ('term_3', 'Term 3'),
        ('semester_1', 'Semester 1'),
        ('semester_2', 'Semester 2'),
        ('annual', 'Annual'),
    ]
    
    name = models.CharField(max_length=100)
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    academic_year = models.CharField(max_length=9)  # Format: 2024-2025
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_finalized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['academic_year', 'start_date']
        unique_together = ['name', 'academic_year']
    
    def __str__(self):
        return f"{self.name} - {self.academic_year}"

class AssessmentType(models.Model):
    """Types of assessments (Exams, Tests, Assignments, etc.)"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=100, 
                                 validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['weight', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.weight}%)"

class Assessment(models.Model):
    """Individual assessment/exam"""
    name = models.CharField(max_length=200)
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.PROTECT, related_name='assessments')
    subject = models.ForeignKey('academics.Subject', on_delete=models.PROTECT, related_name='assessments')
    class_level = models.ForeignKey('academics.Class', on_delete=models.PROTECT, related_name='assessments')
    grading_period = models.ForeignKey(GradingPeriod, on_delete=models.PROTECT, related_name='assessments')
    
    total_marks = models.DecimalField(max_digits=6, decimal_places=2)
    passing_marks = models.DecimalField(max_digits=6, decimal_places=2)
    assessment_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_assessments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-assessment_date', 'subject']
        unique_together = ['name', 'subject', 'class_level', 'grading_period']
    
    def __str__(self):
        return f"{self.name} - {self.subject.name} - {self.class_level.name}"

class StudentGrade(models.Model):
    """Individual student grade for an assessment"""
    # FIXED: Changed from 'students.Student' to 'accounts.User'
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='grades')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='student_grades')
    
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=10, blank=True)
    grade_points = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)  # FIXED
    remark = models.CharField(max_length=100, blank=True)
    
    is_absent = models.BooleanField(default=False)
    is_exempted = models.BooleanField(default=False)
    is_late_submission = models.BooleanField(default=False)
    
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='graded_records')
    graded_at = models.DateTimeField(null=True, blank=True)
    
    comments = models.TextField(blank=True)
    needs_improvement = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['student', 'assessment']
        unique_together = ['student', 'assessment']
        indexes = [
            models.Index(fields=['student', 'assessment']),
            models.Index(fields=['grade']),
        ]
    
    def save(self, *args, **kwargs):
        # Calculate percentage and grade if marks are provided
        if self.marks_obtained is not None and self.assessment.total_marks > 0:
            self.percentage = (self.marks_obtained / self.assessment.total_marks) * 100
            
            # Get grading scale for the subject/assessment
            grading_scale = GradingScale.objects.filter(
                is_active=True,
                min_score__lte=self.percentage,
                max_score__gte=self.percentage
            ).first()
            
            if grading_scale:
                self.grade = grading_scale.grade
                self.grade_points = grading_scale.grade_points  # FIXED
                self.remark = grading_scale.remark
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student} - {self.assessment}: {self.marks_obtained}/{self.assessment.total_marks}"

class SubjectGrade(models.Model):
    """Overall subject grade for a student in a grading period"""
    # FIXED: Changed from 'students.Student' to 'accounts.User'
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='subject_grades')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='student_grades')
    class_level = models.ForeignKey('academics.Class', on_delete=models.CASCADE, related_name='subject_grades')
    grading_period = models.ForeignKey(GradingPeriod, on_delete=models.CASCADE, related_name='subject_grades')
    
    total_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    marks_obtained = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade = models.CharField(max_length=10, blank=True)
    grade_points = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)  # FIXED
    remark = models.CharField(max_length=100, blank=True)
    
    rank_in_class = models.IntegerField(null=True, blank=True)
    rank_in_subject = models.IntegerField(null=True, blank=True)
    
    teacher_comments = models.TextField(blank=True)
    principal_comments = models.TextField(blank=True)
    
    is_finalized = models.BooleanField(default=False)
    finalized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='finalized_grades')
    finalized_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['student', 'subject']
        unique_together = ['student', 'subject', 'grading_period']
        indexes = [
            models.Index(fields=['student', 'grading_period']),
            models.Index(fields=['class_level', 'subject']),
        ]
    
    def calculate_overall_grade(self):
        """Calculate overall grade from individual assessments"""
        grades = StudentGrade.objects.filter(
            student=self.student,
            assessment__subject=self.subject,
            assessment__grading_period=self.grading_period
        ).exclude(is_absent=True).exclude(is_exempted=True)
        
        if not grades.exists():
            return
        
        total_weighted_marks = 0
        total_weight = 0
        
        for grade in grades:
            if grade.marks_obtained is not None:
                weight = grade.assessment.assessment_type.weight
                total_weighted_marks += (grade.marks_obtained / grade.assessment.total_marks) * weight
                total_weight += weight
        
        if total_weight > 0:
            self.percentage = (total_weighted_marks / total_weight) * 100
            
            # Get grading scale
            grading_scale = GradingScale.objects.filter(
                is_active=True,
                min_score__lte=self.percentage,
                max_score__gte=self.percentage
            ).first()
            
            if grading_scale:
                self.grade = grading_scale.grade
                self.grade_points = grading_scale.grade_points  # FIXED
                self.remark = grading_scale.remark
    
    def __str__(self):
        return f"{self.student} - {self.subject}: {self.grade} ({self.percentage}%)"

class ReportCard(models.Model):
    """Student report card for a grading period"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    # FIXED: Changed from 'students.Student' to 'accounts.User'
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='report_cards')
    grading_period = models.ForeignKey(GradingPeriod, on_delete=models.CASCADE, related_name='report_cards')
    class_level = models.ForeignKey('academics.Class', on_delete=models.CASCADE, related_name='report_cards')
    
    total_subjects = models.IntegerField(default=0)
    total_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    marks_obtained = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    overall_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overall_grade = models.CharField(max_length=10, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    attendance_days = models.IntegerField(default=0)
    days_present = models.IntegerField(default=0)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class_position = models.IntegerField(null=True, blank=True)
    stream_position = models.IntegerField(null=True, blank=True)
    overall_position = models.IntegerField(null=True, blank=True)
    
    teacher_comments = models.TextField(blank=True)
    principal_comments = models.TextField(blank=True)
    parent_comments = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='published_report_cards')
    published_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-grading_period__end_date', 'student']
        unique_together = ['student', 'grading_period']
        indexes = [
            models.Index(fields=['student', 'grading_period']),
            models.Index(fields=['class_level', 'grading_period']),
        ]
    
    def calculate_overall(self):
        """Calculate overall performance"""
        subject_grades = SubjectGrade.objects.filter(
            student=self.student,
            grading_period=self.grading_period,
            is_finalized=True
        )
        
        if not subject_grades.exists():
            return
        
        self.total_subjects = subject_grades.count()
        self.marks_obtained = sum([sg.marks_obtained for sg in subject_grades])
        self.total_marks = sum([sg.total_marks for sg in subject_grades])
        
        if self.total_marks > 0:
            self.overall_percentage = (self.marks_obtained / self.total_marks) * 100
        
        # Calculate GPA
        total_grade_points = sum([sg.grade_points or 0 for sg in subject_grades])  # FIXED
        self.gpa = total_grade_points / self.total_subjects if self.total_subjects > 0 else 0
        
        # Get overall grade
        grading_scale = GradingScale.objects.filter(
            is_active=True,
            min_score__lte=self.overall_percentage,
            max_score__gte=self.overall_percentage
        ).first()
        
        if grading_scale:
            self.overall_grade = grading_scale.grade
    
    def __str__(self):
        return f"Report Card: {self.student} - {self.grading_period.name}"

class Gradebook(models.Model):
    """Gradebook for a teacher-subject-class combination"""
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gradebooks')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='gradebooks')
    class_level = models.ForeignKey('academics.Class', on_delete=models.CASCADE, related_name='gradebooks')
    grading_period = models.ForeignKey(GradingPeriod, on_delete=models.CASCADE, related_name='gradebooks')
    
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['teacher', 'subject', 'class_level', 'grading_period']
        ordering = ['subject', 'class_level']
    
    def __str__(self):
        return f"{self.teacher.username}'s Gradebook - {self.subject.name} ({self.class_level.name})"