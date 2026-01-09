# teachers/filters.py - FIXED VERSION
import django_filters
from django_filters import rest_framework as filters
from django_filters.filters import BaseInFilter
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    Department, TeacherProfile, TeacherDocument, TeacherQualification,
    TeacherTraining, TeacherAssignment, TeacherAttendance, TeacherLeave,
    ProfessionalStanding, PerformanceIndicator, TeacherTransfer
)


# ============================================================================
# COMMON CHOICES DEFINITIONS (Define locally to avoid model attribute errors)
# ============================================================================

# Department choices
TSC_CATEGORY_CHOICES = [
    ('primary', 'Primary School'),
    ('junior_secondary', 'Junior Secondary School'),
    ('senior_secondary', 'Senior Secondary School'),
    ('special_needs', 'Special Needs Education'),
    ('technical', 'Technical/Vocational'),
    ('ecde', 'Early Childhood Development Education'),
]

CBC_PATHWAY_CHOICES = [
    ('stem', 'STEM Pathway'),
    ('social_sciences', 'Social Sciences Pathway'),
    ('arts_sports', 'Arts & Sports Pathway'),
    ('general', 'General Pathway'),
    ('applied', 'Applied Pathway'),
    ('technical', 'Technical Pathway'),
]

# TeacherProfile choices
EMPLOYMENT_STATUS_CHOICES = [
    ('active', 'Active'),
    ('on_leave', 'On Leave'),
    ('study_leave', 'On Study Leave'),
    ('maternity_leave', 'On Maternity Leave'),
    ('paternity_leave', 'On Paternity Leave'),
    ('sick_leave', 'On Sick Leave'),
    ('suspended', 'Suspended'),
    ('terminated', 'Terminated'),
    ('retired', 'Retired'),
    ('resigned', 'Resigned'),
    ('transferred', 'Transferred'),
    ('deceased', 'Deceased'),
]

EMPLOYMENT_TYPE_CHOICES = [
    ('permanent_tsc', 'Permanent Teacher (TSC)'),
    ('contract_tsc', 'Contract Teacher (TSC)'),
    ('bom', 'BOM Teacher'),
    ('pta', 'PTA Teacher'),
    ('intern', 'TSC Intern'),
    ('volunteer', 'Volunteer Teacher'),
    ('part_time', 'Part-time Teacher'),
    ('substitute', 'Substitute Teacher'),
]

TEACHING_LEVEL_CHOICES = [
    ('primary', 'Primary School (Grade 1-6)'),
    ('junior_secondary', 'Junior Secondary (Grade 7-9)'),
    ('senior_secondary', 'Senior Secondary (Grade 10-12)'),
    ('ecde', 'Early Childhood Development Education'),
    ('special_needs', 'Special Needs Education'),
    ('technical', 'Technical/Vocational'),
    ('tvet', 'TVET Institution'),
    ('university', 'University'),
]

TSC_STATUS_CHOICES = [
    ('registered', 'TSC Registered'),
    ('provisional', 'Provisional Registration'),
    ('pending', 'Registration Pending'),
    ('intern', 'TSC Intern'),
    ('not_registered', 'Not Registered'),
    ('expired', 'Registration Expired'),
    ('suspended', 'Registration Suspended'),
    ('revoked', 'Registration Revoked'),
]

DESIGNATION_CHOICES = [
    ('classroom_teacher', 'Classroom Teacher'),
    ('senior_teacher', 'Senior Teacher'),
    ('head_of_department', 'Head of Department'),
    ('deputy_head_teacher', 'Deputy Head Teacher'),
    ('head_teacher', 'Head Teacher'),
    ('deputy_principal', 'Deputy Principal'),
    ('principal', 'Principal'),
    ('director_studies', 'Director of Studies'),
    ('curriculum_coordinator', 'Curriculum Coordinator'),
    ('guidance_counselor', 'Guidance and Counseling Teacher'),
    ('games_master', 'Games Master/Mistress'),
    ('lab_technician', 'Laboratory Technician'),
    ('librarian', 'Librarian'),
]

# TeacherDocument choices
DOCUMENT_TYPE_CHOICES = [
    ('tsc_certificate', 'TSC Certificate'),
    ('good_conduct', 'Certificate of Good Conduct'),
    ('academic_certificate', 'Academic Certificate'),
    ('transcript', 'Academic Transcript'),
    ('cbc_certificate', 'CBC Training Certificate'),
    ('tpd_certificate', 'TPD Certificate'),
    ('id_copy', 'National ID/Passport Copy'),
    ('kra_pin', 'KRA PIN Certificate'),
    ('nssf_card', 'NSSF Card'),
    ('nhif_card', 'NHIF Card'),
    ('appointment_letter', 'Appointment Letter'),
    ('confirmation_letter', 'Confirmation Letter'),
    ('promotion_letter', 'Promotion Letter'),
    ('transfer_letter', 'Transfer Letter'),
    ('medical_report', 'Medical Report'),
    ('birth_certificate', 'Birth Certificate'),
    ('marriage_certificate', 'Marriage Certificate'),
    ('police_clearance', 'Police Clearance Certificate'),
    ('cv_resume', 'CV/Resume'),
    ('reference_letter', 'Reference Letter'),
    ('performance_appraisal', 'Performance Appraisal Form'),
    ('leave_document', 'Leave Application/Approval'),
    ('disciplinary', 'Disciplinary Document'),
    ('other', 'Other Document'),
]

DOCUMENT_STATUS_CHOICES = [
    ('pending', 'Pending Review'),
    ('verified', 'Verified'),
    ('rejected', 'Rejected'),
    ('expired', 'Expired'),
    ('missing', 'Missing'),
    ('under_review', 'Under Review'),
]

# TeacherQualification choices
QUALIFICATION_TYPE_CHOICES = [
    ('primary', 'Primary Education Certificate'),
    ('secondary', 'Secondary Education Certificate'),
    ('certificate', 'Certificate'),
    ('diploma', 'Diploma'),
    ('bachelor', "Bachelor's Degree"),
    ('postgraduate_diploma', 'Postgraduate Diploma'),
    ('masters', "Master's Degree"),
    ('phd', 'Doctorate (PhD)'),
    ('professional', 'Professional Certification'),
    ('training', 'Training Certificate'),
]

QUALIFICATION_LEVEL_CHOICES = [
    ('certificate', 'Certificate'),
    ('diploma', 'Diploma'),
    ('bachelor', "Bachelor's Degree"),
    ('postgraduate', 'Postgraduate'),
    ('masters', "Master's Degree"),
    ('phd', 'PhD'),
]

QUALIFICATION_STATUS_CHOICES = [
    ('not_verified', 'Not Verified'),
    ('pending', 'Verification Pending'),
    ('verified', 'Verified'),
    ('rejected', 'Verification Rejected'),
]

# TeacherTraining choices
TRAINING_TYPE_CHOICES = [
    ('cbc', 'CBC Training'),
    ('tpd', 'Teacher Professional Development'),
    ('subject_specific', 'Subject-Specific Training'),
    ('pedagogy', 'Pedagogical Training'),
    ('technology', 'Technology Integration'),
    ('leadership', 'Leadership Training'),
    ('special_needs', 'Special Needs Education'),
    ('assessment', 'Assessment & Evaluation'),
    ('classroom_management', 'Classroom Management'),
    ('guidance_counseling', 'Guidance & Counseling'),
    ('health_safety', 'Health & Safety'),
    ('other', 'Other Training'),
]

TRAINING_CATEGORY_CHOICES = [
    ('mandatory', 'Mandatory'),
    ('optional', 'Optional'),
    ('certification', 'Certification'),
    ('workshop', 'Workshop'),
    ('seminar', 'Seminar'),
]

TRAINING_STATUS_CHOICES = [
    ('registered', 'Registered'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('failed', 'Failed'),
]

# TeacherAssignment choices
TERM_CHOICES = [
    ('term1', 'Term 1'),
    ('term2', 'Term 2'),
    ('term3', 'Term 3'),
]

ASSIGNMENT_TYPE_CHOICES = [
    ('teaching', 'Teaching Assignment'),
    ('administrative', 'Administrative Duty'),
    ('committee', 'Committee Membership'),
    ('co_curricular', 'Co-curricular Activity'),
    ('pastoral', 'Pastoral Duty'),
    ('supervisory', 'Supervisory Duty'),
    ('other', 'Other Assignment'),
]

ASSIGNMENT_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('active', 'Active'),
    ('completed', 'Completed'),
]

# TeacherAttendance choices
ATTENDANCE_STATUS_CHOICES = [
    ('present', 'Present'),
    ('absent', 'Absent'),
    ('late', 'Late'),
    ('half_day', 'Half Day'),
    ('leave', 'On Leave'),
    ('off_duty', 'Off Duty'),
    ('training', 'On Training'),
    ('sick', 'Sick'),
    ('emergency', 'Emergency Leave'),
    ('other', 'Other'),
]

# TeacherLeave choices
LEAVE_TYPE_CHOICES = [
    ('annual', 'Annual Leave'),
    ('sick', 'Sick Leave'),
    ('maternity', 'Maternity Leave'),
    ('paternity', 'Paternity Leave'),
    ('study', 'Study Leave'),
    ('compassionate', 'Compassionate Leave'),
    ('emergency', 'Emergency Leave'),
    ('unpaid', 'Unpaid Leave'),
    ('other', 'Other Leave'),
]

LEAVE_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
    ('in_progress', 'Leave in Progress'),
    ('completed', 'Completed'),
]

# ProfessionalStanding choices
STANDING_TYPE_CHOICES = [
    ('disciplinary', 'Disciplinary Action'),
    ('warning', 'Warning Letter'),
    ('commendation', 'Commendation'),
    ('promotion', 'Promotion Recommendation'),
    ('transfer', 'Transfer Recommendation'),
    ('other', 'Other Record'),
]

# PerformanceIndicator choices
PERFORMANCE_TERM_CHOICES = [
    ('term1', 'Term 1'),
    ('term2', 'Term 2'),
    ('term3', 'Term 3'),
    ('annual', 'Annual'),
]

RATING_CHOICES = [
    ('excellent', 'Excellent'),
    ('good', 'Good'),
    ('satisfactory', 'Satisfactory'),
    ('needs_improvement', 'Needs Improvement'),
    ('poor', 'Poor'),
]

# TeacherTransfer choices
TRANSFER_TYPE_CHOICES = [
    ('inter_school', 'Inter-School Transfer'),
    ('intra_school', 'Intra-School Transfer'),
    ('promotional', 'Promotional Transfer'),
    ('requested', 'Requested Transfer'),
    ('disciplinary', 'Disciplinary Transfer'),
]

TRANSFER_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('completed', 'Completed'),
]

# ============================================================================
# DEPARTMENT FILTERS - FIXED
# ============================================================================

class DepartmentFilter(filters.FilterSet):
    """Filter for Department model"""
    
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    hod = django_filters.NumberFilter(field_name='hod__id')
    hod_is_null = django_filters.BooleanFilter(field_name='hod', lookup_expr='isnull')
    
    # Boolean filters
    is_active = django_filters.BooleanFilter()
    has_hod = django_filters.BooleanFilter(field_name='hod', lookup_expr='isnull', exclude=True)
    
    # TSC category filter - FIXED: Use local choices
    tsc_category = django_filters.ChoiceFilter(
        choices=TSC_CATEGORY_CHOICES
    )
    
    # CBC pathway filter - FIXED: Use local choices
    cbc_pathway = django_filters.ChoiceFilter(
        choices=CBC_PATHWAY_CHOICES
    )
    
    # Date range filters
    created_at = django_filters.DateFromToRangeFilter()
    updated_at = django_filters.DateFromToRangeFilter()
    
    # Search filter (combines multiple fields)
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Department
        fields = [
            'name', 'code', 'hod', 'is_active', 'tsc_category',
            'cbc_pathway', 'created_at', 'updated_at'
        ]
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value)
        )
    
    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('code', 'code'),
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
        )
    )


# ============================================================================
# TEACHER PROFILE FILTERS - FIXED
# ============================================================================

class TeacherProfileFilter(filters.FilterSet):
    """Filter for TeacherProfile model"""
    
    # Basic filters
    first_name = django_filters.CharFilter(field_name='teacher__first_name', lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='teacher__last_name', lookup_expr='icontains')
    full_name = django_filters.CharFilter(method='filter_full_name')
    email = django_filters.CharFilter(field_name='teacher__email', lookup_expr='icontains')
    phone_number = django_filters.CharFilter(field_name='teacher__phone_number', lookup_expr='icontains')
    id_number = django_filters.CharFilter(field_name='teacher__id_number', lookup_expr='exact')
    tsc_number = django_filters.CharFilter(lookup_expr='icontains')
    
    # Department filters
    department = django_filters.NumberFilter(field_name='department__id')
    department_name = django_filters.CharFilter(field_name='department__name', lookup_expr='icontains')
    
    # Status filters - FIXED: Use local choices
    employment_status = django_filters.ChoiceFilter(
        choices=EMPLOYMENT_STATUS_CHOICES
    )
    employment_type = django_filters.ChoiceFilter(
        choices=EMPLOYMENT_TYPE_CHOICES
    )
    tsc_status = django_filters.ChoiceFilter(
        choices=TSC_STATUS_CHOICES
    )
    teaching_level = django_filters.ChoiceFilter(
        choices=TEACHING_LEVEL_CHOICES
    )
    designation = django_filters.ChoiceFilter(
        choices=DESIGNATION_CHOICES
    )
    
    # Boolean filters
    is_active = django_filters.BooleanFilter()
    cbc_trained = django_filters.BooleanFilter()
    tsc_compliant = django_filters.BooleanFilter()
    
    # TPD filters
    tpd_current_module = django_filters.NumberFilter()
    tpd_next_renewal_date = django_filters.DateFromToRangeFilter()
    tpd_expiring_soon = django_filters.BooleanFilter(method='filter_tpd_expiring_soon')
    
    # Date range filters
    employment_date = django_filters.DateFromToRangeFilter()
    created_at = django_filters.DateFromToRangeFilter()
    updated_at = django_filters.DateFromToRangeFilter()
    next_appraisal_date = django_filters.DateFromToRangeFilter()
    
    # Workload filters
    weekly_periods = django_filters.RangeFilter()
    teaching_load_hours = django_filters.RangeFilter()
    
    # Performance filters
    performance_rating = django_filters.RangeFilter()
    
    # Gender filter
    gender = django_filters.ChoiceFilter(
        field_name='teacher__gender',
        choices=[
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other')
        ]
    )
    
    # Search filter (combines multiple fields)
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = TeacherProfile
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'id_number',
            'tsc_number', 'department', 'employment_status', 'employment_type',
            'tsc_status', 'teaching_level', 'designation', 'is_active',
            'cbc_trained', 'tsc_compliant', 'tpd_current_module',
            'employment_date', 'created_at', 'weekly_periods',
            'performance_rating', 'gender'
        ]
    
    def filter_full_name(self, queryset, name, value):
        """Filter by full name (first + last)"""
        return queryset.filter(
            Q(teacher__first_name__icontains=value) |
            Q(teacher__last_name__icontains=value)
        )
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(teacher__first_name__icontains=value) |
            Q(teacher__last_name__icontains=value) |
            Q(teacher__email__icontains=value) |
            Q(teacher__id_number__icontains=value) |
            Q(tsc_number__icontains=value) |
            Q(department__name__icontains=value)
        )
    
    def filter_tpd_expiring_soon(self, queryset, name, value):
        """Filter teachers with TPD expiring soon (within 30 days)"""
        if value:
            thirty_days_later = timezone.now().date() + timedelta(days=30)
            return queryset.filter(
                tpd_next_renewal_date__range=[timezone.now().date(), thirty_days_later]
            )
        return queryset
    
    order_by = django_filters.OrderingFilter(
        fields=(
            ('teacher__last_name', 'last_name'),
            ('teacher__first_name', 'first_name'),
            ('tsc_number', 'tsc_number'),
            ('employment_date', 'employment_date'),
            ('created_at', 'created_at'),
            ('weekly_periods', 'weekly_periods'),
            ('performance_rating', 'performance_rating'),
        )
    )


# ============================================================================
# TEACHER DOCUMENT FILTERS - FIXED
# ============================================================================

class TeacherDocumentFilter(filters.FilterSet):
    """Filter for TeacherDocument model"""
    
    # Basic filters
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    
    # Teacher filters
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    teacher_name = django_filters.CharFilter(method='filter_teacher_name')
    tsc_number = django_filters.CharFilter(field_name='teacher__tsc_number', lookup_expr='icontains')
    
    # Type and status filters - FIXED: Use local choices
    document_type = django_filters.ChoiceFilter(
        choices=DOCUMENT_TYPE_CHOICES
    )
    status = django_filters.ChoiceFilter(
        choices=DOCUMENT_STATUS_CHOICES
    )
    
    # Boolean filters
    is_active = django_filters.BooleanFilter()
    is_required = django_filters.BooleanFilter()
    
    # Verification filters
    verified_by = django_filters.NumberFilter(field_name='verified_by__id')
    verification_date = django_filters.DateFromToRangeFilter()
    
    # Date range filters
    upload_date = django_filters.DateFromToRangeFilter()
    expiry_date = django_filters.DateFromToRangeFilter()
    
    # Expiring soon filter
    expiring_soon = django_filters.BooleanFilter(method='filter_expiring_soon')
    
    # Search filter
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = TeacherDocument
        fields = [
            'title', 'teacher', 'document_type', 'status', 'is_active',
            'is_required', 'verified_by', 'upload_date', 'expiry_date',
            'verification_date'
        ]
    
    def filter_teacher_name(self, queryset, name, value):
        """Filter by teacher name"""
        return queryset.filter(
            Q(teacher__teacher__first_name__icontains=value) |
            Q(teacher__teacher__last_name__icontains=value)
        )
    
    def filter_expiring_soon(self, queryset, name, value):
        """Filter documents expiring soon (within 30 days)"""
        if value:
            thirty_days_later = timezone.now().date() + timedelta(days=30)
            return queryset.filter(
                expiry_date__range=[timezone.now().date(), thirty_days_later]
            )
        return queryset
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(teacher__teacher__first_name__icontains=value) |
            Q(teacher__teacher__last_name__icontains=value) |
            Q(teacher__tsc_number__icontains=value)
        )
    
    order_by = django_filters.OrderingFilter(
        fields=(
            ('upload_date', 'upload_date'),
            ('expiry_date', 'expiry_date'),
            ('title', 'title'),
            ('status', 'status'),
        )
    )


# ============================================================================
# TEACHER QUALIFICATION FILTERS - FIXED
# ============================================================================

class TeacherQualificationFilter(filters.FilterSet):
    """Filter for TeacherQualification model"""
    
    # Basic filters
    title = django_filters.CharFilter(lookup_expr='icontains')
    institution = django_filters.CharFilter(lookup_expr='icontains')
    field_of_study = django_filters.CharFilter(lookup_expr='icontains')
    certificate_number = django_filters.CharFilter(lookup_expr='icontains')
    
    # Teacher filters
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    teacher_name = django_filters.CharFilter(method='filter_teacher_name')
    
    # Type and level filters - FIXED: Use local choices
    qualification_type = django_filters.ChoiceFilter(
        choices=QUALIFICATION_TYPE_CHOICES
    )
    qualification_level = django_filters.ChoiceFilter(
        choices=QUALIFICATION_LEVEL_CHOICES
    )
    
    # Status filters - FIXED: Use local choices
    verification_status = django_filters.ChoiceFilter(
        choices=QUALIFICATION_STATUS_CHOICES
    )
    
    # Boolean filters
    is_active = django_filters.BooleanFilter()
    
    # Verification filters
    verified_by = django_filters.NumberFilter(field_name='verified_by__id')
    verification_date = django_filters.DateFromToRangeFilter()
    
    # Date range filters
    start_date = django_filters.DateFromToRangeFilter()
    end_date = django_filters.DateFromToRangeFilter()
    created_at = django_filters.DateFromToRangeFilter()
    
    # Search filter
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = TeacherQualification
        fields = [
            'title', 'institution', 'field_of_study', 'certificate_number',
            'teacher', 'qualification_type', 'qualification_level',
            'verification_status', 'is_active', 'verified_by',
            'start_date', 'end_date', 'verification_date'
        ]
    
    def filter_teacher_name(self, queryset, name, value):
        """Filter by teacher name"""
        return queryset.filter(
            Q(teacher__teacher__first_name__icontains=value) |
            Q(teacher__teacher__last_name__icontains=value)
        )
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(institution__icontains=value) |
            Q(field_of_study__icontains=value) |
            Q(certificate_number__icontains=value) |
            Q(teacher__teacher__first_name__icontains=value) |
            Q(teacher__teacher__last_name__icontains=value)
        )
    
    order_by = django_filters.OrderingFilter(
        fields=(
            ('end_date', 'end_date'),
            ('start_date', 'start_date'),
            ('title', 'title'),
            ('verification_status', 'verification_status'),
        )
    )


# ============================================================================
# SIMPLIFIED FILTERS FOR OTHER MODELS (to avoid errors)
# ============================================================================

class TeacherTrainingFilter(filters.FilterSet):
    """Simple filter for TeacherTraining"""
    
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    title = django_filters.CharFilter(lookup_expr='icontains')
    organizer = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=TRAINING_STATUS_CHOICES)
    
    class Meta:
        model = TeacherTraining
        fields = ['teacher', 'title', 'organizer', 'status', 'is_active']


class TeacherAssignmentFilter(filters.FilterSet):
    """Simple filter for TeacherAssignment"""
    
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    title = django_filters.CharFilter(lookup_expr='icontains')
    assignment_type = django_filters.ChoiceFilter(choices=ASSIGNMENT_TYPE_CHOICES)
    is_active = django_filters.BooleanFilter()
    
    class Meta:
        model = TeacherAssignment
        fields = ['teacher', 'title', 'assignment_type', 'is_active']


class TeacherAttendanceFilter(filters.FilterSet):
    """Simple filter for TeacherAttendance"""
    
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    date = django_filters.DateFromToRangeFilter()
    status = django_filters.ChoiceFilter(choices=ATTENDANCE_STATUS_CHOICES)
    
    class Meta:
        model = TeacherAttendance
        fields = ['teacher', 'date', 'status']


class TeacherLeaveFilter(filters.FilterSet):
    """Simple filter for TeacherLeave"""
    
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    leave_type = django_filters.ChoiceFilter(choices=LEAVE_TYPE_CHOICES)
    status = django_filters.ChoiceFilter(choices=LEAVE_STATUS_CHOICES)
    start_date = django_filters.DateFromToRangeFilter()
    end_date = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = TeacherLeave
        fields = ['teacher', 'leave_type', 'status', 'start_date', 'end_date', 'is_active']

class ProfessionalStandingFilter(filters.FilterSet):
    """Simple filter for ProfessionalStanding"""
    
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    record_type = django_filters.ChoiceFilter(choices=STANDING_TYPE_CHOICES)
    
    class Meta:
        model = ProfessionalStanding
        fields = ['teacher', 'record_type', 'is_active']

class ProfessionalStandingFilter(filters.FilterSet):
    """Simple filter for ProfessionalStanding"""
    
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    record_type = django_filters.ChoiceFilter(choices=STANDING_TYPE_CHOICES)
    
    class Meta:
        model = ProfessionalStanding
        fields = ['teacher', 'record_type', 'is_active']

class SearchFilter(filters.FilterSet):
    """Simple search filter for TeacherProfile"""
    
    q = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = TeacherProfile
        fields = []
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(teacher__first_name__icontains=value) |
            Q(teacher__last_name__icontains=value) |
            Q(teacher__email__icontains=value) |
            Q(tsc_number__icontains=value) |
            Q(teacher__id_number__icontains=value) |
            Q(department__name__icontains=value)
        )

class PerformanceIndicatorFilter(filters.FilterSet):
    """Simple filter for PerformanceIndicator"""
    
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    academic_year = django_filters.NumberFilter(field_name='academic_year__id')
    overall_score = django_filters.RangeFilter()
    
    class Meta:
        model = PerformanceIndicator
        fields = ['teacher', 'academic_year', 'overall_score', 'is_active']


class TeacherTransferFilter(filters.FilterSet):
    """Simple filter for TeacherTransfer"""
    
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    transfer_type = django_filters.ChoiceFilter(choices=TRANSFER_TYPE_CHOICES)
    status = django_filters.ChoiceFilter(choices=TRANSFER_STATUS_CHOICES)
    
    class Meta:
        model = TeacherTransfer
        fields = ['teacher', 'transfer_type', 'status', 'is_active']


# ============================================================================
# ADVANCED FILTER - FIXED
# ============================================================================

class TeacherAdvancedFilter(filters.FilterSet):
    """Advanced filter combining multiple teacher criteria"""
    
    # Combined search
    q = django_filters.CharFilter(method='filter_combined_search')
    
    # Department filters
    department = django_filters.NumberFilter(field_name='department__id')
    departments = BaseInFilter(field_name='department__id', lookup_expr='in')
    
    # Status combinations
    employment_status_in = BaseInFilter(
        field_name='employment_status', lookup_expr='in'
    )
    tsc_status_in = BaseInFilter(
        field_name='tsc_status', lookup_expr='in'
    )
    
    # Teaching level combinations
    teaching_level_in = BaseInFilter(
        field_name='teaching_level', lookup_expr='in'
    )
    
    # Boolean combinations
    cbc_trained = django_filters.BooleanFilter()
    tsc_compliant = django_filters.BooleanFilter()
    
    # TPD filters
    tpd_module = django_filters.NumberFilter()
    tpd_module_gte = django_filters.NumberFilter(field_name='tpd_current_module', lookup_expr='gte')
    tpd_module_lte = django_filters.NumberFilter(field_name='tpd_current_module', lookup_expr='lte')
    
    # Workload filters
    workload_status = django_filters.ChoiceFilter(
        method='filter_workload_status',
        choices=[
            ('overloaded', 'Overloaded'),
            ('optimal', 'Optimal'),
            ('underutilized', 'Underutilized'),
            ('no_load', 'No Load'),
        ]
    )
    
    # Performance filters
    performance_rating_gte = django_filters.NumberFilter(field_name='performance_rating', lookup_expr='gte')
    performance_rating_lte = django_filters.NumberFilter(field_name='performance_rating', lookup_expr='lte')
    
    # Date ranges
    employment_date_range = django_filters.DateFromToRangeFilter(field_name='employment_date')
    created_at_range = django_filters.DateFromToRangeFilter(field_name='created_at')
    
    # Years of service
    years_of_service_gte = django_filters.NumberFilter(method='filter_years_of_service_gte')
    years_of_service_lte = django_filters.NumberFilter(method='filter_years_of_service_lte')
    
    class Meta:
        model = TeacherProfile
        fields = []
    
    def filter_combined_search(self, queryset, name, value):
        """Combined search across all relevant fields"""
        return queryset.filter(
            Q(teacher__first_name__icontains=value) |
            Q(teacher__last_name__icontains=value) |
            Q(teacher__email__icontains=value) |
            Q(tsc_number__icontains=value) |
            Q(teacher__id_number__icontains=value) |
            Q(department__name__icontains=value)
        )
    
    def filter_workload_status(self, queryset, name, value):
        """Filter by workload status"""
        if value == 'overloaded':
            return queryset.filter(weekly_periods__gt=36)
        elif value == 'optimal':
            return queryset.filter(weekly_periods__range=[23, 36])
        elif value == 'underutilized':
            return queryset.filter(weekly_periods__lt=23)
        elif value == 'no_load':
            return queryset.filter(weekly_periods=0)
        return queryset
    
    def filter_years_of_service_gte(self, queryset, name, value):
        """Filter by minimum years of service"""
        try:
            years = int(value)
            target_date = timezone.now().date() - timedelta(days=years * 365)
            return queryset.filter(employment_date__lte=target_date)
        except (ValueError, TypeError):
            return queryset
    
    def filter_years_of_service_lte(self, queryset, name, value):
        """Filter by maximum years of service"""
        try:
            years = int(value)
            target_date = timezone.now().date() - timedelta(days=years * 365)
            return queryset.filter(employment_date__gte=target_date)
        except (ValueError, TypeError):
            return queryset
    
    order_by = django_filters.OrderingFilter(
        fields=(
            ('teacher__last_name', 'last_name'),
            ('teacher__first_name', 'first_name'),
            ('tsc_number', 'tsc_number'),
            ('employment_date', 'employment_date'),
            ('weekly_periods', 'weekly_periods'),
            ('performance_rating', 'performance_rating'),
        )
    )

class TeacherExportFilter(TeacherProfileFilter):
    """Filter for teacher exports with minimal fields for performance"""
    
    export_format = django_filters.ChoiceFilter(
        method='filter_export',
        choices=[
            ('csv', 'CSV'),
            ('excel', 'Excel'),
            ('pdf', 'PDF')
        ]
    )
    
    def filter_export(self, queryset, name, value):
        """Optimize queryset for export"""
        # Select only needed fields for export
        return queryset.only(
            'tsc_number',
            'teacher__first_name',
            'teacher__last_name',
            'teacher__email',
            'department__name',
            'employment_status'
        )

# ============================================================================
# END OF FILE
# ============================================================================