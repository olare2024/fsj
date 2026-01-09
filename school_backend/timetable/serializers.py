from rest_framework import serializers
from .models import (
    Timetable, Period, TimetableEntry, TeacherTimetable, ClassTimetable,
    Room, RoomBooking, TimetableAdjustment, SpecialSchedule,
    TimetableConflict, TeacherAvailability
)
from teachers.serializers import TeacherProfileSerializer
from academics.serializers import ClassSerializer, SubjectSerializer, AcademicYearSerializer, AcademicTermSerializer

class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = [
            'id', 'timetable', 'period_number', 'start_time', 'end_time',
            'period_type', 'is_break', 'break_name', 'break_duration',
            'description', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class TimetableSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    term_name = serializers.CharField(source='term.get_name_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    periods = PeriodSerializer(many=True, read_only=True)
    
    class Meta:
        model = Timetable
        fields = [
            'id', 'academic_year', 'academic_year_name', 'term', 'term_name',
            'name', 'description', 'is_active', 'is_published', 'days_operational',
            'periods_per_day', 'period_duration', 'school_start_time',
            'school_end_time', 'periods', 'created_by', 'created_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class TimetableEntrySerializer(serializers.ModelSerializer):
    timetable_name = serializers.CharField(source='timetable.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    class_name = serializers.CharField(source='class_assigned.name', read_only=True)
    period_number = serializers.IntegerField(source='period.period_number', read_only=True)
    start_time = serializers.TimeField(source='period.start_time', read_only=True)
    end_time = serializers.TimeField(source='period.end_time', read_only=True)
    
    class Meta:
        model = TimetableEntry
        fields = [
            'id', 'timetable', 'timetable_name', 'day', 'period', 'period_number',
            'start_time', 'end_time', 'subject', 'subject_name', 'teacher',
            'teacher_name', 'class_assigned', 'class_name', 'room', 'notes',
            'is_active', 'is_recurring', 'valid_from', 'valid_to', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class TeacherTimetableSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    
    class Meta:
        model = TeacherTimetable
        fields = [
            'id', 'teacher', 'teacher_name', 'timetable_entry', 'day',
            'period_number', 'start_time', 'end_time', 'subject_name',
            'class_name', 'room', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ClassTimetableSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_assigned.name', read_only=True)
    
    class Meta:
        model = ClassTimetable
        fields = [
            'id', 'class_assigned', 'class_name', 'timetable_entry', 'day',
            'period_number', 'start_time', 'end_time', 'subject_name',
            'teacher_name', 'room', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class RoomSerializer(serializers.ModelSerializer):
    current_bookings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'room_type', 'capacity', 'location', 'facilities',
            'special_requirements', 'is_active', 'is_bookable', 'current_bookings_count',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_current_bookings_count(self, obj):
        from django.utils import timezone
        return obj.bookings.filter(
            start_datetime__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).count()

class RoomBookingSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)
    room_type = serializers.CharField(source='room.room_type', read_only=True)
    booked_by_name = serializers.CharField(source='booked_by.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    class_name = serializers.CharField(source='class_assigned.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = RoomBooking
        fields = [
            'id', 'room', 'room_name', 'room_type', 'title', 'description',
            'booking_type', 'start_datetime', 'end_datetime', 'is_recurring',
            'recurrence_pattern', 'booked_by', 'booked_by_name', 'teacher',
            'teacher_name', 'class_assigned', 'class_name', 'status',
            'approval_required', 'approved_by', 'approved_by_name', 'approved_at',
            'attendees_count', 'special_requirements', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class TimetableAdjustmentSerializer(serializers.ModelSerializer):
    timetable_entry_details = TimetableEntrySerializer(source='timetable_entry', read_only=True)
    original_teacher_name = serializers.CharField(source='original_teacher.user.get_full_name', read_only=True)
    substitute_teacher_name = serializers.CharField(source='substitute_teacher.user.get_full_name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = TimetableAdjustment
        fields = [
            'id', 'timetable_entry', 'timetable_entry_details', 'adjustment_type',
            'original_teacher', 'original_teacher_name', 'substitute_teacher',
            'substitute_teacher_name', 'original_room', 'new_room', 'original_time',
            'new_time', 'adjustment_date', 'effective_from', 'effective_to',
            'reason', 'notes', 'is_active', 'is_notified', 'notified_at',
            'requested_by', 'requested_by_name', 'approved_by', 'approved_by_name',
            'approved_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class SpecialScheduleSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    term_name = serializers.CharField(source='term.get_name_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    affected_classes_names = serializers.SerializerMethodField()
    affected_teachers_names = serializers.SerializerMethodField()
    
    class Meta:
        model = SpecialSchedule
        fields = [
            'id', 'academic_year', 'academic_year_name', 'term', 'term_name',
            'title', 'special_type', 'description', 'start_date', 'end_date',
            'start_time', 'end_time', 'affected_classes', 'affected_classes_names',
            'affected_teachers', 'affected_teachers_names', 'is_whole_school',
            'suspend_regular_timetable', 'modified_timetable', 'is_published',
            'published_at', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_affected_classes_names(self, obj):
        return [cls.name for cls in obj.affected_classes.all()]
    
    def get_affected_teachers_names(self, obj):
        return [teacher.user.get_full_name() for teacher in obj.affected_teachers.all()]

class TimetableConflictSerializer(serializers.ModelSerializer):
    conflict_type_display = serializers.CharField(source='get_conflict_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    timetable_entry_1_details = TimetableEntrySerializer(source='timetable_entry_1', read_only=True)
    timetable_entry_2_details = TimetableEntrySerializer(source='timetable_entry_2', read_only=True)
    room_booking_details = RoomBookingSerializer(source='room_booking', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)
    
    class Meta:
        model = TimetableConflict
        fields = [
            'id', 'conflict_type', 'conflict_type_display', 'severity', 'severity_display',
            'timetable_entry_1', 'timetable_entry_1_details', 'timetable_entry_2',
            'timetable_entry_2_details', 'room_booking', 'room_booking_details',
            'conflict_date', 'conflict_time', 'description', 'is_resolved',
            'resolution_notes', 'resolved_by', 'resolved_by_name', 'resolved_at',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class TeacherAvailabilitySerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    
    class Meta:
        model = TeacherAvailability
        fields = [
            'id', 'teacher', 'teacher_name', 'availability_type', 'day_of_week',
            'start_time', 'end_time', 'start_date', 'end_date', 'is_all_day',
            'reason', 'notes', 'is_available', 'is_approved', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class TimetableGenerateSerializer(serializers.Serializer):
    academic_year = serializers.UUIDField()
    term = serializers.UUIDField()
    name = serializers.CharField(max_length=100)
    classes = serializers.ListField(child=serializers.UUIDField())
    teachers = serializers.ListField(child=serializers.UUIDField())
    subjects = serializers.ListField(child=serializers.UUIDField())
    
    # Constraints
    max_periods_per_day = serializers.IntegerField(default=8)
    teacher_max_periods_per_day = serializers.IntegerField(default=6)
    prefer_morning_slots = serializers.BooleanField(default=True)
    
    def validate(self, data):
        # Add validation logic here
        return data

class TimetableImportSerializer(serializers.Serializer):
    timetable_file = serializers.FileField()
    academic_year = serializers.UUIDField()
    term = serializers.UUIDField()
    overwrite_existing = serializers.BooleanField(default=False)

class DailyTimetableSerializer(serializers.Serializer):
    date = serializers.DateField()
    day_name = serializers.CharField()
    periods = serializers.ListField()
    special_schedules = SpecialScheduleSerializer(many=True)
    adjustments = TimetableAdjustmentSerializer(many=True)