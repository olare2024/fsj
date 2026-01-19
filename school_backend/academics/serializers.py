# academics/serializers.py

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Avg, Count, Max, Min, Q
from django.contrib.auth import get_user_model

from accounts.models import User
from .models import *


# ============================================================================
# CUSTOM SERIALIZER BASE CLASSES
# ============================================================================

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """ModelSerializer with dynamic field selection"""
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        
        if fields:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class TimestampSerializer(serializers.ModelSerializer):
    """Base serializer with timestamp fields"""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class UserRelatedSerializer(serializers.ModelSerializer):
    """Base serializer for user-related models"""
    user_info = serializers.SerializerMethodField()
    
    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'name': obj.user.get_full_name(),
            'email': obj.user.email,
        }


# ============================================================================
# HELPER SERIALIZERS
# ============================================================================

class UserBasicSerializer(DynamicFieldsModelSerializer):
    """Basic user serializer"""
    full_name = serializers.SerializerMethodField()
    profile_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'profile_picture', 'profile_url'
        ]
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_profile_url(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None


class StudentMinimalSerializer(UserBasicSerializer):
    """Minimal student serializer"""
    class Meta(UserBasicSerializer.Meta):
        fields = [
            'id', 'username', 'student_id', 'full_name',
            'profile_picture', 'profile_url'
        ]


class TeacherMinimalSerializer(UserBasicSerializer):
    """Minimal teacher serializer"""
    class Meta(UserBasicSerializer.Meta):
        fields = [
            'id', 'username', 'teacher_id', 'full_name',
            'profile_picture', 'profile_url', 'qualification'
        ]


class SubjectMinimalSerializer(DynamicFieldsModelSerializer):
    """Minimal subject serializer"""
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'credit_hours', 'category']
        read_only_fields = fields


class ClassMinimalSerializer(DynamicFieldsModelSerializer):
    """Minimal class serializer"""
    grade_level_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'code', 'grade_level', 'grade_level_info']
        read_only_fields = fields
    
    def get_grade_level_info(self, obj):
        if obj.grade_level:
            return {
                'id': obj.grade_level.id,
                'name': obj.grade_level.name,
                'code': obj.grade_level.code,
            }
        return None


# ============================================================================
# VALIDATION SERIALIZERS
# ============================================================================

class BaseValidationSerializer(serializers.Serializer):
    """Base validation serializer"""
    
    def validate_percentage(self, value, field_name):
        """Validate percentage fields"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                _(f"{field_name} must be between 0 and 100")
            )
        return value
    
    def validate_date_range(self, start_date, end_date):
        """Validate date range"""
        if end_date < start_date:
            raise serializers.ValidationError(_("End date must be after start date"))
        return True


class AcademicPeriodValidationSerializer(BaseValidationSerializer):
    """Validate academic period"""
    academic_year = serializers.CharField(max_length=20)
    term = serializers.ChoiceField(choices=TermType.choices)
    
    def validate_academic_year(self, value):
        try:
            years = value.split('-')
            if len(years) != 2:
                raise serializers.ValidationError(
                    _("Academic year must be in format YYYY-YYYY")
                )
            year1, year2 = int(years[0]), int(years[1])
            if year2 != year1 + 1:
                raise serializers.ValidationError(
                    _("Second year must be one greater than first year")
                )
        except (ValueError, IndexError):
            raise serializers.ValidationError(_("Invalid academic year format"))
        return value


class DateRangeValidationSerializer(BaseValidationSerializer):
    """Validate date range"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    def validate(self, data):
        self.validate_date_range(data['start_date'], data['end_date'])
        return data


# ============================================================================
# ACADEMIC STRUCTURE SERIALIZERS
# ============================================================================

class AcademicYearSerializer(TimestampSerializer):
    """Academic Year serializer with statistics"""
    is_current = serializers.BooleanField(read_only=True)
    statistics = serializers.SerializerMethodField()
    term_dates = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicYear
        fields = [
            'id', 'name', 'academic_year', 'term',
            'start_date', 'end_date', 'is_current', 'description',
            'first_term_start', 'first_term_end',
            'second_term_start', 'second_term_end',
            'third_term_start', 'third_term_end',
            'min_attendance_percentage', 'passing_grade', 'max_absent_days',
            'statistics', 'term_dates',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'is_current', 'statistics'
        ]
    
    def validate(self, data):
        # Validate academic year format
        serializer = AcademicPeriodValidationSerializer(data={
            'academic_year': data.get('academic_year'),
            'term': data.get('term')
        })
        serializer.is_valid(raise_exception=True)
        
        # Validate date ranges
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError(_("End date must be after start date"))
        
        return data
    
    def get_statistics(self, obj):
        from .models import Enrollment, TeacherAssignment, Class
        return {
            'student_count': Enrollment.objects.filter(
                academic_year=obj.academic_year,
                term=obj.term,
                status='active'
            ).count(),
            'teacher_count': TeacherAssignment.objects.filter(
                academic_year=obj.academic_year,
                term=obj.term,
                is_active=True
            ).values('teacher').distinct().count(),
            'class_count': Class.objects.filter(
                academic_year=obj.academic_year,
                term=obj.term
            ).count(),
        }
    
    def get_term_dates(self, obj):
        return {
            'first_term': {
                'start': obj.first_term_start,
                'end': obj.first_term_end,
                'days': obj.get_days_in_term(TermType.FIRST_TERM)
            },
            'second_term': {
                'start': obj.second_term_start,
                'end': obj.second_term_end,
                'days': obj.get_days_in_term(TermType.SECOND_TERM)
            },
            'third_term': {
                'start': obj.third_term_start,
                'end': obj.third_term_end,
                'days': obj.get_days_in_term(TermType.THIRD_TERM)
            } if obj.third_term_start and obj.third_term_end else None
        }


class AcademicTermSerializer(TimestampSerializer):
    """Academic Term serializer"""
    academic_year_info = serializers.SerializerMethodField()
    duration_info = serializers.SerializerMethodField()
    enrollment_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = AcademicTerm
        fields = [
            'id', 'academic_year', 'academic_year_info', 'name', 'term_type',
            'start_date', 'end_date', 'is_current', 'registration_deadline',
            'fee_payment_deadline', 'examination_start', 'examination_end',
            'closing_date', 'next_term_starts', 'total_instructional_days',
            'total_holidays', 'minimum_attendance_days', 'minimum_pass_percentage',
            'assessment_weight', 'fee_structure', 'description', 'enrollment_count',
            'duration_info', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'enrollment_count', 'duration_info'
        ]
    
    def get_academic_year_info(self, obj):
        return {
            'id': obj.academic_year.id,
            'name': obj.academic_year.name,
            'academic_year': obj.academic_year.academic_year,
        }
    
    def get_duration_info(self, obj):
        return {
            'duration_days': obj.duration_days,
            'days_remaining': obj.days_remaining,
            'is_active': obj.is_active,
        }


class GradeLevelSerializer(TimestampSerializer):
    """Grade Level serializer"""
    statistics = serializers.SerializerMethodField()
    next_grade_info = serializers.SerializerMethodField()
    
    class Meta:
        model = GradeLevel
        fields = [
            'id', 'name', 'code', 'level', 'order', 'description',
            'age_range_min', 'age_range_max', 'next_grade', 'next_grade_info',
            'curriculum', 'max_students', 'statistics',
            'created_at', 'updated_at'
        ]
    
    def get_statistics(self, obj):
        return {
            'student_count': obj.student_count,
            'available_slots': obj.available_slots,
            'utilization_percentage': (
                (obj.student_count / obj.max_students * 100) 
                if obj.max_students > 0 else 0
            )
        }
    
    def get_next_grade_info(self, obj):
        if obj.next_grade:
            return {
                'id': obj.next_grade.id,
                'name': obj.next_grade.name,
                'code': obj.next_grade.code,
            }
        return None


class SubjectSerializer(TimestampSerializer):
    """Subject serializer"""
    statistics = serializers.SerializerMethodField()
    prerequisites_info = serializers.SerializerMethodField()
    grade_levels_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'code', 'description', 'grade_levels', 'grade_levels_info',
            'is_core', 'category', 'credit_hours', 'passing_score', 'max_score',
            'department', 'prerequisites', 'prerequisites_info', 'syllabus',
            'statistics', 'created_at', 'updated_at'
        ]
    
    def get_statistics(self, obj):
        return {
            'teacher_count': len(obj.get_teachers()),
            'student_count': obj.get_student_count(),
            'average_score': obj.get_average_score(),
        }
    
    def get_prerequisites_info(self, obj):
        return [
            {'id': p.id, 'name': p.name, 'code': p.code}
            for p in obj.prerequisites.all()
        ]
    
    def get_grade_levels_info(self, obj):
        return [
            {'id': gl.id, 'name': gl.name, 'code': gl.code}
            for gl in obj.grade_levels.all()
        ]


# ============================================================================
# STUDENT MANAGEMENT SERIALIZERS
# ============================================================================

class EnrollmentSerializer(TimestampSerializer):
    """Student Enrollment serializer"""
    student_info = serializers.SerializerMethodField()
    class_info = serializers.SerializerMethodField()
    academic_performance = serializers.SerializerMethodField()
    attendance_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_info', 'class_assigned', 'class_info',
            'academic_year', 'term', 'enrollment_date', 'enrollment_type',
            'enrollment_number', 'status', 'academic_status', 'remarks',
            'academic_performance', 'attendance_summary', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'enrollment_number', 'academic_performance', 'attendance_summary',
            'created_at', 'updated_at'
        ]
    
    def get_student_info(self, obj):
        return {
            'id': obj.student.id,
            'name': obj.student.get_full_name(),
            'email': obj.student.email,
            'student_id': obj.student.student_id,
            'profile_picture': obj.student.profile_picture.url 
                if obj.student.profile_picture else None,
        }
    
    def get_class_info(self, obj):
        return {
            'id': obj.class_assigned.id,
            'name': obj.class_assigned.name,
            'code': obj.class_assigned.code,
            'grade_level': obj.class_assigned.grade_level.name,
            'form_teacher': obj.class_assigned.form_teacher.get_full_name() 
                if obj.class_assigned.form_teacher else None,
        }
    
    def get_academic_performance(self, obj):
        return obj.get_academic_performance()
    
    def get_attendance_summary(self, obj):
        return obj.get_attendance_summary()


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating enrollments"""
    class Meta:
        model = Enrollment
        fields = ['student', 'class_assigned', 'academic_year', 'term', 'enrollment_type']


class SubjectEnrollmentSerializer(TimestampSerializer):
    """Subject Enrollment serializer"""
    enrollment_info = serializers.SerializerMethodField()
    subject_info = serializers.SerializerMethodField()
    teacher_info = serializers.SerializerMethodField()
    performance = serializers.SerializerMethodField()
    
    class Meta:
        model = SubjectEnrollment
        fields = [
            'id', 'enrollment', 'enrollment_info', 'subject', 'subject_info',
            'teacher', 'teacher_info', 'academic_year', 'term', 'enrollment_date',
            'status', 'grade', 'score', 'credits_earned', 'remarks', 'performance',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['performance', 'created_at', 'updated_at']
    
    def get_enrollment_info(self, obj):
        return {
            'id': obj.enrollment.id,
            'student_name': obj.enrollment.student.get_full_name(),
            'class_name': obj.enrollment.class_assigned.name,
        }
    
    def get_subject_info(self, obj):
        return {
            'id': obj.subject.id,
            'name': obj.subject.name,
            'code': obj.subject.code,
            'credit_hours': obj.subject.credit_hours,
        }
    
    def get_teacher_info(self, obj):
        if obj.teacher:
            return {
                'id': obj.teacher.id,
                'name': obj.teacher.get_full_name(),
                'email': obj.teacher.email,
            }
        return None
    
    def get_performance(self, obj):
        return {
            'assessment_grades': obj.get_assessment_grades(),
            'is_passing': obj.score >= obj.subject.passing_score 
                if obj.score else None,
            'final_grade': obj.grade,
        }


# ============================================================================
# ASSESSMENT & GRADING SERIALIZERS
# ============================================================================

class AssessmentSerializer(TimestampSerializer):
    """Assessment serializer"""
    statistics = serializers.SerializerMethodField()
    subject_info = serializers.SerializerMethodField()
    class_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Assessment
        fields = [
            'id', 'name', 'code', 'subject', 'subject_info', 'class_assigned', 'class_info',
            'assessment_type', 'date', 'start_time', 'end_time', 'total_marks',
            'passing_marks', 'weight', 'description', 'instructions', 'academic_year',
            'term', 'is_published', 'published_date', 'created_by', 'statistics',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'statistics', 'published_date', 'created_at', 'updated_at'
        ]
    
    def get_statistics(self, obj):
        return {
            'class_average': obj.get_class_average(),
            'pass_rate': obj.get_pass_rate(),
            'total_students': Grade.objects.filter(assessment=obj).count(),
        }
    
    def get_subject_info(self, obj):
        return SubjectMinimalSerializer(obj.subject).data
    
    def get_class_info(self, obj):
        return ClassMinimalSerializer(obj.class_assigned).data


class GradeSerializer(TimestampSerializer):
    """Grade serializer"""
    student_info = serializers.SerializerMethodField()
    assessment_info = serializers.SerializerMethodField()
    subject_info = serializers.SerializerMethodField()
    performance_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_info', 'assessment', 'assessment_info',
            'subject', 'subject_info', 'class_assigned', 'enrollment', 'score',
            'grade', 'grade_point', 'percentage', 'remarks', 'is_absent',
            'is_exempted', 'graded_by', 'graded_date', 'performance_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'grade', 'grade_point', 'percentage', 'performance_info',
            'created_at', 'updated_at'
        ]
    
    def get_student_info(self, obj):
        return StudentMinimalSerializer(obj.student).data
    
    def get_assessment_info(self, obj):
        return {
            'id': obj.assessment.id,
            'name': obj.assessment.name,
            'type': obj.assessment.get_assessment_type_display(),
            'total_marks': obj.assessment.total_marks,
        }
    
    def get_subject_info(self, obj):
        return SubjectMinimalSerializer(obj.subject).data
    
    def get_performance_info(self, obj):
        return {
            'is_passing': obj.is_passing,
            'grade_description': obj.grade_description,
        }


class GradeBulkCreateSerializer(BaseValidationSerializer):
    """Bulk grade creation serializer"""
    assessment = serializers.PrimaryKeyRelatedField(queryset=Assessment.objects.all())
    grades = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_grades(self, value):
        for grade_data in value:
            required_fields = ['student_id', 'score']
            for field in required_fields:
                if field not in grade_data:
                    raise serializers.ValidationError(
                        _(f"Missing required field: {field}")
                    )
            
            # Validate student exists
            try:
                User.objects.get(id=grade_data['student_id'], role='student')
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    _(f"Student not found: {grade_data['student_id']}")
                )
            
            # Validate score range
            if grade_data['score'] < 0:
                raise serializers.ValidationError(_("Score cannot be negative"))
        
        return value
    
    def create(self, validated_data):
        assessment = validated_data['assessment']
        grades_data = validated_data['grades']
        request_user = self.context.get('request').user
        
        created_grades = []
        errors = []
        
        for grade_data in grades_data:
            try:
                student = User.objects.get(id=grade_data['student_id'], role='student')
                
                # Get enrollment
                enrollment = Enrollment.objects.filter(
                    student=student,
                    academic_year=assessment.academic_year,
                    term=assessment.term,
                    class_assigned=assessment.class_assigned,
                    status='active'
                ).first()
                
                if not enrollment:
                    errors.append({
                        'student_id': grade_data['student_id'],
                        'error': _("Student not enrolled in this class")
                    })
                    continue
                
                # Create grade
                grade = Grade.objects.create(
                    student=student,
                    assessment=assessment,
                    subject=assessment.subject,
                    class_assigned=assessment.class_assigned,
                    enrollment=enrollment,
                    score=grade_data['score'],
                    remarks=grade_data.get('remarks', ''),
                    is_absent=grade_data.get('is_absent', False),
                    is_exempted=grade_data.get('is_exempted', False),
                    graded_by=request_user,
                )
                
                created_grades.append(grade)
                
            except Exception as e:
                errors.append({
                    'student_id': grade_data.get('student_id'),
                    'error': str(e)
                })
        
        return {
            'created': len(created_grades),
            'errors': errors,
            'grades': GradeSerializer(created_grades, many=True).data
        }


class TranscriptSerializer(TimestampSerializer):
    """Transcript serializer"""
    student_info = serializers.SerializerMethodField()
    academic_performance = serializers.SerializerMethodField()
    generated_by_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Transcript
        fields = [
            'id', 'student', 'student_info', 'academic_year', 'term',
            'gpa', 'cgpa', 'total_credits', 'credits_earned',
            'class_rank', 'grade_level_rank', 'overall_rank',
            'remarks', 'generated_by', 'generated_by_info',
            'generated_date', 'is_official', 'document',
            'academic_performance', 'created_at', 'updated_at'
        ]
    
    def get_student_info(self, obj):
        return StudentMinimalSerializer(obj.student).data
    
    def get_academic_performance(self, obj):
        from .models import Grade
        
        grades = Grade.objects.filter(
            student=obj.student,
            assessment__academic_year=obj.academic_year,
            assessment__term=obj.term
        ).select_related('subject', 'assessment')
        
        subject_data = {}
        for grade in grades:
            subject_id = grade.subject.id
            if subject_id not in subject_data:
                subject_data[subject_id] = {
                    'subject': SubjectMinimalSerializer(grade.subject).data,
                    'grades': [],
                    'scores': [],
                }
            
            subject_data[subject_id]['grades'].append({
                'assessment': grade.assessment.name,
                'type': grade.assessment.get_assessment_type_display(),
                'score': float(grade.score),
                'grade': grade.grade,
            })
            subject_data[subject_id]['scores'].append(float(grade.score))
        
        # Calculate averages
        result = []
        for subject_id, data in subject_data.items():
            avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            result.append({
                'subject': data['subject'],
                'average_score': avg_score,
                'grades': data['grades'],
            })
        
        return result
    
    def get_generated_by_info(self, obj):
        if obj.generated_by:
            return TeacherMinimalSerializer(obj.generated_by).data
        return None


# ============================================================================
# ATTENDANCE SERIALIZERS
# ============================================================================

class AttendanceSerializer(TimestampSerializer):
    """Attendance serializer"""
    student_info = serializers.SerializerMethodField()
    class_info = serializers.SerializerMethodField()
    duration_info = serializers.SerializerMethodField()
    verified_by_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_info', 'enrollment', 'class_assigned', 'class_info',
            'academic_year', 'term', 'date', 'status', 'check_in_time', 'check_out_time',
            'reason', 'medical_certificate', 'parent_note', 'verified_by', 'verified_by_info',
            'verified_date', 'remarks', 'duration_info', 'created_at', 'updated_at'
        ]
        read_only_fields = ['duration_info', 'created_at', 'updated_at']
    
    def get_student_info(self, obj):
        return StudentMinimalSerializer(obj.student).data
    
    def get_class_info(self, obj):
        return ClassMinimalSerializer(obj.class_assigned).data
    
    def get_duration_info(self, obj):
        duration = obj.duration
        return {
            'duration_minutes': duration.seconds // 60 if duration else None,
            'duration_hours': duration.seconds // 3600 if duration else None,
            'is_late': obj.is_late,
        }
    
    def get_verified_by_info(self, obj):
        if obj.verified_by:
            return TeacherMinimalSerializer(obj.verified_by).data
        return None


class AttendanceBulkCreateSerializer(BaseValidationSerializer):
    """Bulk attendance creation serializer"""
    class_assigned = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())
    date = serializers.DateField()
    attendance_records = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate(self, data):
        for record in data['attendance_records']:
            required_fields = ['student_id', 'status']
            for field in required_fields:
                if field not in record:
                    raise serializers.ValidationError(
                        _(f"Missing required field: {field}")
                    )
            
            # Validate student enrollment
            try:
                student = User.objects.get(id=record['student_id'], role='student')
                enrollment = Enrollment.objects.filter(
                    student=student,
                    class_assigned=data['class_assigned'],
                    academic_year=data['class_assigned'].academic_year,
                    term=data['class_assigned'].term,
                    status='active'
                ).first()
                
                if not enrollment:
                    raise serializers.ValidationError(
                        _(f"Student {student.get_full_name()} not enrolled in this class")
                    )
                    
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    _(f"Student not found: {record['student_id']}")
                )
        
        return data
    
    def create(self, validated_data):
        class_obj = validated_data['class_assigned']
        date = validated_data['date']
        records = validated_data['attendance_records']
        request_user = self.context.get('request').user
        
        created_attendance = []
        errors = []
        
        for record in records:
            try:
                student = User.objects.get(id=record['student_id'], role='student')
                enrollment = Enrollment.objects.get(
                    student=student,
                    class_assigned=class_obj,
                    academic_year=class_obj.academic_year,
                    term=class_obj.term,
                    status='active'
                )
                
                attendance, created = Attendance.objects.update_or_create(
                    student=student,
                    date=date,
                    defaults={
                        'enrollment': enrollment,
                        'class_assigned': class_obj,
                        'academic_year': class_obj.academic_year,
                        'term': class_obj.term,
                        'status': record['status'],
                        'reason': record.get('reason', ''),
                        'check_in_time': record.get('check_in_time'),
                        'check_out_time': record.get('check_out_time'),
                        'verified_by': request_user,
                        'verified_date': timezone.now(),
                    }
                )
                
                created_attendance.append(attendance)
                
            except Exception as e:
                errors.append({
                    'student_id': record.get('student_id'),
                    'error': str(e)
                })
        
        return {
            'created': len(created_attendance),
            'errors': errors,
            'attendance': AttendanceSerializer(created_attendance, many=True).data
        }


class AttendanceReportSerializer(TimestampSerializer):
    """Attendance Report serializer"""
    student_info = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    warnings = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceReport
        fields = [
            'id', 'student', 'student_info', 'enrollment', 'academic_year', 'term',
            'period_start', 'period_end', 'total_school_days', 'days_present',
            'days_absent', 'days_late', 'days_excused', 'attendance_percentage',
            'consecutive_absences', 'frequent_absence_pattern', 'is_at_risk',
            'warning_level', 'parent_notified', 'last_notification_date',
            'remarks', 'generated_by', 'generated_date', 'statistics', 'warnings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['statistics', 'warnings', 'created_at', 'updated_at']
    
    def get_student_info(self, obj):
        return StudentMinimalSerializer(obj.student).data
    
    def get_statistics(self, obj):
        return {
            'present_percentage': (obj.days_present / obj.total_school_days * 100) 
                if obj.total_school_days > 0 else 0,
            'absent_percentage': (obj.days_absent / obj.total_school_days * 100) 
                if obj.total_school_days > 0 else 0,
            'late_percentage': (obj.days_late / obj.total_school_days * 100) 
                if obj.total_school_days > 0 else 0,
        }
    
    def get_warnings(self, obj):
        warnings = []
        if obj.is_at_risk:
            warnings.append({
                'level': obj.warning_level,
                'message': _("Attendance below minimum threshold"),
                'attendance_percentage': obj.attendance_percentage,
            })
        
        if obj.consecutive_absences >= 3:
            warnings.append({
                'level': 'warning',
                'message': _(f"{obj.consecutive_absences} consecutive absences detected"),
                'recommendation': _("Contact student/parent"),
            })
        
        return warnings


# ============================================================================
# TIMETABLE SERIALIZERS
# ============================================================================

class ScheduleSerializer(TimestampSerializer):
    """Schedule serializer"""
    subject_info = serializers.SerializerMethodField()
    teacher_info = serializers.SerializerMethodField()
    class_info = serializers.SerializerMethodField()
    classroom_info = serializers.SerializerMethodField()
    timing_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'class_assigned', 'class_info', 'subject', 'subject_info',
            'teacher', 'teacher_info', 'classroom', 'classroom_info',
            'day_of_week', 'start_time', 'end_time', 'academic_year', 'term',
            'is_recurring', 'start_date', 'end_date', 'is_active', 'color_code',
            'description', 'timing_info', 'created_at', 'updated_at'
        ]
        read_only_fields = ['timing_info', 'created_at', 'updated_at']
    
    def get_subject_info(self, obj):
        return SubjectMinimalSerializer(obj.subject).data
    
    def get_teacher_info(self, obj):
        return TeacherMinimalSerializer(obj.teacher).data
    
    def get_class_info(self, obj):
        return ClassMinimalSerializer(obj.class_assigned).data
    
    def get_classroom_info(self, obj):
        if obj.classroom:
            return {
                'id': obj.classroom.id,
                'room_number': obj.classroom.room_number,
                'name': obj.classroom.name,
                'capacity': obj.classroom.capacity,
            }
        return None
    
    def get_timing_info(self, obj):
        return {
            'duration_minutes': obj.duration,
            'is_current': obj.is_current,
        }


class TeacherAssignmentSerializer(TimestampSerializer):
    """Teacher Assignment serializer"""
    teacher_info = serializers.SerializerMethodField()
    subject_info = serializers.SerializerMethodField()
    class_info = serializers.SerializerMethodField()
    assignment_info = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherAssignment
        fields = [
            'id', 'teacher', 'teacher_info', 'subject', 'subject_info',
            'class_assigned', 'class_info', 'academic_year', 'term',
            'is_class_teacher', 'assignment_type', 'hours_per_week',
            'start_date', 'end_date', 'is_active', 'remarks', 'assignment_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['assignment_info', 'created_at', 'updated_at']
    
    def get_teacher_info(self, obj):
        return TeacherMinimalSerializer(obj.teacher).data
    
    def get_subject_info(self, obj):
        return SubjectMinimalSerializer(obj.subject).data
    
    def get_class_info(self, obj):
        return ClassMinimalSerializer(obj.class_assigned).data
    
    def get_assignment_info(self, obj):
        return {
            'duration_days': obj.duration,
            'teaching_hours': obj.get_teaching_hours(),
        }


# ============================================================================
# CLASS MANAGEMENT SERIALIZERS
# ============================================================================

class ClassSerializer(TimestampSerializer):
    """Class serializer"""
    statistics = serializers.SerializerMethodField()
    grade_level_info = serializers.SerializerMethodField()
    teacher_info = serializers.SerializerMethodField()
    classroom_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = [
            'id', 'name', 'code', 'grade_level', 'grade_level_info',
            'academic_year', 'term', 'classroom', 'classroom_info',
            'form_teacher', 'teacher_info', 'assistant_teacher',
            'max_students', 'students_count', 'description', 'statistics',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'students_count', 'statistics', 'created_at', 'updated_at'
        ]
    
    def get_statistics(self, obj):
        return {
            'available_slots': obj.available_slots,
            'utilization_percentage': (
                (obj.students_count / obj.max_students * 100) 
                if obj.max_students > 0 else 0
            ),
            'performance_summary': obj.get_average_performance(),
            'attendance_summary': obj.get_attendance_summary(),
        }
    
    def get_grade_level_info(self, obj):
        if obj.grade_level:
            return {
                'id': obj.grade_level.id,
                'name': obj.grade_level.name,
                'code': obj.grade_level.code,
            }
        return None
    
    def get_teacher_info(self, obj):
        teachers = {}
        if obj.form_teacher:
            teachers['form_teacher'] = TeacherMinimalSerializer(obj.form_teacher).data
        if obj.assistant_teacher:
            teachers['assistant_teacher'] = TeacherMinimalSerializer(obj.assistant_teacher).data
        return teachers
    
    def get_classroom_info(self, obj):
        if obj.classroom:
            return {
                'id': obj.classroom.id,
                'room_number': obj.classroom.room_number,
                'name': obj.classroom.name,
                'capacity': obj.classroom.capacity,
            }
        return None


# ============================================================================
# COMPETENCY-BASED EDUCATION SERIALIZERS
# ============================================================================

class CompetencyAreaSerializer(TimestampSerializer):
    """Competency Area serializer"""
    grade_levels_info = serializers.SerializerMethodField()
    subjects_info = serializers.SerializerMethodField()
    parent_area_info = serializers.SerializerMethodField()
    assessment_info = serializers.SerializerMethodField()
    
    class Meta:
        model = CompetencyArea
        fields = [
            'id', 'name', 'code', 'description', 'curriculum', 'grade_levels',
            'grade_levels_info', 'subjects', 'subjects_info', 'assessment_method',
            'levels', 'parent_area', 'parent_area_info', 'is_core', 'order',
            'assessment_info', 'created_at', 'updated_at'
        ]
        read_only_fields = ['assessment_info', 'created_at', 'updated_at']
    
    def get_grade_levels_info(self, obj):
        return [
            {'id': gl.id, 'name': gl.name, 'code': gl.code}
            for gl in obj.grade_levels.all()
        ]
    
    def get_subjects_info(self, obj):
        return [
            {'id': s.id, 'name': s.name, 'code': s.code}
            for s in obj.subjects.all()
        ]
    
    def get_parent_area_info(self, obj):
        if obj.parent_area:
            return {
                'id': obj.parent_area.id,
                'name': obj.parent_area.name,
                'code': obj.parent_area.code,
            }
        return None
    
    def get_assessment_info(self, obj):
        return {
            'student_count': obj.student_count,
            'levels': obj.get_competency_levels(),
        }


class CompetencyAssessmentSerializer(TimestampSerializer):
    """Competency Assessment serializer"""
    student_info = serializers.SerializerMethodField()
    competency_area_info = serializers.SerializerMethodField()
    grade_level_info = serializers.SerializerMethodField()
    assessed_by_info = serializers.SerializerMethodField()
    verified_by_info = serializers.SerializerMethodField()
    
    class Meta:
        model = CompetencyAssessment
        fields = [
            'id', 'student', 'student_info', 'competency_area', 'competency_area_info',
            'academic_year', 'term', 'grade_level', 'grade_level_info', 'score', 'level',
            'assessed_by', 'assessed_by_info', 'assessment_date', 'evidence', 'comments',
            'is_verified', 'verified_by', 'verified_by_info', 'verified_date',
            'created_at', 'updated_at'
        ]
    
    def get_student_info(self, obj):
        return StudentMinimalSerializer(obj.student).data
    
    def get_competency_area_info(self, obj):
        return {
            'id': obj.competency_area.id,
            'name': obj.competency_area.name,
            'code': obj.competency_area.code,
        }
    
    def get_grade_level_info(self, obj):
        if obj.grade_level:
            return {
                'id': obj.grade_level.id,
                'name': obj.grade_level.name,
                'code': obj.grade_level.code,
            }
        return None
    
    def get_assessed_by_info(self, obj):
        if obj.assessed_by:
            return TeacherMinimalSerializer(obj.assessed_by).data
        return None
    
    def get_verified_by_info(self, obj):
        if obj.verified_by:
            return TeacherMinimalSerializer(obj.verified_by).data
        return None


# ============================================================================
# INFRASTRUCTURE SERIALIZERS
# ============================================================================

class ClassroomSerializer(TimestampSerializer):
    """Classroom serializer"""
    current_status = serializers.SerializerMethodField()
    facilities_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Classroom
        fields = [
            'id', 'room_number', 'name', 'building', 'floor', 'capacity',
            'facilities', 'facilities_info', 'is_special', 'special_type',
            'description', 'is_available', 'current_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['current_status', 'created_at', 'updated_at']
    
    def get_current_status(self, obj):
        current_class = obj.current_class
        if current_class:
            return {
                'is_occupied': True,
                'current_class': {
                    'id': current_class.id,
                    'name': current_class.name,
                    'teacher': current_class.teacher.get_full_name() 
                        if current_class.teacher else None,
                }
            }
        return {'is_occupied': False}
    
    def get_facilities_info(self, obj):
        return obj.facilities if isinstance(obj.facilities, list) else []


# ============================================================================
# EVENTS AND CONFIGURATION SERIALIZERS
# ============================================================================

class AcademicEventSerializer(TimestampSerializer):
    """Academic Event serializer"""
    participants_info = serializers.SerializerMethodField()
    affected_classes_info = serializers.SerializerMethodField()
    event_details = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicEvent
        fields = [
            'id', 'title', 'event_type', 'start_date', 'end_date',
            'start_time', 'end_time', 'academic_year', 'term',
            'description', 'location', 'organizer', 'participants',
            'participants_info', 'affected_classes', 'affected_classes_info',
            'is_holiday', 'color_code', 'event_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['event_details', 'created_at', 'updated_at']
    
    def get_participants_info(self, obj):
        return [
            {'id': user.id, 'name': user.get_full_name(), 'role': user.role}
            for user in obj.participants.all()
        ]
    
    def get_affected_classes_info(self, obj):
        return [
            {'id': class_obj.id, 'name': class_obj.name, 'code': class_obj.code}
            for class_obj in obj.affected_classes.all()
        ]
    
    def get_event_details(self, obj):
        return {
            'duration_days': obj.duration_days,
            'is_current': obj.is_current(),
        }


class GradingScaleSerializer(TimestampSerializer):
    """Grading Scale serializer"""
    scale_info = serializers.SerializerMethodField()
    
    class Meta:
        model = GradingScale
        fields = [
            'id', 'name', 'scale_type', 'academic_level', 'curriculum',
            'is_default', 'grade_ranges', 'description', 'scale_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['scale_info', 'created_at', 'updated_at']
    
    def get_scale_info(self, obj):
        return {
            'total_ranges': len(obj.grade_ranges),
            'points_range': {
                'min': min(r['points'] for r in obj.grade_ranges) 
                    if obj.grade_ranges else 0,
                'max': max(r['points'] for r in obj.grade_ranges) 
                    if obj.grade_ranges else 4.0,
            }
        }


# ============================================================================
# DASHBOARD AND ANALYTICS SERIALIZERS
# ============================================================================

class DashboardStatsSerializer(serializers.Serializer):
    """Dashboard statistics"""
    overview = serializers.SerializerMethodField()
    attendance = serializers.SerializerMethodField()
    performance = serializers.SerializerMethodField()
    upcoming = serializers.SerializerMethodField()
    
    def get_overview(self, obj):
        from .models import Enrollment, User, Class
        return {
            'total_students': User.objects.filter(role='student').count(),
            'total_teachers': User.objects.filter(role='teacher').count(),
            'total_classes': Class.objects.count(),
            'total_subjects': Subject.objects.count(),
        }
    
    def get_attendance(self, obj):
        from .models import Attendance
        today = timezone.now().date()
        attendance = Attendance.objects.filter(date=today)
        
        return {
            'today_present': attendance.filter(status='present').count(),
            'today_absent': attendance.filter(status='absent').count(),
            'today_late': attendance.filter(status='late').count(),
            'attendance_rate': (
                attendance.filter(status='present').count() / attendance.count() * 100
                if attendance.count() > 0 else 0
            ),
        }
    
    def get_performance(self, obj):
        from .models import Grade
        grades = Grade.objects.all()
        
        return {
            'average_score': grades.aggregate(Avg('score'))['score__avg'] or 0,
            'top_performing_class': self._get_top_performing_class(),
            'pass_rate': (
                grades.filter(is_passing=True).count() / grades.count() * 100
                if grades.count() > 0 else 0
            ),
        }
    
    def get_upcoming(self, obj):
        from .models import Assessment, AcademicEvent
        today = timezone.now().date()
        next_week = today + timezone.timedelta(days=7)
        
        return {
            'upcoming_assessments': Assessment.objects.filter(
                date__gte=today, date__lte=next_week
            ).count(),
            'upcoming_events': AcademicEvent.objects.filter(
                start_date__gte=today, start_date__lte=next_week
            ).count(),
        }
    
    def _get_top_performing_class(self):
        from .models import Grade, Class
        from django.db.models import Avg
        
        top_class = Class.objects.annotate(
            avg_score=Avg('grades__score')
        ).order_by('-avg_score').first()
        
        return top_class.name if top_class else None


class PerformanceAnalyticsSerializer(serializers.Serializer):
    """Performance analytics"""
    period = serializers.ChoiceField(choices=['daily', 'weekly', 'monthly', 'yearly'])
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError(_("End date must be after start date"))
        return data


# ============================================================================
# EXPORT SERIALIZERS
# ============================================================================

class ExportSerializerMixin:
    """Mixin for export serializers"""
    
    @staticmethod
    def get_export_fields():
        """Define export field mapping"""
        return {
            'id': 'ID',
            'name': 'Name',
            'code': 'Code',
            'date': 'Date',
            'status': 'Status',
            'score': 'Score',
            'grade': 'Grade',
        }


class GradeExportSerializer(serializers.Serializer, ExportSerializerMixin):
    """Grade export serializer"""
    student_id = serializers.CharField(source='student.student_id')
    student_name = serializers.CharField(source='student.get_full_name')
    student_class = serializers.CharField(source='class_assigned.name')
    subject = serializers.CharField(source='subject.name')
    assessment = serializers.CharField(source='assessment.name')
    score = serializers.FloatField()
    grade = serializers.CharField()
    percentage = serializers.FloatField()
    assessment_date = serializers.DateField(source='assessment.date')
    graded_by = serializers.CharField(source='graded_by.get_full_name')
    
    class Meta:
        fields = [
            'student_id', 'student_name', 'student_class', 'subject',
            'assessment', 'score', 'grade', 'percentage', 'assessment_date',
            'graded_by'
        ]


class AttendanceExportSerializer(serializers.Serializer, ExportSerializerMixin):
    """Attendance export serializer"""
    student_id = serializers.CharField(source='student.student_id')
    student_name = serializers.CharField(source='student.get_full_name')
    student_class = serializers.CharField(source='class_assigned.name')
    date = serializers.DateField()
    status = serializers.CharField()
    check_in_time = serializers.TimeField(allow_null=True)
    check_out_time = serializers.TimeField(allow_null=True)
    reason = serializers.CharField(allow_null=True)
    verified_by = serializers.CharField(
        source='verified_by.get_full_name', 
        allow_null=True
    )
    
    class Meta:
        fields = [
            'student_id', 'student_name', 'student_class', 'date',
            'status', 'check_in_time', 'check_out_time', 'reason',
            'verified_by'
        ]


# ============================================================================
# ACADEMIC REPORT SERIALIZERS
# ============================================================================

class AcademicReportSerializer(TimestampSerializer):
    """Academic Report serializer"""
    student_info = serializers.SerializerMethodField()
    enrollment_info = serializers.SerializerMethodField()
    performance_summary = serializers.SerializerMethodField()
    subject_performance = serializers.SerializerMethodField()
    generated_by_info = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicReport
        fields = [
            'id', 'student', 'student_info', 'enrollment', 'enrollment_info',
            'academic_year', 'term', 'report_type', 'report_date', 'gpa', 'cgpa',
            'overall_score', 'class_rank', 'grade_level_rank', 'overall_rank',
            'total_credits', 'credits_earned', 'attendance_rate', 'conduct_rating',
            'extracurricular_activities', 'achievements', 'strengths', 'areas_for_improvement',
            'form_teacher_comment', 'head_teacher_comment', 'parent_feedback',
            'recommendations', 'next_term_expectations', 'is_published',
            'published_date', 'generated_by', 'generated_by_info', 'document',
            'performance_summary', 'subject_performance',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'performance_summary', 'subject_performance', 'created_at', 'updated_at'
        ]
    
    def get_student_info(self, obj):
        return {
            'id': obj.student.id,
            'name': obj.student.get_full_name(),
            'student_id': obj.student.student_id,
            'profile_picture': obj.student.profile_picture.url 
                if obj.student.profile_picture else None,
        }
    
    def get_enrollment_info(self, obj):
        return {
            'id': obj.enrollment.id,
            'class_name': obj.enrollment.class_assigned.name,
            'grade_level': obj.enrollment.class_assigned.grade_level.name,
            'academic_year': obj.enrollment.academic_year,
            'term': obj.enrollment.term,
        }
    
    def get_performance_summary(self, obj):
        from .models import Grade, Attendance
        
        grades = Grade.objects.filter(
            student=obj.student,
            assessment__academic_year=obj.academic_year,
            assessment__term=obj.term
        )
        
        attendance = Attendance.objects.filter(
            student=obj.student,
            academic_year=obj.academic_year,
            term=obj.term
        )
        
        return {
            'total_subjects': grades.values('subject').distinct().count(),
            'average_score': grades.aggregate(Avg('score'))['score__avg'] or 0,
            'attendance_days': attendance.filter(status='present').count(),
            'total_school_days': attendance.count(),
            'best_subject': self._get_best_subject(grades),
            'weakest_subject': self._get_weakest_subject(grades),
        }
    
    def get_subject_performance(self, obj):
        from .models import Grade
        
        grades = Grade.objects.filter(
            student=obj.student,
            assessment__academic_year=obj.academic_year,
            assessment__term=obj.term
        ).select_related('subject')
        
        subject_data = {}
        for grade in grades:
            subject_id = grade.subject.id
            if subject_id not in subject_data:
                subject_data[subject_id] = {
                    'subject': {
                        'id': grade.subject.id,
                        'name': grade.subject.name,
                        'code': grade.subject.code,
                    },
                    'grades': [],
                    'scores': [],
                }
            
            subject_data[subject_id]['grades'].append({
                'assessment': grade.assessment.name,
                'type': grade.assessment.get_assessment_type_display(),
                'score': float(grade.score),
                'grade': grade.grade,
                'date': grade.assessment.date,
            })
            subject_data[subject_id]['scores'].append(float(grade.score))
        
        # Calculate subject statistics
        result = []
        for subject_id, data in subject_data.items():
            scores = data['scores']
            avg_score = sum(scores) / len(scores) if scores else 0
            max_score = max(scores) if scores else 0
            min_score = min(scores) if scores else 0
            
            result.append({
                'subject': data['subject'],
                'average_score': avg_score,
                'highest_score': max_score,
                'lowest_score': min_score,
                'grade_count': len(scores),
                'grades': data['grades'],
            })
        
        return result
    
    def get_generated_by_info(self, obj):
        if obj.generated_by:
            return {
                'id': obj.generated_by.id,
                'name': obj.generated_by.get_full_name(),
                'role': obj.generated_by.role,
            }
        return None
    
    def _get_best_subject(self, grades):
        from django.db.models import Avg
        
        best = grades.values('subject__name').annotate(
            avg_score=Avg('score')
        ).order_by('-avg_score').first()
        
        return best['subject__name'] if best else None
    
    def _get_weakest_subject(self, grades):
        from django.db.models import Avg
        
        weakest = grades.values('subject__name').annotate(
            avg_score=Avg('score')
        ).order_by('avg_score').first()
        
        return weakest['subject__name'] if weakest else None


# ============================================================================
# BULK OPERATION SERIALIZERS
# ============================================================================

class EnrollmentBulkCreateSerializer(BaseValidationSerializer):
    """Bulk enrollment creation serializer"""
    class_assigned = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())
    academic_year = serializers.CharField()
    term = serializers.CharField()
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    enrollment_type = serializers.ChoiceField(
        choices=[
            ('new', 'New Student'),
            ('transfer', 'Transfer Student'),
            ('repeat', 'Repeating Student'),
            ('promoted', 'Promoted Student'),
        ],
        default='new'
    )
    
    def validate(self, data):
        # Validate students exist and are not already enrolled
        student_ids = data['student_ids']
        class_obj = data['class_assigned']
        academic_year = data['academic_year']
        term = data['term']
        
        existing_enrollments = Enrollment.objects.filter(
            student_id__in=student_ids,
            class_assigned=class_obj,
            academic_year=academic_year,
            term=term,
            status='active'
        ).values_list('student_id', flat=True)
        
        for student_id in student_ids:
            try:
                student = User.objects.get(id=student_id, role='student')
                if student_id in existing_enrollments:
                    raise serializers.ValidationError(
                        _(f"Student {student.get_full_name()} is already enrolled in this class")
                    )
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    _(f"Student not found: {student_id}")
                )
        
        return data
    
    def create(self, validated_data):
        class_obj = validated_data['class_assigned']
        academic_year = validated_data['academic_year']
        term = validated_data['term']
        student_ids = validated_data['student_ids']
        enrollment_type = validated_data['enrollment_type']
        request_user = self.context.get('request').user
        
        created_enrollments = []
        errors = []
        
        for student_id in student_ids:
            try:
                student = User.objects.get(id=student_id, role='student')
                
                # Generate enrollment number
                enrollment_number = Enrollment.generate_enrollment_number(
                    student, class_obj, academic_year, term
                )
                
                # Create enrollment
                enrollment = Enrollment.objects.create(
                    student=student,
                    class_assigned=class_obj,
                    academic_year=academic_year,
                    term=term,
                    enrollment_number=enrollment_number,
                    enrollment_type=enrollment_type,
                    status='active',
                    academic_status='passing',
                    created_by=request_user,
                )
                
                created_enrollments.append(enrollment)
                
            except Exception as e:
                errors.append({
                    'student_id': student_id,
                    'error': str(e)
                })
        
        return {
            'created': len(created_enrollments),
            'errors': errors,
            'enrollments': EnrollmentSerializer(created_enrollments, many=True).data
        }


# ============================================================================
# SETUP AND CONFIGURATION SERIALIZERS
# ============================================================================

class AcademicConfigurationSerializer(TimestampSerializer):
    """Academic Configuration serializer"""
    current_academic_year = serializers.SerializerMethodField()
    current_term = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicConfiguration
        fields = [
            'id', 'academic_year_format', 'term_structure', 'grading_system',
            'minimum_attendance_percentage', 'passing_grade', 'max_absent_days',
            'assessment_weights', 'report_cards_per_year', 'transcript_requirements',
            'competency_assessment_frequency', 'cbc_strands', 'special_needs_support',
            'is_active', 'current_academic_year', 'current_term',
            'created_at', 'updated_at'
        ]
    
    def get_current_academic_year(self, obj):
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year:
            return AcademicYearSerializer(current_year).data
        return None
    
    def get_current_term(self, obj):
        current_term = AcademicTerm.objects.filter(is_current=True).first()
        if current_term:
            return AcademicTermSerializer(current_term).data
        return None


# ============================================================================
# EXPORT SERIALIZERS
# ============================================================================

class StudentPerformanceExportSerializer(serializers.Serializer):
    """Student performance export serializer"""
    student_id = serializers.CharField()
    student_name = serializers.CharField()
    class_name = serializers.CharField()
    grade_level = serializers.CharField()
    average_score = serializers.FloatField()
    attendance_rate = serializers.FloatField()
    gpa = serializers.FloatField()
    class_rank = serializers.IntegerField()
    
    class Meta:
        fields = [
            'student_id', 'student_name', 'class_name', 'grade_level',
            'average_score', 'attendance_rate', 'gpa', 'class_rank'
        ]


# ============================================================================
# API VIEW SERIALIZERS
# ============================================================================

class SetupCheckSerializer(serializers.Serializer):
    """Setup check serializer"""
    is_setup_complete = serializers.BooleanField()
    checks = serializers.DictField()
    missing_items = serializers.ListField()
    missing_count = serializers.IntegerField()
    timestamp = serializers.DateTimeField()


class EssentialDataSerializer(serializers.Serializer):
    """Essential data serializer"""
    academic_years = serializers.ListField()
    grade_levels = serializers.ListField()
    subjects = serializers.ListField()
    classrooms = serializers.ListField()
    competency_areas = serializers.ListField()
    counts = serializers.DictField()
    has_minimum_data = serializers.BooleanField()
    timestamp = serializers.DateTimeField()


class DashboardStatisticsSerializer(serializers.Serializer):
    """Dashboard statistics serializer"""
    overview = serializers.DictField()
    attendance = serializers.DictField()
    performance = serializers.DictField()
    upcoming = serializers.DictField()
    current_academic = serializers.DictField()
    date = serializers.DateField()


class ClassPerformanceSerializer(serializers.Serializer):
    """Class performance serializer"""
    class_id = serializers.IntegerField()
    class_name = serializers.CharField()
    grade_level = serializers.CharField()
    total_students = serializers.IntegerField()
    average_score = serializers.FloatField()
    highest_score = serializers.FloatField()
    lowest_score = serializers.FloatField()
    pass_rate = serializers.FloatField()
    attendance_rate = serializers.FloatField()


class StudentProgressSerializer(serializers.Serializer):
    """Student progress serializer"""
    student = serializers.DictField()
    current_class = serializers.CharField()
    current_grade_level = serializers.CharField()
    current_gpa = serializers.FloatField()
    attendance_percentage = serializers.FloatField()
    improvement_rate = serializers.FloatField()
    subject_progress = serializers.ListField()
    predicted_grade = serializers.CharField(allow_null=True)
    timestamp = serializers.DateTimeField()