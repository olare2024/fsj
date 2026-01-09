# assignments/models.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from students.models import StudentEnrollment
from django.db import transaction
from django.db.models import Q, Avg, Count, Sum
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import os

# FIXED: Import Class instead of ClassRoom, and use string references to avoid circular imports
from academics.models import AcademicTerm, AcademicYear
from accounts.models import User




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
    def get_queryset(self):
        return AssignmentQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def published(self):
        return self.get_queryset().published()
    
    def for_student(self, student):
        return self.get_queryset().for_student(student)
    
    def overdue(self):
        return self.get_queryset().overdue()
class AssignmentManager(models.Manager):
    """Custom manager for Assignment model with optimized queries"""
    
    def get_queryset(self):
        """Return base queryset with common select_related and prefetch_related"""
        return super().get_queryset().select_related(
            'subject', 'teacher', 'classroom', 'academic_year', 'term', 'category', 'created_by'
        )
    
    def active(self):
        """Get active assignments"""
        return self.get_queryset().filter(is_active=True)
    
    def published(self):
        """Get published assignments"""
        return self.active().filter(status='published')
    
    def for_teacher(self, teacher):
        """Get assignments for a specific teacher"""
        return self.active().filter(teacher=teacher)
    
    def for_classroom(self, classroom):
        """Get assignments for a specific classroom"""
        return self.active().filter(classroom=classroom)
    
    def for_student(self, student):
        """
        Get assignments for a specific student based on enrollment
        Returns empty queryset if student not enrolled
        """
        from students.models import StudentEnrollment
        
        enrollment = StudentEnrollment.objects.filter(
            student__user=student,
            status='active'
        ).first()
        
        if enrollment:
            return self.published().filter(
                classroom=enrollment.class_enrolled,
                academic_year=enrollment.academic_year,
                term=enrollment.current_term
            )
        return self.none()
    
    def overdue(self):
        """Get overdue assignments"""
        from django.utils import timezone
        return self.published().filter(
            due_date__lt=timezone.now(),
            status__in=['published', 'in_progress']
        )
    
    def upcoming(self, days=7):
        """Get assignments due within specified days"""
        from django.utils import timezone
        from django.db.models import Q
        
        now = timezone.now()
        future_date = now + timezone.timedelta(days=days)
        
        return self.published().filter(
            Q(due_date__gte=now) & Q(due_date__lte=future_date)
        )
    
    def with_submission_stats(self):
        """Annotate queryset with submission statistics"""
        from django.db.models import Count, Q, F
        
        return self.get_queryset().annotate(
            total_students_count=Count('classroom__student_enrollments', 
                                     filter=Q(classroom__student_enrollments__status='active')),
            submitted_count=Count('student_assignments',
                                filter=Q(student_assignments__status__in=['submitted', 'late', 'graded'])),
            graded_count=Count('student_assignments',
                             filter=Q(student_assignments__status='graded')),
            submission_rate=F('submitted_count') * 100.0 / F('total_students_count'),
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
    
    # Basic Information Fields
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
    
    # Academic Context Fields
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name=_('Subject')
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='assignments_created',
        verbose_name=_('Teacher')
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
        AcademicYear,
        on_delete=models.CASCADE,
        verbose_name=_('Academic Year')
    )
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE, verbose_name=_('AcademicTerm'))
    curriculum = models.CharField(
        max_length=10,
        choices=CurriculumChoices.choices,
        default=CurriculumChoices.CBC,
        verbose_name=_('Curriculum')
    )
    
    # Assignment Details Fields
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
    
    # Content Fields
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
    
    # Kenya CBC Competencies Fields
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
    
    # Creation and Ownership
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_assignments',
        verbose_name=_('Created By')
    )
    
    # Attachment Fields
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
    
    # Submission Settings Fields
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
    
    # Status and Tracking Fields
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name=_('Status')
    )
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Published At'))
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Closed At'))
    
    # Analytics Fields (cached values)
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
    
    # Approval Workflow Fields
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__in': ['admin', 'head_teacher']},
        related_name='approved_assignments',
        verbose_name=_('Approved By')
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Approved At'))
    
    # Custom Manager
    objects = AssignmentManager()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')
        indexes = [
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['subject', 'term']),
            models.Index(fields=['teacher', 'created_at']),
            models.Index(fields=['curriculum', 'classroom']),
            models.Index(fields=['is_active']),
            models.Index(fields=['due_date', 'status', 'is_active']),
            models.Index(fields=['teacher', 'status', 'due_date']),
            models.Index(fields=['classroom', 'subject', 'due_date']),
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
    
    # ================ STRING REPRESENTATION ================
    def __str__(self):
        return f"{self.title} - {self.subject.name} - {self.term}"
    
    # ================ VALIDATION METHODS ================
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
        
        # Validate group assignment settings
        if self.is_group_assignment:
            if self.max_group_size < 2:
                errors['max_group_size'] = _('Group assignments require at least 2 students per group.')
            if not self.classroom:
                errors['classroom'] = _('Group assignments require a classroom to be specified.')
        
        # Validate curriculum alignment
        if self.category and self.category.curriculum != self.curriculum:
            errors['category'] = _(
                f'Category curriculum ({self.category.curriculum}) does not match '
                f'assignment curriculum ({self.curriculum})'
            )
        
        if errors:
            raise ValidationError(errors)
    
    # ================ SAVE OVERRIDE ================
    def save(self, *args, **kwargs):
        """Override save to handle status transitions and auto-updates"""
        is_new = self.pk is None
        
        # Handle status transitions
        if self.status == self.StatusChoices.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        
        if self.status in [self.StatusChoices.CLOSED, self.StatusChoices.GRADED] and not self.closed_at:
            self.closed_at = timezone.now()
        
        if not self.is_active and self.status != self.StatusChoices.ARCHIVED:
            self.status = self.StatusChoices.ARCHIVED
        
        # Auto-update analytics when publishing
        if is_new and self.status == self.StatusChoices.PUBLISHED:
            self.update_analytics()
        
        super().save(*args, **kwargs)
        
        # Create student assignments after save if published
        if self.status == self.StatusChoices.PUBLISHED and self.classroom and is_new:
            self.create_student_assignments()
    
    # ================ STUDENT ASSIGNMENT MANAGEMENT ================
    def create_student_assignments(self, batch_size=100):
        """
        Create student assignments for all students in the classroom
        Returns: (created_count, skipped_count)
        """
        if not self.classroom:
            return 0, 0
        
        from students.models import StudentEnrollment
        from django.db import transaction
        
        # Get active student enrollments
        enrollments = StudentEnrollment.objects.filter(
            class_enrolled=self.classroom,
            status='active',
            academic_year=self.academic_year
        ).select_related('student__user').only('student__user_id')
        
        # Get existing student assignments to avoid duplicates
        existing_student_ids = set(
            self.student_assignments.values_list('student_id', flat=True)
        )
        
        assignments_to_create = []
        
        with transaction.atomic():
            for enrollment in enrollments:
                student_id = enrollment.student.user_id
                
                # Skip if already exists
                if student_id in existing_student_ids:
                    continue
                
                assignments_to_create.append(
                    StudentAssignment(
                        assignment=self,
                        student_id=student_id,
                        status='not_submitted'
                    )
                )
                
                # Bulk create in batches
                if len(assignments_to_create) >= batch_size:
                    StudentAssignment.objects.bulk_create(
                        assignments_to_create,
                        ignore_conflicts=True
                    )
                    assignments_to_create = []
            
            # Create remaining assignments
            if assignments_to_create:
                StudentAssignment.objects.bulk_create(
                    assignments_to_create,
                    ignore_conflicts=True
                )
        
        created_count = len(assignments_to_create)
        skipped_count = len(existing_student_ids)
        
        return created_count, skipped_count
    
    def get_student_assignment(self, student):
        """
        Get or create student assignment for a specific student
        Returns: StudentAssignment instance
        """
        return self.student_assignments.get_or_create(
            student=student,
            defaults={'status': 'not_submitted'}
        )[0]
    
    def bulk_update_grades(self, grade_data, graded_by=None):
        """
        Bulk update grades for multiple students
        grade_data: dict of {student_id: marks_obtained}
        """
        from django.db import transaction, models
        
        if not grade_data:
            return 0
        
        now = timezone.now()
        updated_count = 0
        
        with transaction.atomic():
            # Get all student assignments for these students
            student_ids = list(grade_data.keys())
            assignments = self.student_assignments.filter(
                student_id__in=student_ids
            ).select_for_update()
            
            # Create a mapping for quick access
            assignment_map = {ass.student_id: ass for ass in assignments}
            
            updates = []
            for student_id, marks in grade_data.items():
                assignment = assignment_map.get(student_id)
                if assignment:
                    assignment.marks_obtained = marks
                    assignment.status = StudentAssignment.SUBMISSION_STATUS[3][0]  # 'graded'
                    assignment.graded_at = now
                    if graded_by:
                        assignment.graded_by = graded_by
                    updates.append(assignment)
            
            # Bulk update
            if updates:
                StudentAssignment.objects.bulk_update(
                    updates,
                    ['marks_obtained', 'status', 'graded_at', 'graded_by', 'updated_at']
                )
                updated_count = len(updates)
                
                # Update assignment analytics
                self.update_analytics()
        
        return updated_count
    
    # ================ ANALYTICS METHODS ================
    def get_average_score(self, force_recalculate=False):
        """
        Calculate average score from graded assignments
        force_recalculate: If True, ignores cached value and recalculates
        """
        if not force_recalculate and self.average_score > 0:
            return self.average_score
        
        from django.db.models import Avg
        
        avg = self.student_assignments.filter(
            status='graded',
            marks_obtained__isnull=False
        ).aggregate(avg_score=Avg('marks_obtained'))['avg_score']
        
        return round(avg or 0, 2)
    
    def get_completion_rate(self, force_recalculate=False):
        """
        Calculate completion rate
        force_recalculate: If True, ignores cached value and recalculates
        """
        if not force_recalculate and self.completion_rate > 0:
            return self.completion_rate
        
        total_students = self.total_students
        if total_students == 0:
            return 0
        
        submitted_count = self.student_assignments.filter(
            status__in=['submitted', 'late', 'graded']
        ).count()
        
        return round((submitted_count / total_students) * 100, 2)
    
    def update_analytics(self):
        """Update all analytics fields"""
        self.average_score = self.get_average_score(force_recalculate=True)
        self.completion_rate = self.get_completion_rate(force_recalculate=True)
        self.save(update_fields=['average_score', 'completion_rate', 'updated_at'])
    
    # ================ PROPERTIES ================
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
    def is_due_soon(self):
        """Check if assignment is due within 24 hours"""
        if not self.due_date or self.is_closed:
            return False
        
        time_remaining = self.due_date - timezone.now()
        return 0 < time_remaining.total_seconds() <= 86400  # 24 hours
    
    @property
    def days_until_due(self):
        """Days remaining until due date (negative if overdue)"""
        if not self.due_date:
            return None
        
        delta = self.due_date - timezone.now()
        return delta.days
    
    @property
    def total_students(self):
        """Total number of students in the classroom"""
        if not self.classroom:
            return 0
        
        from students.models import StudentEnrollment
        
        # Cache the result for this instance
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
        
        total_students = self.total_students
        
        return {
            'total': total_students,
            'submitted': stats['submitted'],
            'late': stats['late'],
            'graded': stats['graded'],
            'not_submitted': stats['not_submitted'],
            'submission_rate': round((stats['submitted'] / total_students * 100), 2) if total_students > 0 else 0,
            'grading_rate': round((stats['graded'] / stats['submitted'] * 100), 2) if stats['submitted'] > 0 else 0,
            'late_rate': round((stats['late'] / total_students * 100), 2) if total_students > 0 else 0,
        }
    
    @property
    def grade_summary(self):
        """Get grade distribution summary"""
        from django.db.models import Count, Q, Avg, Max, Min
        
        graded_assignments = self.student_assignments.filter(status='graded')
        
        if not graded_assignments.exists():
            return {}
        
        summary = graded_assignments.aggregate(
            total=Count('id'),
            passed=Count('id', filter=Q(final_marks__gte=self.passing_marks)),
            failed=Count('id', filter=Q(final_marks__lt=self.passing_marks)),
            avg_score=Avg('final_marks'),
            max_score=Max('final_marks'),
            min_score=Min('final_marks'),
            avg_percentage=Avg('percentage'),
        )
        
        summary['pass_rate'] = round((summary['passed'] / summary['total']) * 100, 2)
        return summary
    
    @property
    def can_be_published(self):
        """Check if assignment can be published"""
        return (
            self.status in [self.StatusChoices.DRAFT, self.StatusChoices.IN_PROGRESS] and
            self.title and
            self.subject and
            self.due_date and
            self.due_date > timezone.now() and
            self.total_marks > 0
        )
    
    @property
    def requires_approval(self):
        """Check if assignment requires approval before publishing"""
        return self.require_approval and not self.approved_by
    
    @property
    def extension_allowed(self):
        """Check if extensions are allowed"""
        return self.allow_late_submission and not self.is_closed
    
    # ================ UTILITY METHODS ================
    def get_submission_deadline_extended(self, days=0, hours=0):
        """Calculate extended deadline"""
        from datetime import timedelta
        return self.due_date + timedelta(days=days, hours=hours)
    
    def publish(self):
        """Publish the assignment"""
        if self.can_be_published:
            self.status = self.StatusChoices.PUBLISHED
            self.save()
            return True
        return False
    
    def close(self):
        """Close the assignment"""
        if self.status in [self.StatusChoices.PUBLISHED, self.StatusChoices.IN_PROGRESS]:
            self.status = self.StatusChoices.CLOSED
            self.save()
            return True
        return False
    
    def archive(self):
        """Archive the assignment"""
        self.is_active = False
        self.status = self.StatusChoices.ARCHIVED
        self.save()
        return True
    
    def duplicate(self, new_title=None):
        """
        Create a duplicate of this assignment
        Returns: New Assignment instance
        """
        from django.db import transaction
        
        with transaction.atomic():
            # Create copy
            new_assignment = Assignment.objects.create(
                title=new_title or f"Copy of {self.title}",
                description=self.description,
                assignment_type=self.assignment_type,
                category=self.category,
                subject=self.subject,
                teacher=self.teacher,
                classroom=self.classroom,
                stream=self.stream,
                academic_year=self.academic_year,
                term=self.term,
                curriculum=self.curriculum,
                due_date=self.due_date,
                total_marks=self.total_marks,
                passing_marks=self.passing_marks,
                difficulty_level=self.difficulty_level,
                estimated_completion_time=self.estimated_completion_time,
                instructions=self.instructions,
                learning_objectives=self.learning_objectives,
                resources=self.resources,
                rubric=self.rubric,
                competencies=self.competencies,
                core_competencies=self.core_competencies,
                created_by=self.created_by,
                allow_late_submission=self.allow_late_submission,
                late_submission_penalty=self.late_submission_penalty,
                allow_resubmission=self.allow_resubmission,
                max_resubmissions=self.max_resubmissions,
                require_approval=self.require_approval,
                is_group_assignment=self.is_group_assignment,
                max_group_size=self.max_group_size,
                status=self.StatusChoices.DRAFT,
            )
            
            return new_assignment

class StudentAssignment(BaseAssignmentModel):
    """Enhanced student submission for assignments"""
    
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
        related_name='submissions'
    )
    is_group_submission = models.BooleanField(default=False)
    
    # Submission details
    submission_date = models.DateTimeField(null=True, blank=True)
    submission_text = models.TextField(blank=True)
    submission_file = models.FileField(upload_to=submission_file_path, blank=True, null=True)
    submission_files = models.JSONField(
        blank=True, 
        null=True, 
        help_text="JSON array of multiple submission files"
    )
    word_count = models.PositiveIntegerField(default=0)
    character_count = models.PositiveIntegerField(default=0)
    
    # Version control
    version = models.PositiveIntegerField(default=1)
    previous_version = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='next_versions'
    )
    
    # Grading
    marks_obtained = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    penalty_points = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    final_marks = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    grade = models.CharField(max_length=5, blank=True)
    grade_points = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(4)]
    )
    
    # Kenya grading system
    kcpe_points = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    kcse_grade = models.CharField(max_length=2, blank=True)
    
    # Feedback
    teacher_feedback = models.TextField(blank=True)
    rubric_scores = models.JSONField(blank=True, null=True, help_text="Scores for each rubric criterion")
    audio_feedback = models.FileField(
        upload_to='audio_feedback/', 
        blank=True, 
        null=True,
        help_text="Audio recording of teacher feedback"
    )
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUS, default='not_submitted')
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='graded_student_assignments'
    )
    
    # Student tracking
    time_spent = models.PositiveIntegerField(
        default=0, 
        help_text="Time spent in minutes",
        validators=[MinValueValidator(0)]
    )
    last_accessed = models.DateTimeField(null=True, blank=True)
    draft_saved = models.DateTimeField(null=True, blank=True)
    
    # System fields
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submission_date']
        verbose_name = _('Student Assignment')
        verbose_name_plural = _('Student Assignments')
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['assignment', 'status']),
            models.Index(fields=['grade', 'created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assignment.title}"
    
    def clean(self):
        """Validate submission data"""
        errors = {}
        
        if self.marks_obtained and self.assignment.total_marks:
            if self.marks_obtained > self.assignment.total_marks:
                errors['marks_obtained'] = f'Marks obtained cannot exceed total marks ({self.assignment.total_marks}).'
        
        if self.submission_date and self.assignment.due_date:
            if self.submission_date > self.assignment.due_date and not self.assignment.allow_late_submission:
                errors['submission_date'] = 'Late submissions are not allowed for this assignment.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Override save to handle calculations and status updates"""
        # Calculate word and character counts
        if self.submission_text:
            self.word_count = len(self.submission_text.split())
            self.character_count = len(self.submission_text)
        
        # Calculate final marks with penalty
        if self.marks_obtained is not None:
            self.final_marks = max(0, self.marks_obtained - self.penalty_points)
            
            # Auto-calculate grade if not set
            if not self.grade and self.final_marks and self.assignment.total_marks:
                self._calculate_grade()
        
        # Update status based on submission
        if self.submission_date and not self.is_submitted:
            if self.submission_date > self.assignment.due_date:
                self.status = 'late'
            else:
                self.status = 'submitted'
        
        # Update version if this is a resubmission
        if self.status == 'resubmitted' and self.previous_version:
            self.version = self.previous_version.version + 1
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def _calculate_grade(self):
        """Calculate grade based on final marks"""
        percentage = self.percentage
        if percentage >= 80:
            self.grade = 'A'
            self.grade_points = 4.0
        elif percentage >= 75:
            self.grade = 'A-'
            self.grade_points = 3.7
        elif percentage >= 70:
            self.grade = 'B+'
            self.grade_points = 3.3
        elif percentage >= 65:
            self.grade = 'B'
            self.grade_points = 3.0
        elif percentage >= 60:
            self.grade = 'B-'
            self.grade_points = 2.7
        elif percentage >= 55:
            self.grade = 'C+'
            self.grade_points = 2.3
        elif percentage >= 50:
            self.grade = 'C'
            self.grade_points = 2.0
        elif percentage >= 45:
            self.grade = 'C-'
            self.grade_points = 1.7
        elif percentage >= 40:
            self.grade = 'D+'
            self.grade_points = 1.3
        elif percentage >= 35:
            self.grade = 'D'
            self.grade_points = 1.0
        else:
            self.grade = 'E'
            self.grade_points = 0.0
    
    @property
    def is_submitted(self):
        return self.status in ['submitted', 'late', 'graded', 'returned', 'resubmitted']
    
    @property
    def is_late(self):
        return self.status == 'late'
    
    @property
    def is_graded(self):
        return self.status == 'graded'
    
    @property
    def percentage(self):
        if self.final_marks and self.assignment.total_marks and self.assignment.total_marks > 0:
            return (self.final_marks / self.assignment.total_marks) * 100
        return 0
    
    @property
    def days_late(self):
        if self.is_late and self.submission_date and self.assignment.due_date:
            return (self.submission_date - self.assignment.due_date).days
        return 0
    
    @property
    def can_resubmit(self):
        """Check if student can resubmit"""
        return (self.assignment.allow_resubmission and 
                self.status in ['graded', 'returned'] and 
                self.version < self.assignment.max_resubmissions)


class AssignmentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    
    def published(self):
        return self.filter(status='published')
    
    def for_student(self, student):
        """Get assignments for a specific student"""
        from students.models import StudentEnrollment
        
        enrollment = StudentEnrollment.objects.filter(
            student__user=student,
            status='active'
        ).first()
        
        if enrollment:
            return self.filter(
                classroom=enrollment.class_enrolled,
                academic_year=enrollment.academic_year,
                term=enrollment.current_term
            )
        return self.none()
    
    def overdue(self):
        return self.filter(
            due_date__lt=timezone.now(),
            status__in=['published', 'in_progress']
        )

class AssignmentGroup(BaseAssignmentModel):
    """Group for collaborative assignments"""
    name = models.CharField(max_length=100)
    assignment = models.ForeignKey(
        Assignment, 
        on_delete=models.CASCADE, 
        related_name='groups'
    )
    leader = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='led_groups',
        limit_choices_to={'role': 'student'}
    )
    members = models.ManyToManyField(
        User, 
        through='GroupMembership', 
        related_name='assignment_groups_news',
        limit_choices_to={'role': 'student'}
    )
    
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_groups',
        limit_choices_to={'role': 'teacher'}
    )

    class Meta:
        unique_together = ['assignment', 'name']
        verbose_name = _('Assignment Group')
        verbose_name_plural = _('Assignment Groups')
        indexes = [
            models.Index(fields=['assignment', 'name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.assignment.title}"
    
    def clean(self):
        """Validate group data"""
        if self.assignment and not self.assignment.is_group_assignment:
            raise ValidationError('This assignment does not allow group work.')
    
    @property
    def member_count(self):
        return self.members.count()
    
    @property
    def is_full(self):
        return self.member_count >= self.assignment.max_group_size


class GroupMembership(BaseAssignmentModel):
    """Through model for group membership"""
    group = models.ForeignKey(AssignmentGroup, on_delete=models.CASCADE)
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='assignment_memberships',
        limit_choices_to={'role': 'student'}
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('member', 'Member'),
            ('co_leader', 'Co-Leader'),
            ('researcher', 'Researcher'),
            ('writer', 'Writer'),
            ('presenter', 'Presenter'),
        ],
        default='member'
    )
    
    class Meta:
        unique_together = ['group', 'student']
        verbose_name = _('Group Membership')
        verbose_name_plural = _('Group Memberships')
        indexes = [
            models.Index(fields=['group', 'student']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} in {self.group.name}"

class AssignmentGradeScale(BaseAssignmentModel):
    """Enhanced grade scale for assignments with Kenya education system support"""
    
    CURRICULUM_CHOICES = (
        ('cbc', 'CBC'),
        ('icse', 'ICSE'),
        ('american', 'American'),
        ('igcse', 'IGCSE'),
        ('combined', 'Combined'),
        ('ib', 'International Baccalaureate'),
        ('montessori', 'Montessori'),
    )
    
    name = models.CharField(max_length=100)
    curriculum = models.CharField(
        max_length=15,  # Increased to accommodate 'International Baccalaureate' length
        choices=CURRICULUM_CHOICES,  # Use local definition, not Assignment.CURRICULUM_CHOICES
        default='cbc'
    )
    min_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    grade = models.CharField(max_length=5)
    points = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(4)]
    )
    description = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=7, default='#6B7280', help_text="Hex color for display")
    
    # Kenya-specific grading
    kcpe_equivalent = models.CharField(max_length=10, blank=True, help_text="KCPE equivalent")
    kcse_equivalent = models.CharField(max_length=10, blank=True, help_text="KCSE equivalent")
    
    class Meta:
        ordering = ['curriculum', 'min_percentage']
        verbose_name = _('Grade Scale')
        verbose_name_plural = _('Grade Scales')
        unique_together = ['curriculum', 'min_percentage', 'max_percentage']
        indexes = [
            models.Index(fields=['curriculum', 'min_percentage']),
        ]
    
    def __str__(self):
        return f"{self.grade} ({self.min_percentage}% - {self.max_percentage}%) - {self.curriculum}"
    
    def clean(self):
        """Validate grade scale data"""
        if self.min_percentage >= self.max_percentage:
            raise ValidationError('Min percentage must be less than max percentage.')
        
        if self.min_percentage < 0 or self.max_percentage > 100:
            raise ValidationError('Percentages must be between 0 and 100.')


class AssignmentComment(BaseAssignmentModel):
    """Comments and discussions on assignments"""
    assignment = models.ForeignKey(
        Assignment, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    student_assignment = models.ForeignKey(
        StudentAssignment, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='comments'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='replies'
    )
    content = models.TextField()
    is_private = models.BooleanField(
        default=False, 
        help_text="Private comments are only visible to teachers"
    )
    file_attachment = models.FileField(
        upload_to='assignment_comments/', 
        blank=True, 
        null=True
    )
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('Assignment Comment')
        verbose_name_plural = _('Assignment Comments')
        indexes = [
            models.Index(fields=['assignment', 'created_at']),
            models.Index(fields=['author', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.get_full_name()} on {self.assignment.title}"
    
    @property
    def is_reply(self):
        return self.parent_comment is not None


class AssignmentAnalytics(BaseAssignmentModel):
    """Analytics data for assignments"""
    assignment = models.OneToOneField(
        Assignment, 
        on_delete=models.CASCADE, 
        related_name='analytics'
    )
    total_views = models.PositiveIntegerField(default=0)
    unique_viewers = models.PositiveIntegerField(default=0)
    average_time_spent = models.PositiveIntegerField(
        default=0, 
        help_text="In minutes"
    )
    common_issues = models.JSONField(
        blank=True, 
        null=True, 
        help_text="Common issues identified in submissions"
    )
    plagiarism_cases = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    average_completion_time = models.PositiveIntegerField(
        default=0, 
        help_text="Average time to complete in minutes"
    )
    question_analysis = models.JSONField(
        blank=True, 
        null=True, 
        help_text="Analysis of question performance"
    )
    
    # Engagement metrics
    average_score = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    submission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    class Meta:
        verbose_name = _('Assignment Analytics')
        verbose_name_plural = _('Assignment Analytics')
        indexes = [
            models.Index(fields=['assignment']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.assignment.title}"
    
    def update_analytics(self):
        """Update analytics data from assignment submissions"""
        submissions = self.assignment.student_assignments.all()
        
        if submissions.exists():
            # Calculate average score
            self.average_score = submissions.aggregate(
                avg_score=Avg('final_marks')
            )['avg_score'] or 0
            
            # Calculate submission rate
            total_students = self.assignment.total_students
            submitted_count = submissions.filter(
                status__in=['submitted', 'late', 'graded']
            ).count()
            self.submission_rate = (submitted_count / total_students * 100) if total_students > 0 else 0
            
            self.save()
    
    @property
    def last_updated(self):
        return self.updated_at


class AssignmentReminder(BaseAssignmentModel):
    """Automated reminders for assignments"""
    assignment = models.ForeignKey(
        Assignment, 
        on_delete=models.CASCADE, 
        related_name='reminders'
    )
    reminder_type = models.CharField(
        max_length=20,
        choices=[
            ('due_date', 'Due Date Reminder'),
            ('submission_deadline', 'Submission Deadline'),
            ('grading_reminder', 'Grading Reminder'),
            ('custom', 'Custom Reminder'),
        ]
    )
    reminder_date = models.DateTimeField()
    message = models.TextField()
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Target audience
    target_users = models.ManyToManyField(
        User, 
        blank=True, 
        related_name='assignment_reminders'
    )
    send_to_all_students = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['reminder_date']
        verbose_name = _('Assignment Reminder')
        verbose_name_plural = _('Assignment Reminders')
        indexes = [
            models.Index(fields=['reminder_date', 'sent']),
            models.Index(fields=['assignment', 'reminder_type']),
        ]
    
    def __str__(self):
        return f"Reminder for {self.assignment.title} - {self.reminder_date}"
    
    def clean(self):
        """Validate reminder data"""
        if self.reminder_date < timezone.now():
            raise ValidationError('Reminder date cannot be in the past.')
    
    @property
    def is_overdue(self):
        return self.reminder_date < timezone.now() and not self.sent
    
    def mark_sent(self):
        """Mark reminder as sent"""
        self.sent = True
        self.sent_at = timezone.now()
        self.save()