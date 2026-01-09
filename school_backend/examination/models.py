# examination/models.py
import datetime
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

# Import models from other apps
from academics.models import Class, Subject, AcademicYear, AcademicTerm
from accounts.models import User
from students.models import StudentProfile, StudentEnrollment

User = get_user_model()


class BaseExamModel(models.Model):
    """Abstract base model for all examination models with common fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class GradeScale(BaseExamModel):
    """Translate a numeric grade to other scales (Letter grade, 4.0 scale, etc.)"""
    
    CURRICULUM_CHOICES = [
        ('cbc', 'CBC'),
        ('8-4-4', '8-4-4'),
        ('igcse', 'IGCSE'),
        ('ib', 'IB'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    curriculum = models.CharField(
        max_length=20,
        choices=CURRICULUM_CHOICES,
        default='8-4-4'
    )
    is_default = models.BooleanField(
        default=False, 
        help_text="Default grade scale for the system"
    )

    class Meta:
        verbose_name = _("Grade Scale")
        verbose_name_plural = _("Grade Scales")
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_rule(self, grade):
        """Get the grade scale rule for a specific grade"""
        if grade is None:
            return None
        rule = self.gradescalerule_set.filter(
            min_grade__lte=grade, 
            max_grade__gte=grade
        ).first()
        return rule

    def to_letter(self, grade):
        """Convert numeric grade to letter grade"""
        rule = self.get_rule(grade)
        return rule.letter_grade if rule else None

    def to_numeric(self, grade):
        """Convert numeric grade to scale points"""
        rule = self.get_rule(grade)
        return rule.numeric_scale if rule else None

    def save(self, *args, **kwargs):
        """Ensure only one default grade scale per curriculum"""
        if self.is_default:
            GradeScale.objects.filter(
                curriculum=self.curriculum, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class GradeScaleRule(BaseExamModel):
    """Individual rule for grade scale conversion"""
    
    min_grade = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_grade = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    letter_grade = models.CharField(max_length=50, blank=True, null=True)
    numeric_scale = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(4)]
    )
    grade_scale = models.ForeignKey(GradeScale, on_delete=models.CASCADE)
    description = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Grade description"
    )
    color = models.CharField(
        max_length=7, 
        default='#6B7280', 
        help_text="Hex color for display"
    )

    class Meta:
        unique_together = ("min_grade", "max_grade", "grade_scale")
        ordering = ['grade_scale', '-min_grade']
        indexes = [
            models.Index(fields=["min_grade", "max_grade", "grade_scale"]),
        ]
        verbose_name = _("Grade Scale Rule")
        verbose_name_plural = _("Grade Scale Rules")

    def __str__(self):
        return f"{self.min_grade}-{self.max_grade} {self.letter_grade} {self.numeric_scale}"

    def clean(self):
        """Validate grade rule consistency"""
        if not self.letter_grade and not self.numeric_scale:
            raise ValidationError(
                "Either a letter grade or numeric scale must be provided."
            )
        
        if self.min_grade >= self.max_grade:
            raise ValidationError("min_grade must be less than max_grade.")
            
        if self.min_grade < 0 or self.max_grade > 100:
            raise ValidationError("Grades must be between 0 and 100.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Examination(BaseExamModel):
    """Examination management with scheduling and tracking"""
    
    EXAM_TYPES = [
        ('cat1', 'CAT 1'),
        ('cat2', 'CAT 2'),
        ('cat3', 'CAT 3'),
        ('end_term', 'End of AcademicTerm'),
        ('mid_term', 'Mid AcademicTerm'),
        ('pre_mock', 'Pre-Mock'),
        ('mock', 'Mock Exam'),
        ('kcpe', 'KCPE'),
        ('kcse', 'KCSE'),
        ('internal', 'Internal Assessment'),
    ]
    
    EXAM_STATUS = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('postponed', 'Postponed'),
    ]

    name = models.CharField(max_length=100, help_text="Name of the examination")
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES, default='internal')
    status = models.CharField(max_length=20, choices=EXAM_STATUS, default='scheduled')
    start_date = models.DateField()
    end_date = models.DateField()
    out_of = models.IntegerField(
        default=100,
        help_text="Maximum possible score",
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    
    # Academic context
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    classes = models.ManyToManyField(Class, related_name="examinations")
    subjects = models.ManyToManyField(Subject, related_name="examinations", blank=True)
    
    # Additional details
    instructions = models.TextField(blank=True, help_text="Examination instructions")
    duration = models.DurationField(null=True, blank=True, help_text="Exam duration")
    venue = models.CharField(max_length=200, blank=True, help_text="Exam venue")
    
    # Grade scale for this exam
    grade_scale = models.ForeignKey(
        GradeScale, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Grade scale used for this examination"
    )
    
    comments = models.TextField(blank=True, null=True, help_text="Comments Regarding Exam")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_examinations'
    )
    
    # Timestamps
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', 'name']
        verbose_name = _("Examination")
        verbose_name_plural = _("Examinations")
        indexes = [
            models.Index(fields=['exam_type', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['academic_year', 'term']),
        ]

    def __str__(self):
        return f"{self.name} - {self.academic_year} {self.term}"

    @property
    def exam_status(self):
        """Calculate exam status based on dates"""
        today = datetime.date.today()
        if today > self.end_date:
            return "completed"
        elif self.start_date <= today <= self.end_date:
            return "ongoing"
        return "scheduled"

    @property
    def total_students(self):
        """Get total number of students taking this exam"""
        total = 0
        for class_obj in self.classes.all():
            total += StudentEnrollment.objects.filter(
                class_enrolled=class_obj,
                status='active',
                academic_year=self.academic_year
            ).count()
        return total

    @property
    def is_active(self):
        """Check if exam is currently active"""
        today = datetime.date.today()
        return self.start_date <= today <= self.end_date

    @property
    def days_remaining(self):
        """Days remaining until exam starts"""
        if self.start_date:
            delta = self.start_date - datetime.date.today()
            return max(0, delta.days)
        return None

    def clean(self):
        """Validate examination data"""
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be later than end date.")
        
        # Validate exam dates within term dates
        if (self.start_date < self.term.start_date or 
            self.end_date > self.term.end_date):
            raise ValidationError("Exam dates must be within the term dates.")
            
        super().clean()

    def save(self, *args, **kwargs):
        """Auto-update status based on dates"""
        self.status = self.exam_status
        super().save(*args, **kwargs)


class StudentMark(BaseExamModel):
    """Individual student marks for examinations"""
    
    exam = models.ForeignKey(
        Examination, 
        on_delete=models.CASCADE, 
        related_name="student_marks"
    )
    points_scored = models.FloatField(
        help_text="Points scored by student",
        validators=[MinValueValidator(0)]
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name="student_marks"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="exam_marks"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="entered_marks"
    )
    
    # Calculated fields
    percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage score"
    )
    grade = models.CharField(max_length=5, blank=True, help_text="Letter grade")
    points = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        help_text="Grade points"
    )
    remarks = models.CharField(max_length=100, blank=True, help_text="Teacher remarks")
    
    # Status flags
    is_absent = models.BooleanField(default=False, help_text="Student was absent")
    is_special = models.BooleanField(default=False, help_text="Special consideration")
    special_notes = models.TextField(blank=True, help_text="Notes for special cases")
    
    # Verification
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_marks'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    date_time = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("exam", "subject", "student")
        ordering = ["exam", "subject", "student"]
        verbose_name = _("Student Mark")
        verbose_name_plural = _("Student Marks")
        indexes = [
            models.Index(fields=['exam', 'subject']),
            models.Index(fields=['student', 'exam']),
            models.Index(fields=['grade', 'points']),
        ]

    def __str__(self):
        return f"{self.exam.name} - {self.student.get_full_name()} - {self.subject} - {self.points_scored}"

    @property
    def is_passing(self):
        """Check if mark is passing (50% and above)"""
        return self.percentage >= 50 if self.percentage else False

    @property
    def mark_summary(self):
        """Generate comprehensive mark summary"""
        return {
            'student': self.student.get_full_name(),
            'subject': self.subject.name,
            'points_scored': self.points_scored,
            'out_of': self.exam.out_of,
            'percentage': float(self.percentage) if self.percentage else 0,
            'grade': self.grade,
            'points': float(self.points) if self.points else 0,
            'remarks': self.remarks,
            'is_passing': self.is_passing
        }

    def clean(self):
        """Validate mark data"""
        if not self.is_absent:
            if self.points_scored < 0 or self.points_scored > self.exam.out_of:
                raise ValidationError(
                    f"Points scored must be between 0 and {self.exam.out_of}."
                )
        else:
            self.points_scored = 0
            
        super().clean()

    def save(self, *args, **kwargs):
        """Calculate derived fields before saving"""
        if not self.is_absent and self.exam.out_of > 0:
            self.percentage = (self.points_scored / self.exam.out_of) * 100
            
            # Auto-calculate grade if grade scale exists
            if self.exam.grade_scale:
                self.grade = self.exam.grade_scale.to_letter(float(self.percentage))
                self.points = self.exam.grade_scale.to_numeric(float(self.percentage))
            
            # Auto-generate remarks
            if self.percentage >= 80:
                self.remarks = "Excellent"
            elif self.percentage >= 70:
                self.remarks = "Good"
            elif self.percentage >= 60:
                self.remarks = "Satisfactory"
            elif self.percentage >= 50:
                self.remarks = "Fair"
            else:
                self.remarks = "Needs Improvement"
        else:
            self.percentage = 0
            self.grade = "ABS"
            self.remarks = "Absent"
            
        super().save(*args, **kwargs)


class Result(BaseExamModel):
    """Comprehensive student academic results for a term"""
    
    CONDUCT_GRADES = [
        ('A', 'Excellent'),
        ('B', 'Good'),
        ('C', 'Satisfactory'),
        ('D', 'Needs Improvement'),
        ('E', 'Unsatisfactory'),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='academic_results'
    )
    gpa = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        help_text="Grade Point Average"
    )
    cat_gpa = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        help_text="CAT Grade Point Average"
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    grade_scale = models.ForeignKey(
        GradeScale, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Grade scale used for this result"
    )
    
    # Position tracking
    class_position = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Position in class"
    )
    stream_position = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Position in stream"
    )
    overall_position = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Overall position"
    )
    total_students = models.PositiveIntegerField(
        default=0, 
        help_text="Total students in class"
    )
    
    # Performance metrics
    attendance_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Attendance rate for the term"
    )
    conduct_grade = models.CharField(
        max_length=2, 
        blank=True, 
        choices=CONDUCT_GRADES,
        help_text="Conduct/Behavior grade"
    )
    
    # Comments and feedback
    teacher_comments = models.TextField(blank=True, help_text="Teacher's general comments")
    principal_comments = models.TextField(blank=True, help_text="Principal's comments")
    improvement_areas = models.TextField(blank=True, help_text="Areas for improvement")
    
    # Publication status
    is_published = models.BooleanField(default=False, help_text="Whether results are published to parents")
    published_at = models.DateTimeField(null=True, blank=True)
    parent_acknowledged = models.BooleanField(default=False, help_text="Parent has acknowledged results")
    parent_acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "academic_year", "term")
        ordering = ["academic_year", "term", "class_position"]
        verbose_name = _("Student Result")
        verbose_name_plural = _("Student Results")
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['gpa', 'class_position']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.academic_year} {self.term}"

    @property
    def letter_grade(self):
        """Get letter grade based on GPA"""
        if self.gpa is None or not self.grade_scale:
            return None
        return self.grade_scale.to_letter(self.gpa)

    @property
    def performance_summary(self):
        """Generate comprehensive performance summary"""
        return {
            'gpa': self.gpa,
            'letter_grade': self.letter_grade,
            'class_position': self.class_position,
            'total_students': self.total_students,
            'attendance_rate': float(self.attendance_rate),
            'conduct_grade': self.conduct_grade
        }

    def clean(self):
        """Validate result data"""
        if self.gpa is not None and (self.gpa < 0.0 or self.gpa > 4.0):
            raise ValidationError("GPA must be between 0.0 and 4.0.")
        if self.cat_gpa is not None and (self.cat_gpa < 0.0 or self.cat_gpa > 4.0):
            raise ValidationError("CAT GPA must be between 0.0 and 4.0.")
        
        if self.class_position and self.total_students:
            if self.class_position > self.total_students:
                raise ValidationError("Class position cannot exceed total students.")

    def save(self, *args, **kwargs):
        """Auto-calculate total students if not provided"""
        if not self.total_students and hasattr(self.student, 'current_class'):
            self.total_students = StudentEnrollment.objects.filter(
                class_enrolled=self.student.current_class,
                status='active',
                academic_year=self.academic_year
            ).count()
        super().save(*args, **kwargs)


class SubjectResult(BaseExamModel):
    """Detailed subject-level results for comprehensive reporting"""
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subject_results'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    
    # Assessment components
    cat1_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    cat2_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    cat3_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    end_term_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Calculated scores
    total_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    average_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    grade = models.CharField(max_length=5, blank=True)
    points = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(4)]
    )
    
    # Teacher feedback
    teacher_comments = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    improvement_areas = models.TextField(blank=True)
    
    # Position tracking
    subject_position = models.PositiveIntegerField(null=True, blank=True)
    total_in_subject = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "subject", "academic_year", "term")
        ordering = ["subject", "subject_position"]
        verbose_name = _("Subject Result")
        verbose_name_plural = _("Subject Results")
        indexes = [
            models.Index(fields=['student', 'subject']),
            models.Index(fields=['academic_year', 'term']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject} - {self.academic_year} {self.term}"

    @property
    def is_passing(self):
        """Check if subject result is passing"""
        return self.average_score >= 50 if self.average_score else False

    def save(self, *args, **kwargs):
        """Calculate total and average scores"""
        scores = [self.cat1_score, self.cat2_score, self.cat3_score, self.end_term_score]
        valid_scores = [score for score in scores if score is not None]
        
        if valid_scores:
            self.total_score = sum(valid_scores)
            self.average_score = self.total_score / len(valid_scores)
        
        super().save(*args, **kwargs)