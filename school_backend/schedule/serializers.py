from rest_framework import serializers
from .models import (
    Period, Curriculum, GradeLevel, Timetable, 
    BreakTime, CurriculumSubjectMapping
)
from academic.models import AllocatedSubject
from academic.serializers import (
    ClassRoomSerializer,
    SubjectSerializer,
)
from users.serializers import TeacherSerializer
from administration.serializers import TermSerializer


class CurriculumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['id', 'name', 'description', 'is_active']
        read_only_fields = ['id']


class GradeLevelSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source='curriculum.get_name_display', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = GradeLevel
        fields = ['id', 'curriculum', 'curriculum_name', 'grade', 'name', 'full_name']
        read_only_fields = ['id']

    def get_full_name(self, obj):
        return f"{obj.curriculum.get_name_display()} - {obj.name}"


class CurriculumSubjectMappingSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source='curriculum.get_name_display', read_only=True)
    grade_level_name = serializers.CharField(source='grade_level.name', read_only=True)
    subject_name = serializers.CharField(source='subject.subject.name', read_only=True)

    class Meta:
        model = CurriculumSubjectMapping
        fields = [
            'id', 'curriculum', 'curriculum_name', 'grade_level', 'grade_level_name',
            'subject', 'subject_name', 'is_core', 'periods_per_week'
        ]
        read_only_fields = ['id']


class PeriodSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    classroom = ClassRoomSerializer(read_only=True)
    curriculum_name = serializers.CharField(source='curriculum.get_name_display', read_only=True)
    grade_level_name = serializers.CharField(source='grade_level.name', read_only=True)
    
    # Writeable fields for creation/update
    curriculum_id = serializers.PrimaryKeyRelatedField(
        queryset=Curriculum.objects.all(), source='curriculum', write_only=True, required=False
    )
    grade_level_id = serializers.PrimaryKeyRelatedField(
        queryset=GradeLevel.objects.all(), source='grade_level', write_only=True, required=False
    )
    allocated_subject_id = serializers.PrimaryKeyRelatedField(
        queryset=AllocatedSubject.objects.all(), source='allocated_subject', write_only=True, required=False
    )

    class Meta:
        model = Period
        fields = [
            "id", "day_of_week", "start_time", "end_time", "teacher", "subject",
            "classroom", "curriculum", "curriculum_name", "grade_level", "grade_level_name",
            "is_active", "curriculum_id", "grade_level_id", "allocated_subject_id"
        ]
        read_only_fields = ["id", "teacher", "subject", "classroom"]

    def create(self, validated_data):
        """
        Override create to handle dynamic assignment from allocated_subject
        or direct curriculum/grade level assignment.
        """
        allocated_subject = validated_data.pop('allocated_subject', None)
        curriculum = validated_data.pop('curriculum', None)
        grade_level = validated_data.pop('grade_level', None)

        if allocated_subject:
            # Use allocated_subject to automatically set relationships
            teacher = allocated_subject.teacher
            subject = allocated_subject.subject
            classroom = allocated_subject.class_room
            
            # Auto-detect curriculum and grade level from allocated_subject if not provided
            if not curriculum:
                # You might want to add curriculum/grade_level to AllocatedSubject model
                # For now, we'll handle it through direct assignment
                pass

            period = Period.objects.create(
                **validated_data,
                teacher=teacher,
                subject=subject,
                classroom=classroom,
                curriculum=curriculum,
                grade_level=grade_level,
            )
        else:
            # Direct creation with provided data
            if not curriculum or not grade_level:
                raise serializers.ValidationError({
                    "error": "Both curriculum and grade_level are required when not using allocated_subject."
                })
            
            period = Period.objects.create(**validated_data)

        return period

    def validate(self, data):
        """
        Validate period constraints across different curricula.
        """
        day_of_week = data.get('day_of_week')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        classroom = data.get('classroom')
        curriculum = data.get('curriculum')
        
        # Check for time conflicts
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time."
            })

        # Check for classroom conflicts (same curriculum, same day/time)
        if day_of_week and start_time and classroom and curriculum:
            conflicting_periods = Period.objects.filter(
                day_of_week=day_of_week,
                classroom=classroom,
                curriculum=curriculum,
                is_active=True
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            # Check for time overlap
            for period in conflicting_periods:
                if (start_time < period.end_time and end_time > period.start_time):
                    raise serializers.ValidationError({
                        "classroom": f"Classroom already occupied by {period.subject} at this time."
                    })

        return data


class BreakTimeSerializer(serializers.ModelSerializer):
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = BreakTime
        fields = [
            'id', 'timetable', 'break_type', 'start_time', 'end_time',
            'duration_minutes', 'duration_display'
        ]
        read_only_fields = ['id', 'duration_minutes']

    def get_duration_display(self, obj):
        return f"{obj.duration_minutes} minutes"


class TimetableSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(source='curriculum.get_name_display', read_only=True)
    grade_level_name = serializers.CharField(source='grade_level.name', read_only=True)
    periods = PeriodSerializer(many=True, read_only=True)
    breaks = BreakTimeSerializer(many=True, read_only=True)
    period_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Timetable
        fields = [
            'id', 'name', 'curriculum', 'curriculum_name', 'grade_level', 'grade_level_name',
            'term', 'academic_year', 'periods', 'breaks', 'is_active', 'period_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_period_count(self, obj):
        return obj.periods.count()

    def validate(self, data):
        """
        Validate timetable constraints.
        """
        curriculum = data.get('curriculum')
        grade_level = data.get('grade_level')
        term = data.get('term')
        academic_year = data.get('academic_year')

        # Check for duplicate timetables
        if Timetable.objects.filter(
            curriculum=curriculum,
            grade_level=grade_level,
            term=term,
            academic_year=academic_year
        ).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError({
                "error": "A timetable for this curriculum, grade level, term and academic year already exists."
            })

        return data


class TimetableDetailSerializer(TimetableSerializer):
    """Extended serializer with full period details"""
    periods = PeriodSerializer(many=True, read_only=True)
    breaks = BreakTimeSerializer(many=True, read_only=True)


class CurriculumTimetableSerializer(serializers.Serializer):
    """Serializer for curriculum-specific timetable requests"""
    curriculum = serializers.ChoiceField(choices=Curriculum.CURRICULUM_CHOICES)
    grade_level = serializers.IntegerField(min_value=1, max_value=12)
    term = serializers.IntegerField(min_value=1, max_value=3)
    academic_year = serializers.CharField(max_length=9)


class BulkPeriodCreateSerializer(serializers.Serializer):
    """Serializer for bulk period creation"""
    periods_data = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_periods_data(self, value):
        """Validate each period in bulk creation"""
        for period_data in value:
            if not all(k in period_data for k in ['day_of_week', 'start_time', 'end_time', 'classroom_id']):
                raise serializers.ValidationError("Each period must contain day_of_week, start_time, end_time, and classroom_id.")
        return value