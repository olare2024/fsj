# assignments/models.py - COMPLETE FIXED VERSION
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
import uuid
import os
import json

User = get_user_model()


def assignment_file_path(instance, filename):
    """Generate file path for assignment attachments"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('assignments', str(instance.term.id), filename)


def submission_file_path(instance, filename):
    """Generate file path for student submissions"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('submissions', str(instance.assignment.term.id), filename)


class BaseAssignmentModel(models.Model):
    """Abstract base model for all assignment models"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class AssignmentCategory(BaseAssignmentModel):
    """Categories for organizing assignments"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name")
    
    # Kenya curriculum alignment
    curriculum = models.CharField(
        max_length=10,
        choices=[
            ('cbc', 'CBC'),
            ('8-4-4', '8-4-4'),
            ('igcse', 'IGCSE'),
        ],
        default='cbc'
    )
    education_level = models.CharField(
        max_length=20,
        choices=[
            ('pre_primary', 'Pre-Primary'),
            ('lower_primary', 'Lower Primary'),
            ('upper_primary', 'Upper Primary'),
            ('lower_secondary', 'Lower Secondary'),
            ('upper_secondary', 'Upper Secondary'),
        ],
        blank=True
    )

    class Meta:
        verbose_name = _('Assignment Category')
        verbose_name_plural = _('Assignment Categories')
        ordering = ['name']

    def __str__(self):
        return self.name


class AssignmentManager(models.Manager):
    """Custom manager for Assignment model with optimized queries"""
    
    def get_queryset(self):
        """Return base queryset with common select_related and prefetch_related"""
        return super().get_queryset().select_related(
            'subject', 'teacher', 'classroom', 
            'academic_year', 'term', 'category', 'created_by'
        ).prefetch_related('student_assignments')
    
    def active(self):
        """Get active assignments"""
        return self.get_queryset().filter(is_active=True)
    
    def published(self):
        """Get published assignments"""
        return self.active().filter(status='published')
    
    def for_teacher(self, teacher_user):
        """
        Get assignments for a specific teacher (User instance)
        
        Args:
            teacher_user: User instance with teacher role
        """
        return self.active().filter(teacher=teacher_user)
    
    def for_classroom(self, classroom):
        """Get assignments for a specific classroom"""
        return self.active().filter(classroom=classroom)
    
    def for_student(self, student_user):
        """
        Get assignments for a specific student based on enrollment
        
        Args:
            student_user: User instance with student role
        """
        from students.models import StudentEnrollment
        
        enrollment = StudentEnrollment.objects.filter(
            student_profile__user=student_user,
            status='active'
        ).select_related('class_enrolled', 'academic_year').first()
        
        if enrollment:
            return self.published().filter(
                classroom=enrollment.class_enrolled,
                academic_year=enrollment.academic_year,
                term=enrollment.current_term
            )
        return self.none()
    
    def overdue(self):
        """Get overdue assignments"""
        return self.published().filter(
            due_date__lt=timezone.now(),
            status__in=['published', 'in_progress']
        )
    
    def upcoming(self, days=7):
        """Get assignments due within specified days"""
        from django.db.models import Q
        
        now = timezone.now()
        future_date = now + timezone.timedelta(days=days)
        
        return self.published().filter(
            Q(due_date__gte=now) & Q(due_date__lte=future_date)
        )
    
    def with_submission_stats(self):
        """Annotate queryset with submission statistics"""
        from django.db.models import Count, Q, F, Avg, ExpressionWrapper, FloatField
        
        return self.get_queryset().annotate(
            total_students_count=Count('classroom__student_enrollments', 
                                     filter=Q(classroom__student_enrollments__status='active')),
            submitted_count=Count('student_assignments',
                                filter=Q(student_assignments__status__in=['submitted', 'late', 'graded'])),
            graded_count=Count('student_assignments',
                             filter=Q(student_assignments__status='graded')),
            average_score=Avg('student_assignments__marks_obtained',
                            filter=Q(student_assignments__status='graded')),
            submission_rate=ExpressionWrapper(
                F('submitted_count') * 100.0 / F('total_students_count'),
                output_field=FloatField()
            ),
        )


class Assignment(BaseAssignmentModel):
    """Enhanced Assignment model for Delvok Academy with Kenya CBC/8-4-4 support"""
    
    # Constants and Choices
    class AssignmentTypes(models.TextChoices):
        HOMEWORK = 'homework', _('Homework')
        CLASSWORK = 'classwork', _('Classwork')
        PROJECT = 'project', _('Project')
        QUIZ = 'quiz', _('Quiz')
        TEST = 'test', _('Test')
        EXAM = 'exam', _('Exam')
        PRACTICAL = 'practical', _('Practical Work')
        PRESENTATION = 'presentation', _('Presentation')
        RESEARCH = 'research', _('Research Paper')
        REVISION = 'revision', _('Revision Exercise')
        ASSESSMENT = 'assessment', _('Continuous Assessment')
    
    class StatusChoices(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
        IN_PROGRESS = 'in_progress', _('In Progress')
        CLOSED = 'closed', _('Closed')
        GRADED = 'graded', _('Graded')
        ARCHIVED = 'archived', _('Archived')
    
    class DifficultyLevels(models.TextChoices):
        EASY = 'easy', _('Easy')
        MEDIUM = 'medium', _('Medium')
        HARD = 'hard', _('Hard')
        CHALLENGING = 'challenging', _('Challenging')
    
    class CurriculumChoices(models.TextChoices):
        CBC = 'cbc', _('CBC')
        EIGHT_FOUR_FOUR = '8-4-4', _('8-4-4')
        IGCSE = 'igcse', _('IGCSE')
    
    class CoreCompetencies(models.TextChoices):
        COMMUNICATION = 'communication', _('Communication and Collaboration')
        CRITICAL_THINKING = 'critical_thinking', _('Critical Thinking and Problem Solving')
        CREATIVITY = 'creativity', _('Creativity and Imagination')
        CITIZENSHIP = 'citizenship', _('Citizenship')
        LEARNING_TO_LEARN = 'learning_to_learn', _('Learning to Learn')
        SELF_EFFICACY = 'self_efficacy', _('Self-Efficacy')
        DIGITAL_LITERACY = 'digital_literacy', _('Digital Literacy')
    
    # ====================
    # CORE RELATIONSHIPS
    # ====================
    
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='assignments_created',
        verbose_name=_('Teacher'),
        help_text=_("Teacher who created this assignment")
    )
    
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name=_('Subject')
    )
    
    classroom = models.ForeignKey(
        'academics.Class',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='assignments_classroom',
        verbose_name=_('Classroom')
    )
    
    stream = models.ForeignKey(
        'academics.Stream',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments',
        verbose_name=_('Stream')
    )
    
    academic_year = models.ForeignKey(
        'academics.AcademicYear',
        on_delete=models.CASCADE,
        verbose_name=_('Academic Year')
    )
    
    term = models.ForeignKey(
        'academics.AcademicTerm', 
        on_delete=models.CASCADE, 
        verbose_name=_('Academic Term')
    )
    
    # ====================
    # BASIC INFORMATION
    # ====================
    
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    assignment_type = models.CharField(
        max_length=20,
        choices=AssignmentTypes.choices,
        default=AssignmentTypes.HOMEWORK,
        verbose_name=_('Type')
    )
    
    category = models.ForeignKey(
        AssignmentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Category')
    )
    
    curriculum = models.CharField(
        max_length=10,
        choices=CurriculumChoices.choices,
        default=CurriculumChoices.CBC,
        verbose_name=_('Curriculum')
    )
    
    # ====================
    # ASSIGNMENT DETAILS
    # ====================
    
    due_date = models.DateTimeField(verbose_name=_('Due Date'))
    total_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        verbose_name=_('Total Marks')
    )
    
    passing_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=40,
        validators=[MinValueValidator(0)],
        verbose_name=_('Passing Marks')
    )
    
    difficulty_level = models.CharField(
        max_length=15,
        choices=DifficultyLevels.choices,
        default=DifficultyLevels.MEDIUM,
        verbose_name=_('Difficulty Level')
    )
    
    estimated_completion_time = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(5)],
        help_text=_("Estimated time in minutes"),
        verbose_name=_('Estimated Time')
    )
    
    # ====================
    # CONTENT & INSTRUCTIONS
    # ====================
    
    instructions = models.TextField(blank=True, verbose_name=_('Instructions'))
    learning_objectives = models.TextField(
        blank=True,
        help_text=_("Specific learning objectives for this assignment"),
        verbose_name=_('Learning Objectives')
    )
    
    resources = models.TextField(
        blank=True,
        help_text=_("Recommended resources or reading materials"),
        verbose_name=_('Resources')
    )
    
    rubric = models.JSONField(
        blank=True,
        null=True,
        help_text=_("Grading rubric in JSON format"),
        verbose_name=_('Rubric')
    )
    
    # ====================
    # KENYA CBC COMPETENCIES
    # ====================
    
    competencies = models.JSONField(
        blank=True,
        null=True,
        help_text=_("CBC competencies addressed in this assignment"),
        verbose_name=_('Competencies')
    )
    
    core_competencies = models.CharField(
        max_length=20,
        choices=CoreCompetencies.choices,
        blank=True,
        verbose_name=_('Core Competencies')
    )
    
    # ====================
    # CREATION & OWNERSHIP
    # ====================
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_assignments',
        verbose_name=_('Created By')
    )
    
    # ====================
    # ATTACHMENTS
    # ====================
    
    attachment = models.FileField(
        upload_to=assignment_file_path,
        blank=True,
        null=True,
        verbose_name=_('Main Attachment')
    )
    
    additional_files = models.JSONField(
        blank=True,
        null=True,
        help_text=_("JSON array of additional file URLs"),
        verbose_name=_('Additional Files')
    )
    
    # ====================
    # SUBMISSION SETTINGS
    # ====================
    
    allow_late_submission = models.BooleanField(
        default=False,
        verbose_name=_('Allow Late Submission')
    )
    
    late_submission_penalty = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Percentage penalty for late submissions"),
        verbose_name=_('Late Submission Penalty')
    )
    
    allow_resubmission = models.BooleanField(
        default=False,
        verbose_name=_('Allow Resubmission')
    )
    
    max_resubmissions = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        verbose_name=_('Max Resubmissions')
    )
    
    require_approval = models.BooleanField(
        default=False,
        verbose_name=_('Require Approval')
    )
    
    is_group_assignment = models.BooleanField(
        default=False,
        verbose_name=_('Group Assignment')
    )
    
    max_group_size = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_('Max Group Size')
    )
    
    # ====================
    # STATUS & TRACKING
    # ====================
    
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name=_('Status')
    )
    
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Published At'))
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Closed At'))
    
    # ====================
    # ANALYTICS (cached values)
    # ====================
    
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('Views Count'))
    average_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Average Score')
    )
    
    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Completion Rate')
    )
    
    # ====================
    # APPROVAL WORKFLOW
    # ====================
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__in': ['admin', 'head_teacher']},
        related_name='approved_assignments_by',
        verbose_name=_('Approved By')
    )
    
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Approved At'))
    
    # ====================
    # CUSTOM MANAGER
    # ====================
    
    objects = AssignmentManager()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')
        indexes = [
            models.Index(fields=['teacher', 'status']),
            models.Index(fields=['subject', 'academic_year']),
            models.Index(fields=['classroom', 'due_date']),
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['curriculum', 'difficulty_level']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(passing_marks__lte=models.F('total_marks')),
                name='passing_marks_lte_total_marks'
            ),
            models.CheckConstraint(
                check=models.Q(due_date__gt=models.F('created_at')),
                name='due_date_after_creation'
            ),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.subject.name} - {self.teacher.get_full_name()}"
    
    # ====================
    # PROPERTIES
    # ====================
    
    @property
    def teacher_name(self):
        """Get teacher's full name"""
        return self.teacher.get_full_name()
    
    @property
    def teacher_profile(self):
        """Get teacher profile if exists"""
        try:
            return self.teacher.teacher_profile
        except:
            return None
    
    @property
    def is_published(self):
        return self.status == self.StatusChoices.PUBLISHED
    
    @property
    def is_closed(self):
        return self.status in [
            self.StatusChoices.CLOSED,
            self.StatusChoices.GRADED,
            self.StatusChoices.ARCHIVED
        ]
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now() and not self.is_closed
    
    @property
    def can_be_published(self):
        """Check if assignment has all required fields for publishing"""
        required_fields = ['title', 'subject', 'teacher', 'due_date', 'total_marks']
        for field in required_fields:
            if not getattr(self, field):
                return False
        
        if not self.classroom:
            return False
            
        return True
    
    @property
    def total_students(self):
        """Total number of students in the classroom"""
        if not self.classroom:
            return 0
        
        from students.models import StudentEnrollment
        
        if not hasattr(self, '_total_students_cache'):
            self._total_students_cache = StudentEnrollment.objects.filter(
                class_enrolled=self.classroom,
                status='active',
                academic_year=self.academic_year
            ).count()
        
        return self._total_students_cache
    
    @property
    def submission_stats(self):
        """Get comprehensive submission statistics"""
        from django.db.models import Count, Q
        
        stats = self.student_assignments.aggregate(
            total=Count('id'),
            submitted=Count('id', filter=Q(status__in=['submitted', 'late', 'graded'])),
            late=Count('id', filter=Q(status='late')),
            graded=Count('id', filter=Q(status='graded')),
            not_submitted=Count('id', filter=Q(status='not_submitted')),
        )
        
        return {
            'total': self.total_students,
            'submitted': stats['submitted'],
            'late': stats['late'],
            'graded': stats['graded'],
            'not_submitted': stats['not_submitted'],
            'submission_rate': round((stats['submitted'] / self.total_students * 100), 2) if self.total_students > 0 else 0,
            'grading_rate': round((stats['graded'] / stats['submitted'] * 100), 2) if stats['submitted'] > 0 else 0,
        }
    
    @property
    def grade_summary(self):
        """Get grade distribution summary"""
        from django.db.models import Count, Q
        from decimal import Decimal
        
        graded = self.student_assignments.filter(
            status='graded',
            marks_obtained__isnull=False
        )
        
        if not graded.exists():
            return {
                'grades': {},
                'average': 0,
                'highest': 0,
                'lowest': 0,
                'pass_count': 0,
                'fail_count': 0
            }
        
        # Grade categories based on percentage
        grade_categories = {
            'A': Q(marks_obtained__gte=Decimal('80')),
            'B': Q(marks_obtained__gte=Decimal('70'), marks_obtained__lt=Decimal('80')),
            'C': Q(marks_obtained__gte=Decimal('60'), marks_obtained__lt=Decimal('70')),
            'D': Q(marks_obtained__gte=Decimal('50'), marks_obtained__lt=Decimal('60')),
            'F': Q(marks_obtained__lt=Decimal('50'))
        }
        
        grades = {}
        for grade, query in grade_categories.items():
            grades[grade] = graded.filter(query).count()
        
        stats = graded.aggregate(
            avg=models.Avg('marks_obtained'),
            max=models.Max('marks_obtained'),
            min=models.Min('marks_obtained'),
            pass_count=Count('id', filter=Q(marks_obtained__gte=self.passing_marks)),
            fail_count=Count('id', filter=Q(marks_obtained__lt=self.passing_marks))
        )
        
        return {
            'grades': grades,
            'average': float(stats['avg'] or 0),
            'highest': float(stats['max'] or 0),
            'lowest': float(stats['min'] or 0),
            'pass_count': stats['pass_count'] or 0,
            'fail_count': stats['fail_count'] or 0,
            'pass_rate': round((stats['pass_count'] / graded.count() * 100), 2) if graded.count() > 0 else 0
        }
    
    @property
    def days_until_due(self):
        """Days remaining until due date (negative if overdue)"""
        if not self.due_date:
            return None
        
        delta = self.due_date - timezone.now()
        return delta.days
    
    # ====================
    # METHODS
    # ====================
    
    def clean(self):
        """Validate assignment data"""
        errors = {}
        
        # Validate dates
        if self.due_date and self.due_date < timezone.now():
            errors['due_date'] = _('Due date cannot be in the past.')
        
        # Validate marks
        if self.passing_marks and self.total_marks:
            if self.passing_marks > self.total_marks:
                errors['passing_marks'] = _('Passing marks cannot exceed total marks.')
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Override save to handle status transitions"""
        is_new = self.pk is None
        
        # Handle status transitions
        if self.status == self.StatusChoices.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        
        if self.status in [self.StatusChoices.CLOSED, self.StatusChoices.GRADED] and not self.closed_at:
            self.closed_at = timezone.now()
        
        if not self.is_active and self.status != self.StatusChoices.ARCHIVED:
            self.status = self.StatusChoices.ARCHIVED
        
        super().save(*args, **kwargs)
        
        # Create student assignments after save if published and new
        if self.status == self.StatusChoices.PUBLISHED and self.classroom and is_new:
            self.create_student_assignments()
    
    def create_student_assignments(self, batch_size=100):
        """
        Create student assignments for all students in the classroom
        """
        if not self.classroom:
            return 0, 0
        
        from students.models import StudentEnrollment
        
        enrollments = StudentEnrollment.objects.filter(
            class_enrolled=self.classroom,
            status='active',
            academic_year=self.academic_year
        ).select_related('student_profile__user')
        
        existing_student_ids = set(
            self.student_assignments.values_list('student_id', flat=True)
        )
        
        assignments_to_create = []
        
        for enrollment in enrollments:
            student_user = enrollment.student_profile.user
            
            if student_user.id in existing_student_ids:
                continue
            
            assignments_to_create.append(
                StudentAssignment(
                    assignment=self,
                    student=student_user,
                    status='not_submitted'
                )
            )
            
            if len(assignments_to_create) >= batch_size:
                StudentAssignment.objects.bulk_create(
                    assignments_to_create,
                    ignore_conflicts=True
                )
                assignments_to_create = []
        
        if assignments_to_create:
            StudentAssignment.objects.bulk_create(
                assignments_to_create,
                ignore_conflicts=True
            )
        
        return len(assignments_to_create), len(existing_student_ids)
    
    def update_statistics(self):
        """Update cached statistics for this assignment"""
        from django.db.models import Avg, Count, Q
        
        # Update completion rate
        total = self.total_students
        submitted = self.student_assignments.filter(
            status__in=['submitted', 'late', 'graded']
        ).count()
        
        self.completion_rate = (submitted / total * 100) if total > 0 else 0
        
        # Update average score
        graded = self.student_assignments.filter(
            status='graded',
            marks_obtained__isnull=False
        )
        
        if graded.exists():
            avg = graded.aggregate(avg=Avg('marks_obtained'))['avg']
            self.average_score = avg or 0
        else:
            self.average_score = 0
        
        self.save(update_fields=['completion_rate', 'average_score', 'updated_at'])


class StudentAssignment(BaseAssignmentModel):
    """Student assignment submission model"""
    
    SUBMISSION_STATUS = [
        ('not_submitted', 'Not Submitted'),
        ('submitted', 'Submitted'),
        ('late', 'Submitted Late'),
        ('graded', 'Graded'),
        ('returned', 'Returned for Revision'),
        ('resubmitted', 'Resubmitted'),
    ]
    
    assignment = models.ForeignKey(
        Assignment, 
        on_delete=models.CASCADE, 
        related_name='student_assignments'
    )
    
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_assignments',
        limit_choices_to={'role': 'student'}
    )
    
    # Group assignment support
    group = models.ForeignKey(
        'AssignmentGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='group_assignments',
        verbose_name=_('Group')
    )
    
    # Submission details
    submission_date = models.DateTimeField(null=True, blank=True)
    submission_text = models.TextField(blank=True)
    submission_file = models.FileField(upload_to=submission_file_path, blank=True, null=True)
    attachments = models.JSONField(
        blank=True,
        null=True,
        help_text=_("JSON array of additional attachment URLs"),
        verbose_name=_('Additional Attachments')
    )
    
    # Grading
    marks_obtained = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    final_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_('Final Marks'),
        help_text=_("Marks after applying penalties or bonuses")
    )
    
    # Feedback
    feedback = models.TextField(blank=True, verbose_name=_('Feedback'))
    comments = models.TextField(blank=True, verbose_name=_('Internal Comments'))
    
    # Grading details
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='graded_student_assignments',
        verbose_name=_('Graded By')
    )
    
    graded_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Graded At'))
    
    # Resubmission tracking
    resubmission_count = models.PositiveIntegerField(default=0, verbose_name=_('Resubmission Count'))
    last_resubmission_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Last Resubmission Date'))
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=SUBMISSION_STATUS, 
        default='not_submitted',
        verbose_name=_('Status')
    )
    
    # Late submission tracking
    is_late = models.BooleanField(default=False, verbose_name=_('Is Late Submission'))
    late_penalty_applied = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Late Penalty Applied')
    )
    
    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submission_date']
        verbose_name = _('Student Assignment')
        verbose_name_plural = _('Student Assignments')
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['assignment', 'status']),
            models.Index(fields=['group', 'assignment']),
            models.Index(fields=['submission_date']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assignment.title}"
    
    @property
    def is_submitted(self):
        return self.status in ['submitted', 'late', 'graded', 'returned', 'resubmitted']
    
    @property
    def percentage(self):
        if self.marks_obtained and self.assignment.total_marks and self.assignment.total_marks > 0:
            return (self.marks_obtained / self.assignment.total_marks) * 100
        return 0
    
    @property
    def final_percentage(self):
        """Calculate final percentage after penalties"""
        if self.final_marks and self.assignment.total_marks and self.assignment.total_marks > 0:
            return (self.final_marks / self.assignment.total_marks) * 100
        return self.percentage
    
    @property
    def grade(self):
        """Calculate letter grade based on percentage"""
        percentage = self.final_percentage
        
        if percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 50:
            return 'D'
        else:
            return 'F'
    
    @property
    def is_passing(self):
        """Check if assignment is passing"""
        return self.final_percentage >= 40  # Assuming 40% is passing
    
    @property
    def days_late(self):
        """Calculate how many days late the submission was"""
        if not self.submission_date or not self.assignment.due_date:
            return 0
        
        if self.submission_date > self.assignment.due_date:
            delta = self.submission_date - self.assignment.due_date
            return delta.days
        return 0
    
    def clean(self):
        """Validate student assignment data"""
        errors = {}
        
        # Validate marks
        if self.marks_obtained:
            if self.marks_obtained > self.assignment.total_marks:
                errors['marks_obtained'] = _('Marks obtained cannot exceed total marks.')
        
        if self.final_marks:
            if self.final_marks > self.assignment.total_marks:
                errors['final_marks'] = _('Final marks cannot exceed total marks.')
        
        # Validate resubmission count
        if self.resubmission_count > self.assignment.max_resubmissions:
            errors['resubmission_count'] = _('Resubmission count exceeds maximum allowed.')
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Override save to handle status transitions and calculations"""
        # Set final marks if not set
        if self.marks_obtained and not self.final_marks:
            self.final_marks = self.marks_obtained
        
        # Apply late penalty if needed
        if self.is_late and self.assignment.allow_late_submission:
            if self.assignment.late_submission_penalty > 0 and not self.late_penalty_applied:
                penalty = (self.final_marks * self.assignment.late_submission_penalty) / 100
                self.final_marks = max(0, self.final_marks - penalty)
                self.late_penalty_applied = self.assignment.late_submission_penalty
        
        # Update status if needed
        if self.marks_obtained and self.status != 'graded':
            self.status = 'graded'
            if not self.graded_at:
                self.graded_at = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Update assignment statistics
        if self.status == 'graded' or self.status in ['submitted', 'late']:
            self.assignment.update_statistics()


class AssignmentGroup(BaseAssignmentModel):
    """Group for collaborative assignments"""
    
    name = models.CharField(max_length=100, verbose_name=_('Group Name'))
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name=_('Assignment')
    )
    
    leader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='led_groups',
        verbose_name=_('Group Leader')
    )
    
    members = models.ManyToManyField(
        User,
        limit_choices_to={'role': 'student'},
        related_name='group_memberships',
        through='GroupMembership',
        verbose_name=_('Group Members')
    )
    
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    
    class Meta:
        verbose_name = _('Assignment Group')
        verbose_name_plural = _('Assignment Groups')
        unique_together = ['assignment', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.assignment.title}"
    
    @property
    def member_count(self):
        return self.members.count() + 1  # +1 for leader
    
    def clean(self):
        """Validate group data"""
        if self.assignment and not self.assignment.is_group_assignment:
            raise ValidationError(_('This assignment does not allow groups.'))
        
        if self.assignment and self.member_count > self.assignment.max_group_size:
            raise ValidationError(
                _('Group size exceeds maximum allowed for this assignment.')
            )
    
    def save(self, *args, **kwargs):
        """Ensure leader is added as member"""
        super().save(*args, **kwargs)
        
        # Add leader as member if not already
        if self.leader not in self.members.all():
            self.members.add(self.leader)


class GroupMembership(BaseAssignmentModel):
    """Through model for group memberships"""
    
    group = models.ForeignKey(
        AssignmentGroup,
        on_delete=models.CASCADE,
        verbose_name=_('Group')
    )
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='assignment_group_memberships',
        verbose_name=_('Student')
    )
    
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Joined At'))
    role = models.CharField(
        max_length=20,
        choices=[
            ('member', 'Member'),
            ('secretary', 'Secretary'),
            ('treasurer', 'Treasurer'),
        ],
        default='member',
        verbose_name=_('Role')
    )
    
    class Meta:
        verbose_name = _('Group Membership')
        verbose_name_plural = _('Group Memberships')
        unique_together = ['group', 'student']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.group.name}"


class AssignmentComment(BaseAssignmentModel):
    """Comments and discussions on assignments"""
    
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Assignment')
    )
    
    student_assignment = models.ForeignKey(
        StudentAssignment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='assignment_comments',
        verbose_name=_('Student Assignment')
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignment_comments',
        verbose_name=_('Author')
    )
    
    content = models.TextField(verbose_name=_('Content'))
    
    is_private = models.BooleanField(
        default=False,
        verbose_name=_('Is Private'),
        help_text=_('Private comments are only visible to teachers')
    )
    
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('Parent Comment')
    )
    
    attachments = models.JSONField(
        blank=True,
        null=True,
        help_text=_("JSON array of attachment URLs"),
        verbose_name=_('Attachments')
    )
    
    class Meta:
        verbose_name = _('Assignment Comment')
        verbose_name_plural = _('Assignment Comments')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.get_full_name()} on {self.assignment.title}"


class AssignmentAnalytics(BaseAssignmentModel):
    """Analytics data for assignments"""
    
    ANALYTICS_TYPES = [
        ('submission_rates', 'Submission Rates'),
        ('grade_distribution', 'Grade Distribution'),
        ('completion_time', 'Completion Time'),
        ('student_performance', 'Student Performance'),
        ('question_analysis', 'Question Analysis'),
        ('overall_summary', 'Overall Summary'),
        ('difficulty_analysis', 'Difficulty Analysis'),
    ]
    
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='analytics',
        verbose_name=_('Assignment')
    )
    
    analytics_type = models.CharField(
        max_length=50,
        choices=ANALYTICS_TYPES,
        default='submission_rates',
        verbose_name=_('Analytics Type')
    )
    
    data = models.JSONField(
        default=dict,
        verbose_name=_('Analytics Data')
    )
    
    period_start = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Period Start')
    )
    
    period_end = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Period End')
    )
    
    # FIXED: Remove the default value since we have auto_now_add=True
    generated_at = models.DateTimeField(
        auto_now_add=True,  # This automatically sets the date when object is created
        verbose_name=_('Generated At')
    )
    
    class Meta:
        verbose_name = _('Assignment Analytics')
        verbose_name_plural = _('Assignment Analytics')
        unique_together = ['assignment', 'analytics_type', 'period_start', 'period_end']
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"Analytics for {self.assignment.title} ({self.analytics_type})"

class AssignmentReminder(BaseAssignmentModel):
    """Reminders for assignments"""
    
    REMINDER_TYPES = [
        ('submission', 'Submission Reminder'),
        ('grading', 'Grading Reminder'),
        ('upcoming', 'Upcoming Deadline'),
        ('overdue', 'Overdue Assignment'),
    ]
    
    DELIVERY_METHODS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    ]
    
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='reminders',
        verbose_name=_('Assignment')
    )
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={'role': 'student'},
        related_name='assignment_reminders',
        verbose_name=_('Student')
    )
    
    classroom = models.ForeignKey(
        'academics.Class',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='assignment_reminders',
        verbose_name=_('Classroom')
    )
    
    reminder_type = models.CharField(
        max_length=20,
        choices=REMINDER_TYPES,
        default='submission',
        verbose_name=_('Reminder Type')
    )
    
    message = models.TextField(verbose_name=_('Message'))
    
    scheduled_for = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Scheduled For')
    )
    
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Sent At'))
    
    sent_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_reminders',
        verbose_name=_('Sent By')
    )
    
    is_sent = models.BooleanField(default=False, verbose_name=_('Is Sent'))
    
    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_METHODS,
        default='in_app',
        verbose_name=_('Delivery Method')
    )
    
    class Meta:
        verbose_name = _('Assignment Reminder')
        verbose_name_plural = _('Assignment Reminders')
        ordering = ['scheduled_for']
        indexes = [
            models.Index(fields=['scheduled_for', 'is_sent']),
            models.Index(fields=['assignment', 'student']),
        ]
    
    def __str__(self):
        return f"Reminder for {self.assignment.title} ({self.reminder_type})"
    
    def clean(self):
        """Validate reminder data"""
        if not self.student and not self.classroom:
            raise ValidationError(_('Either a student or classroom must be specified.'))
        
        if self.student and self.classroom:
            raise ValidationError(_('Specify either a student or a classroom, not both.'))
    
    def mark_as_sent(self):
        """Mark reminder as sent"""
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save()
    
    @property
    def is_overdue(self):
        """Check if reminder is overdue for sending"""
        return not self.is_sent and self.scheduled_for < timezone.now()
    
    @property
    def recipient_display(self):
        """Display recipient information"""
        if self.student:
            return self.student.get_full_name()
        elif self.classroom:
            return self.classroom.name
        return _('No recipient specified')