"""
students/models.py
Student models integrated with accounts system.
"""

import uuid
import logging
from datetime import timedelta
from decimal import Decimal
import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.apps import apps

from accounts.models import User


logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS AND CHOICES
# ============================================================================

# House Choices (matching accounts model)
HOUSE_CHOICES = [
    ('unity', 'Unity House'),
    ('courage', 'Courage House'),
    ('wisdom', 'Wisdom House'),
    ('success', 'Success House'),
    ('excellence', 'Excellence House'),
    ('integrity', 'Integrity House'),
    ('bravery', 'Bravery House'),
    ('honor', 'Honor House'),
]

# Enrollment Status Choices
ENROLLMENT_STATUS = (
    ('active', 'Active'),
    ('transferred', 'Transferred'),
    ('graduated', 'Graduated'),
    ('withdrawn', 'Withdrawn'),
    ('suspended', 'Suspended'),
    ('pending', 'Pending'),
    ('inactive', 'Inactive'),
)

# Grade Level Choices
GRADE_LEVEL_CHOICES = (
    ('pre_primary_1', 'Pre-Primary 1 (PP1)'),
    ('pre_primary_2', 'Pre-Primary 2 (PP2)'),
    ('grade_1', 'Grade 1'),
    ('grade_2', 'Grade 2'),
    ('grade_3', 'Grade 3'),
    ('grade_4', 'Grade 4'),
    ('grade_5', 'Grade 5'),
    ('grade_6', 'Grade 6'),
    ('grade_7', 'Grade 7'),
    ('grade_8', 'Grade 8'),
    ('grade_9', 'Grade 9'),
    ('grade_10', 'Grade 10 (Senior 1)'),
    ('grade_11', 'Grade 11 (Senior 2)'),
    ('grade_12', 'Grade 12 (Senior 3)'),
)

# Student Status Choices
STUDENT_STATUS = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('graduated', 'Graduated'),
    ('transferred', 'Transferred'),
    ('suspended', 'Suspended'),
    ('expelled', 'Expelled'),
    ('deceased', 'Deceased'),
)

# Gender Choices (matching accounts model)
GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

# Blood Group Choices (matching accounts model)
BLOOD_GROUP_CHOICES = (
    ('a_positive', 'A+'),
    ('a_negative', 'A-'),
    ('b_positive', 'B+'),
    ('b_negative', 'B-'),
    ('ab_positive', 'AB+'),
    ('ab_negative', 'AB-'),
    ('o_positive', 'O+'),
    ('o_negative', 'O-'),
)

# Disability Choices
DISABILITY_CHOICES = (
    ('none', 'No Disability'),
    ('physical', 'Physical Disability'),
    ('visual', 'Visual Impairment'),
    ('hearing', 'Hearing Impairment'),
    ('speech', 'Speech Impairment'),
    ('learning', 'Learning Disability'),
    ('intellectual', 'Intellectual Disability'),
    ('multiple', 'Multiple Disabilities'),
)

# Transportation Mode Choices
TRANSPORT_CHOICES = (
    ('school_bus', 'School Bus'),
    ('parent_drop', 'Parent Drop-off'),
    ('public_transport', 'Public Transport'),
    ('walking', 'Walking'),
    ('bicycle', 'Bicycle'),
    ('other', 'Other'),
)

# ============================================================================
# BASE MODEL
# ============================================================================

class BaseStudentModel(models.Model):
    """
    Abstract base model for student-related models with audit trail.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(class)s_entries',
        verbose_name=_("Created By")
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_%(class)s_entries',
        verbose_name=_("Updated By")
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']

    def get_audit_info(self):
        """
        Get audit information for the model.
        
        Returns:
            dict: Audit information including created/updated dates and users.
        """
        return {
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by.get_full_name() if self.created_by else 'System',
            'updated_by': self.updated_by.get_full_name() if self.updated_by else 'System'
        }

    def save(self, *args, **kwargs):
        """
        Auto-set audit fields if user is available in request.
        """
        from django.contrib.auth.models import AnonymousUser
        request = getattr(settings, 'CURRENT_REQUEST', None)
        
        if request and hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            if not self.pk and not self.created_by:
                self.created_by = request.user
            if not self.updated_by:
                self.updated_by = request.user
        
        super().save(*args, **kwargs)


# ============================================================================
# MAIN MODELS
# ============================================================================

class StudentProfile(models.Model):
    """
    Student Profile model integrated with accounts.User system.
    This model extends the User model with student-specific information.
    """
    
    # Core relationship with User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile_model',  # Different from accounts.StudentProfile
        verbose_name=_("User Account")
    )
    
    # ====================
    # Academic Information
    # ====================
    admission_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Admission Number"),
        help_text=_("Unique student admission number")
    )
    
    upi_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("UPI Number"),
        help_text=_("Unique Personal Identifier from NEMIS")
    )
    
    nemis_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("NEMIS Number"),
        help_text=_("National Education Management Information System number")
    )
    
    # Academic Relationships - Use string references
    current_class = models.ForeignKey(
        'academics.Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_students_profile',
        verbose_name=_("Current Class")
    )
    
    current_academic_year = models.ForeignKey(
        'academics.AcademicYear',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_year_students_profile',
        verbose_name=_("Current Academic Year")
    )
    
    # ====================
    # CBC-Specific Information
    # ====================
    cbc_pathway = models.CharField(
        max_length=20,
        choices=[
            ('stem', 'STEM Pathway'),
            ('social_sciences', 'Social Sciences Pathway'),
            ('arts_sports', 'Arts & Sports Pathway'),
            ('general', 'General Pathway'),
        ],
        blank=True,
        null=True,
        verbose_name=_("CBC Pathway")
    )
    
    portfolio_status = models.CharField(
        max_length=20,
        choices=[
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('submitted', 'Submitted'),
            ('reviewed', 'Reviewed'),
            ('completed', 'Completed'),
        ],
        default='not_started',
        verbose_name=_("Portfolio Status")
    )
    
    community_service_hours_completed = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Community Service Hours Completed")
    )
    
    # ====================
    # Academic Performance
    # ====================
    overall_grade = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("Overall Grade")
    )
    
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
        verbose_name=_("GPA")
    )
    
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Attendance Percentage")
    )
    
    rank_in_class = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Rank in Class")
    )
    
    # ====================
    # Academic History
    # ====================
    previous_grades = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Previous Grades")
    )
    
    test_scores = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Test Scores")
    )
    
    # ====================
    # Learning Preferences
    # ====================
    learning_style = models.CharField(
        max_length=50,
        choices=[
            ('visual', 'Visual'),
            ('auditory', 'Auditory'),
            ('kinesthetic', 'Kinesthetic'),
            ('reading_writing', 'Reading/Writing')
        ],
        blank=True,
        verbose_name=_("Learning Style")
    )
    
    strengths = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Academic Strengths")
    )
    
    weaknesses = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Areas for Improvement")
    )
    
    # ====================
    # Behavioral Information
    # ====================
    conduct_rating = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('satisfactory', 'Satisfactory'),
            ('needs_improvement', 'Needs Improvement')
        ],
        default='good',
        verbose_name=_("Conduct Rating")
    )
    
    behavioral_notes = models.TextField(
        blank=True,
        verbose_name=_("Behavioral Notes")
    )
    
    disciplinary_actions = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Disciplinary Actions")
    )
    
    # ====================
    # Extracurricular Activities
    # ====================
    extracurricular_activities = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Extracurricular Activities")
    )
    
    talents = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Talents/Skills")
    )
    
    club_memberships = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Club Memberships")
    )
    
    # ====================
    # Health Information
    # ====================
    health_conditions = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Health Conditions")
    )
    
    allergies = models.TextField(
        blank=True,
        verbose_name=_("Allergies")
    )
    
    dietary_restrictions = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Dietary Restrictions")
    )
    
    medication_schedule = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Medication Schedule")
    )
    
    # ====================
    # Transport Information
    # ====================
    transport_mode = models.CharField(
        max_length=20,
        choices=TRANSPORT_CHOICES,
        default='parent_drop',
        verbose_name=_("Transportation Mode")
    )
    
    bus_route = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Bus Route")
    )
    
    bus_stop = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Bus Stop")
    )
    
    # ====================
    # Financial Information
    # ====================
    fee_status = models.CharField(
        max_length=20,
        choices=[
            ('paid', 'Fully Paid'),
            ('partial', 'Partially Paid'),
            ('unpaid', 'Unpaid'),
            ('scholarship', 'Scholarship'),
            ('bursary', 'Bursary'),
        ],
        default='unpaid',
        verbose_name=_("Fee Status")
    )
    
    fee_arrears = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Fee Arrears")
    )
    
    scholarship_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Scholarship Details")
    )
    
    # ====================
    # Career Information
    # ====================
    career_interests = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Career Interests")
    )
    
    future_plans = models.TextField(
        blank=True,
        verbose_name=_("Future Plans")
    )
    
    # ====================
    # Social Information
    # ====================
    friends = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        verbose_name=_("Friends")
    )
    
    # ====================
    # Previous Education
    # ====================
    previous_school = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Previous School")
    )
    
    previous_class = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Previous Class")
    )
    
    transfer_certificate = models.FileField(
        upload_to='transfer_certificates/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_("Transfer Certificate")
    )
    
    birth_certificate = models.FileField(
        upload_to='birth_certificates/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_("Birth Certificate")
    )
    
    recommendation_letter = models.FileField(
        upload_to='recommendation_letters/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_("Recommendation Letter")
    )
    
    # ====================
    # Status and Metadata
    # ====================
    student_status = models.CharField(
        max_length=20,
        choices=STUDENT_STATUS,
        default='active',
        verbose_name=_("Student Status")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active")
    )
    
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Remarks")
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Metadata")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Student Profile")
        verbose_name_plural = _("Student Profiles")
        ordering = ['admission_number']
        indexes = [
            models.Index(fields=['admission_number']),
            models.Index(fields=['upi_number']),
            models.Index(fields=['nemis_number']),
            models.Index(fields=['student_status']),
            models.Index(fields=['cbc_pathway']),
            models.Index(fields=['current_class']),
            models.Index(fields=['current_academic_year']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.admission_number} - {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        """Generate admission number if not provided and update user role."""
        is_new = self._state.adding
        
        if not self.admission_number:
            self.admission_number = self._generate_admission_number()
        
        # Ensure user has student role
        if self.user.role != User.Role.STUDENT:
            self.user.role = User.Role.STUDENT
            self.user.save(update_fields=['role'])
        
        # Update admission number in User model
        if self.user.admission_number != self.admission_number:
            self.user.admission_number = self.admission_number
            self.user.save(update_fields=['admission_number'])
        
        super().save(*args, **kwargs)

    def _generate_admission_number(self):
        """Generate unique admission number."""
        current_year = timezone.now().year
        last_student = StudentProfile.objects.filter(
            admission_number__startswith=f'DEL-STU-{current_year}-'
        ).order_by('-admission_number').first()
        
        if last_student:
            try:
                last_seq = int(last_student.admission_number.split('-')[-1])
                new_seq = last_seq + 1
            except (ValueError, IndexError):
                new_seq = 1
        else:
            new_seq = 1
        
        return f"DEL-STU-{current_year}-{new_seq:04d}"

    def clean(self):
        """Validate student data."""
        errors = {}
        
        # Validate admission number format
        if self.admission_number and not self.admission_number.startswith('DEL-STU-'):
            errors['admission_number'] = _("Admission number must start with 'DEL-STU-'")
        
        # Validate age through user's date_of_birth
        if self.user.date_of_birth:
            age = self.user.age
            if age and age < 3:
                errors['user'] = _("Student must be at least 3 years old")
            if age and age > 25:
                errors['user'] = _("Student age seems unrealistic for school")
        
        # Validate CBC pathway for senior students
        if self.current_class and self.cbc_pathway:
            # Use apps.get_model to avoid import
            try:
                Class = apps.get_model('academics', 'Class')
                student_class = Class.objects.get(id=self.current_class.id)
                if hasattr(student_class, 'education_level'):
                    if student_class.education_level == 'senior_school' and not self.cbc_pathway:
                        errors['cbc_pathway'] = _("CBC pathway is required for Senior School students")
            except Exception:
                pass
        
        if errors:
            raise ValidationError(errors)

    # ====================
    # Properties
    # ====================

    @property
    def full_name(self):
        """Get student's full name from User model."""
        return self.user.get_full_name()

    @property
    def age(self):
        """Get student's age from User model."""
        return self.user.age

    @property
    def is_cbc_student(self):
        """Check if student is in CBC system."""
        return bool(self.cbc_pathway)

    @property
    def academic_info(self):
        """Get academic information."""
        info = {
            'admission_number': self.admission_number,
            'current_class': str(self.current_class) if self.current_class else 'Not Assigned',
            'academic_year': str(self.current_academic_year) if self.current_academic_year else 'Not Assigned',
            'overall_grade': self.overall_grade,
            'gpa': float(self.gpa),
            'attendance_percentage': float(self.attendance_percentage),
            'rank_in_class': self.rank_in_class,
        }
        
        if self.is_cbc_student:
            info['cbc_pathway'] = self.get_cbc_pathway_display()
            info['portfolio_status'] = self.get_portfolio_status_display()
            info['community_service_hours'] = self.community_service_hours_completed
        
        return info

    @property
    def contact_info(self):
        """Get contact information from User model."""
        return {
            'phone': self.user.phone_number,
            'email': self.user.email,
            'address': self.user.address,
            'emergency_contact': {
                'name': self.user.emergency_contact_name,
                'phone': self.user.emergency_contact_phone,
                'relationship': self.user.emergency_contact_relationship,
            }
        }

    @property
    def parent_info(self):
        """Get parent information from User model."""
        return {
            'parent_name': self.user.parent_name,
            'parent_email': self.user.parent_email,
            'parent_phone': self.user.parent_phone,
            'parent_occupation': self.user.parent_occupation,
        }

    @property
    def medical_info(self):
        """Get medical information."""
        return {
            'blood_group': self.user.get_blood_group_display() if self.user.blood_group else 'Not Specified',
            'medical_info': self.user.medical_info,
            'allergies': self.allergies,
            'dietary_restrictions': self.dietary_restrictions,
            'current_medications': self.user.current_medications,
            'doctor_name': self.user.doctor_name,
            'doctor_phone': self.user.doctor_phone,
        }

    # ====================
    # Methods
    # ====================

    def get_enrollment_history(self):
        """Get enrollment history for this student."""
        return self.enrollments.all().order_by('-academic_year__start_date')

    def get_current_enrollment(self):
        """Get current active enrollment."""
        return self.enrollments.filter(status='active').first()

    def update_academic_performance(self):
        """Update academic performance metrics."""
        try:
            # Use string reference to avoid import
            Grade = apps.get_model('grading', 'Grade')
            grades = Grade.objects.filter(
                student=self.user,
                is_active=True
            )
            
            if grades.exists():
                total_points = sum(grade.grade_points for grade in grades)
                self.gpa = total_points / grades.count()
                self.save()
                return True
        except Exception as e:
            logger.error(f"Error updating academic performance: {e}")
        
        return False

    def add_community_service_hours(self, hours, activity_description=None, verified_by=None):
        """Add community service hours."""
        if hours > 0:
            self.community_service_hours_completed += hours
            
            # Add to extracurricular activities
            if not self.extracurricular_activities:
                self.extracurricular_activities = []
            
            service_record = {
                'id': str(uuid.uuid4()),
                'date': timezone.now().date().isoformat(),
                'hours': hours,
                'activity': activity_description or 'Community Service',
                'verified_by': str(verified_by) if verified_by else None,
                'type': 'community_service',
            }
            
            self.extracurricular_activities.append(service_record)
            self.save()
            return True
        return False

    def update_portfolio_status(self, new_status, notes=None):
        """Update portfolio status."""
        valid_statuses = [choice[0] for choice in self._meta.get_field('portfolio_status').choices]
        
        if new_status in valid_statuses:
            self.portfolio_status = new_status
            if notes:
                self.remarks = f"{self.remarks or ''}\nPortfolio Update: {notes}"
            self.save()
            return True
        return False

    def add_test_score(self, test_name, subject, score, max_score, date_taken):
        """Add a test score."""
        test_score = {
            'id': str(uuid.uuid4()),
            'test_name': test_name,
            'subject': subject,
            'score': score,
            'max_score': max_score,
            'percentage': (score / max_score) * 100,
            'date_taken': date_taken.isoformat() if hasattr(date_taken, 'isoformat') else date_taken,
            'added_at': timezone.now().isoformat()
        }
        
        if not self.test_scores:
            self.test_scores = []
        
        self.test_scores.append(test_score)
        self.save()
        return True

    def add_extracurricular(self, activity, position, duration, achievements=None):
        """Add extracurricular activity."""
        extracurricular = {
            'id': str(uuid.uuid4()),
            'activity': activity,
            'position': position,
            'duration': duration,
            'achievements': achievements or [],
            'added_at': timezone.now().isoformat()
        }
        
        if not self.extracurricular_activities:
            self.extracurricular_activities = []
        
        self.extracurricular_activities.append(extracurricular)
        self.save()
        return True

    def generate_student_report(self):
        """Generate comprehensive student report."""
        report = {
            'personal_info': {
                'name': self.full_name,
                'admission_number': self.admission_number,
                'upi_number': self.upi_number,
                'nemis_number': self.nemis_number,
                'date_of_birth': self.user.date_of_birth,
                'age': self.age,
                'gender': self.user.get_gender_display(),
            },
            'academic_info': self.academic_info,
            'contact_info': self.contact_info,
            'parent_info': self.parent_info,
            'medical_info': self.medical_info,
            'extracurricular': {
                'activities': self.extracurricular_activities,
                'talents': self.talents,
                'club_memberships': self.club_memberships,
            },
            'behavioral': {
                'conduct_rating': self.get_conduct_rating_display(),
                'disciplinary_actions': self.disciplinary_actions,
            },
            'status': {
                'student_status': self.get_student_status_display(),
                'fee_status': self.get_fee_status_display(),
                'fee_arrears': float(self.fee_arrears),
            },
        }
        
        if self.is_cbc_student:
            report['cbc_info'] = {
                'pathway': self.get_cbc_pathway_display(),
                'portfolio_status': self.get_portfolio_status_display(),
                'community_service_hours': self.community_service_hours_completed,
            }
        
        return report

    def promote_to_next_class(self, next_academic_year):
        """Promote student to next class."""
        try:
            # Find next class based on current class
            next_grade = self._get_next_grade_level()
            next_class = apps.get_model('academics', 'Class').objects.filter(
                academic_year=next_academic_year,
                grade_level=next_grade,
                is_active=True
            ).first()
            
            if next_class:
                # Create new enrollment for next year
                new_enrollment = StudentEnrollment.objects.create(
                    student_profile=self,
                    class_enrolled=next_class,
                    academic_year=next_academic_year,
                    remarks=f"Promoted from {self.current_class.display_name}",
                    created_by=self.user,
                )
                
                # Update current profile
                self.current_class = next_class
                self.current_academic_year = next_academic_year
                self.save()
                
                return new_enrollment
        except Exception as e:
            logger.error(f"Error promoting student: {e}")
        
        return None

    def _get_next_grade_level(self):
        """Get next grade level."""
        if not self.current_class:
            return None
        
        grade_order = [choice[0] for choice in GRADE_LEVEL_CHOICES]
        try:
            current_index = grade_order.index(self.current_class.grade_level)
            if current_index < len(grade_order) - 1:
                return grade_order[current_index + 1]
        except (ValueError, IndexError):
            pass
        
        return self.current_class.grade_level


class StudentEnrollment(models.Model):

    SENIOR_SCHOOL_TRACKS = (
    ('stem_science', 'STEM - Pure Sciences'),
    ('stem_technical', 'STEM - Technical & Engineering'),
    ('stem_applied', 'STEM - Applied Sciences'),
    ('social_sciences_general', 'Social Sciences - General'),
    ('social_sciences_business', 'Social Sciences - Business'),
    ('social_sciences_humanities', 'Social Sciences - Humanities'),
    ('arts_performing', 'Arts - Performing Arts'),
    ('arts_visual', 'Arts - Visual & Creative Arts'),
    ('sports_performance', 'Sports - Performance'),
    ('sports_management', 'Sports - Management'),
)
    """
    Student enrollment management.
    Links students to classes and academic years.
    """
    
    # Core Relationships
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_("Student Profile")
    )
    
    class_enrolled = models.ForeignKey(
        'academics.Class',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_("Class")
    )
    
    academic_year = models.ForeignKey(
        'academics.AcademicYear',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_("Academic Year")
    )
    
    # Enrollment Information
    enrollment_date = models.DateField(
        default=timezone.now,
        verbose_name=_("Enrollment Date")
    )
    
    enrollment_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Enrollment Number")
    )
    
    # Status Information
    status = models.CharField(
        max_length=20,
        choices=ENROLLMENT_STATUS,
        default='active',
        verbose_name=_("Status")
    )
    
    status_changed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Status Changed Date")
    )
    
    status_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Status Reason")
    )
    
    # Academic Information
    roll_number = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name=_("Roll Number")
    )
    
    # CBC-Specific Information
    cbc_pathway_selection = models.CharField(
        max_length=20,
        choices=[
            ('stem', 'STEM Pathway'),
            ('social_sciences', 'Social Sciences Pathway'),
            ('arts_sports', 'Arts & Sports Pathway'),
        ],
        blank=True,
        null=True,
        verbose_name=_("CBC Pathway Selection")
    )
    
    senior_track_selection = models.CharField(
        max_length=30,
        choices=SENIOR_SCHOOL_TRACKS,
        blank=True,
        null=True,
        verbose_name=_("Senior Track Selection")
    )
    
    # House and Extracurricular
    house = models.CharField(
        max_length=20,
        choices=HOUSE_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("House")
    )
    
    # Financial Information
    fee_status = models.CharField(
        max_length=20,
        choices=[
            ('paid', 'Fully Paid'),
            ('partial', 'Partially Paid'),
            ('unpaid', 'Unpaid'),
            ('scholarship', 'Scholarship'),
            ('bursary', 'Bursary'),
        ],
        default='unpaid',
        verbose_name=_("Fee Status")
    )
    
    fee_arrears = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Fee Arrears")
    )
    
    # Metadata
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Remarks")
    )
    
    enrollment_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Enrollment Metadata")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Student Enrollment")
        verbose_name_plural = _("Student Enrollments")
        unique_together = ['student_profile', 'academic_year']
        ordering = ['class_enrolled', 'roll_number']
        indexes = [
            models.Index(fields=['student_profile', 'academic_year']),
            models.Index(fields=['enrollment_number']),
            models.Index(fields=['status']),
            models.Index(fields=['house']),
            models.Index(fields=['class_enrolled']),
            models.Index(fields=['cbc_pathway_selection']),
            models.Index(fields=['senior_track_selection']),
            models.Index(fields=['fee_status']),
        ]

    def __str__(self):
        return f"{self.student_profile.full_name} - {self.class_enrolled} - {self.academic_year}"

    def save(self, *args, **kwargs):
        """Generate enrollment number and update status dates."""
        is_new = self._state.adding
        
        if not self.enrollment_number:
            self.enrollment_number = self._generate_enrollment_number()
        
        if self.pk:
            original = StudentEnrollment.objects.get(pk=self.pk)
            if original.status != self.status:
                self.status_changed_date = timezone.now().date()
        else:
            self.status_changed_date = timezone.now().date()
        
        # Auto-set roll number if not provided
        if not self.roll_number:
            self.roll_number = self._get_next_roll_number()
        
        super().save(*args, **kwargs)

    def _generate_enrollment_number(self):
        """Generate unique enrollment number."""
        year = self.enrollment_date.year
        student_initials = self.student_profile.admission_number[-4:] if self.student_profile.admission_number else 'ST'
        
        # Find last enrollment for this year
        last_enrollment = StudentEnrollment.objects.filter(
            enrollment_date__year=year
        ).order_by('-enrollment_number').first()
        
        if last_enrollment and last_enrollment.enrollment_number:
            try:
                last_num = int(last_enrollment.enrollment_number.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
        
        return f"ENR-{year}-{student_initials}-{new_num:04d}"

    def _get_next_roll_number(self):
        """Get next available roll number for the class."""
        enrollments = StudentEnrollment.objects.filter(
            class_enrolled=self.class_enrolled,
            academic_year=self.academic_year
        ).exclude(roll_number=None).order_by('-roll_number')
        
        if enrollments.exists():
            return enrollments.first().roll_number + 1
        return 1

    def clean(self):
        """Validate enrollment data."""
        errors = {}
        
        # Check for duplicate enrollment in same academic year
        duplicate_enrollment = StudentEnrollment.objects.filter(
            student_profile=self.student_profile,
            academic_year=self.academic_year
        ).exclude(pk=self.pk).exists()
        
        if duplicate_enrollment:
            errors['academic_year'] = _('Student is already enrolled for this academic year.')
        
        # Check for duplicate roll number in same class
        if self.roll_number:
            duplicate_roll = StudentEnrollment.objects.filter(
                academic_year=self.academic_year,
                class_enrolled=self.class_enrolled,
                roll_number=self.roll_number
            ).exclude(pk=self.pk).exists()
            
            if duplicate_roll:
                errors['roll_number'] = _('Roll number must be unique within the class for this academic year.')
        
        if errors:
            raise ValidationError(errors)

    @property
    def is_current(self):
        """Check if this is the current enrollment."""
        if not self.academic_year:
            return False
        
        # Use apps.get_model to avoid import
        AcademicYear = apps.get_model('academics', 'AcademicYear')
        try:
            return self.status == 'active' and self.academic_year.is_current
        except AttributeError:
            return False

    @property
    def enrollment_summary(self):
        """Get enrollment summary."""
        return {
            'student': self.student_profile.full_name,
            'class': str(self.class_enrolled),
            'academic_year': str(self.academic_year),
            'enrollment_date': self.enrollment_date,
            'enrollment_number': self.enrollment_number,
            'status': self.get_status_display(),
            'roll_number': self.roll_number,
            'is_current': self.is_current,
        }


# ============================================================================
# SIGNAL HANDLERS
# ============================================================================

@receiver(post_save, sender=StudentEnrollment)
def update_student_current_class(sender, instance, created, **kwargs):
    """
    Update student's current class when enrollment is created or updated.
    """
    if instance.status == 'active':
        instance.student_profile.current_class = instance.class_enrolled
        instance.student_profile.current_academic_year = instance.academic_year
        instance.student_profile.save()


@receiver(post_save, sender=StudentProfile)
def create_user_student_profile(sender, instance, created, **kwargs):
    """
    Ensure user has student profile in accounts if needed.
    """
    try:
        # Try to get or create the accounts StudentProfile
        accounts_student_profile, created_accounts = apps.get_model('accounts', 'StudentProfile').objects.get_or_create(
            user=instance.user,
            defaults={
                'admission_number': instance.admission_number,
                'current_class': instance.current_class,
                'roll_number': instance.roll_number if hasattr(instance, 'roll_number') else None,
                'house': instance.house if hasattr(instance, 'house') else None,
                'conduct_rating': instance.conduct_rating,
            }
        )
        
        # Update if exists
        if not created_accounts:
            accounts_student_profile.admission_number = instance.admission_number
            accounts_student_profile.current_class = instance.current_class
            accounts_student_profile.save()
            
    except Exception as e:
        logger.error(f"Error syncing student profile with accounts: {e}")


@receiver(post_save, sender=User)
def create_student_profile_for_user(sender, instance, created, **kwargs):
    """
    Create student profile when a student user is created.
    """
    if created and instance.role == User.Role.STUDENT:
        try:
            # Generate admission number if not provided
            admission_number = instance.admission_number or StudentProfile._generate_admission_number(instance)
            
            StudentProfile.objects.create(
                user=instance,
                admission_number=admission_number
            )
        except Exception as e:
            logger.error(f"Error creating student profile for user {instance.email}: {e}")