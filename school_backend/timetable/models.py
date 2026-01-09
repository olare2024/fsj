from django.db import models
from django.conf import settings
import uuid

class Timetable(models.Model):
    DAY_CHOICES = (
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
    )

    PERIOD_TYPES = (
        ('academic', 'Academic Period'),
        ('break', 'Break'),
        ('assembly', 'Assembly'),
        ('sports', 'Sports/Games'),
        ('clubs', 'Clubs/Societies'),
        ('remedial', 'Remedial Classes'),
        ('prep', 'Preparation Time'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE)
    term = models.ForeignKey('academics.AcademicTerm', on_delete=models.CASCADE)
    
    # Timetable details
    name = models.CharField(max_length=100, help_text="e.g., Term 1 Timetable 2024")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    
    # Schedule settings
    days_operational = models.JSONField(default=list, help_text="Days when school is operational")
    periods_per_day = models.IntegerField(default=8)
    period_duration = models.IntegerField(default=40, help_text="Duration in minutes")
    
    # Timings
    school_start_time = models.TimeField(default='08:00')
    school_end_time = models.TimeField(default='16:00')
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Timetable"
        verbose_name_plural = "Timetables"
        unique_together = ['academic_year', 'term', 'name']
        ordering = ['-academic_year', '-term', 'name']

    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"

    def save(self, *args, **kwargs):
        # Ensure only one active timetable per academic year and term
        if self.is_active:
            Timetable.objects.filter(
                academic_year=self.academic_year,
                term=self.term,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

class Period(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='periods')
    
    # Period details
    period_number = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    period_type = models.CharField(max_length=20, choices=Timetable.PERIOD_TYPES, default='academic')
    
    # Break specific fields
    is_break = models.BooleanField(default=False)
    break_name = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., Morning Break, Lunch")
    break_duration = models.IntegerField(null=True, blank=True, help_text="Duration in minutes")
    
    # Additional information
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Period"
        verbose_name_plural = "Periods"
        unique_together = ['timetable', 'period_number']
        ordering = ['timetable', 'period_number']

    def __str__(self):
        if self.is_break:
            return f"{self.timetable.name} - {self.break_name}"
        return f"{self.timetable.name} - Period {self.period_number}"

class TimetableEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='entries')
    
    # Scheduling details
    day = models.CharField(max_length=10, choices=Timetable.DAY_CHOICES)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    
    # Academic assignment
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE)
    teacher = models.ForeignKey('accounts.TeacherProfile', on_delete=models.CASCADE)
    class_assigned = models.ForeignKey('academics.Class', on_delete=models.CASCADE)
    
    # Location
    room = models.CharField(max_length=50, blank=True, null=True)
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Recurrence (for special schedules)
    is_recurring = models.BooleanField(default=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Timetable Entry"
        verbose_name_plural = "Timetable Entries"
        unique_together = ['timetable', 'day', 'period', 'class_assigned']
        ordering = ['day', 'period__period_number']

    def __str__(self):
        return f"{self.day} - {self.period} - {self.class_assigned.name} - {self.subject.name}"

class TeacherTimetable(models.Model):
    """Precomputed teacher timetable for quick access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey('accounts.TeacherProfile', on_delete=models.CASCADE, related_name='TeacherTimetable_entries')
    timetable_entry = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE)
    
    # Denormalized fields for performance
    day = models.CharField(max_length=10, choices=Timetable.DAY_CHOICES)
    period_number = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject_name = models.CharField(max_length=200)
    class_name = models.CharField(max_length=100)
    room = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Teacher Timetable"
        verbose_name_plural = "Teacher Timetables"
        unique_together = ['teacher', 'timetable_entry']
        ordering = ['day', 'period_number']

    def __str__(self):
        return f"{self.teacher.user.get_full_name()} - {self.day} P{self.period_number}"

class ClassTimetable(models.Model):
    """Precomputed class timetable for quick access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_assigned = models.ForeignKey('academics.Class', on_delete=models.CASCADE, related_name='timetable_class_new_entries')
    timetable_entry = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE)
    
    # Denormalized fields for performance
    day = models.CharField(max_length=10, choices=Timetable.DAY_CHOICES)
    period_number = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject_name = models.CharField(max_length=200)
    teacher_name = models.CharField(max_length=200)
    room = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Class Timetable"
        verbose_name_plural = "Class Timetables"
        unique_together = ['class_assigned', 'timetable_entry']
        ordering = ['day', 'period_number']

    def __str__(self):
        return f"{self.class_assigned.name} - {self.day} P{self.period_number}"

class Room(models.Model):
    ROOM_TYPES = (
        ('classroom', 'Classroom'),
        ('laboratory', 'Laboratory'),
        ('library', 'Library'),
        ('computer_lab', 'Computer Lab'),
        ('art_room', 'Art Room'),
        ('music_room', 'Music Room'),
        ('sports_hall', 'Sports Hall'),
        ('auditorium', 'Auditorium'),
        ('conference', 'Conference Room'),
        ('staff_room', 'Staff Room'),
        ('other', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='classroom')
    capacity = models.IntegerField(default=30)
    location = models.CharField(max_length=100, blank=True, null=True)
    
    # Facilities
    facilities = models.JSONField(default=list, help_text="Available facilities and equipment")
    special_requirements = models.TextField(blank=True, null=True)
    
    # Availability
    is_active = models.BooleanField(default=True)
    is_bookable = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

class RoomBooking(models.Model):
    BOOKING_STATUS = (
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    BOOKING_TYPES = (
        ('regular', 'Regular Class'),
        ('exam', 'Examination'),
        ('meeting', 'Meeting'),
        ('event', 'Event'),
        ('special_class', 'Special Class'),
        ('other', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    
    # Booking details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPES, default='regular')
    
    # Timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.JSONField(default=dict, blank=True, null=True)
    
    # Booking party
    booked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='room_bookings')
    teacher = models.ForeignKey('accounts.TeacherProfile', on_delete=models.CASCADE, null=True, blank=True)
    class_assigned = models.ForeignKey('academics.Class', on_delete=models.CASCADE, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='scheduled')
    approval_required = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bookings')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Additional information
    attendees_count = models.IntegerField(default=0)
    special_requirements = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Room Booking"
        verbose_name_plural = "Room Bookings"
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['room', 'start_datetime', 'end_datetime']),
            models.Index(fields=['status', 'start_datetime']),
        ]

    def __str__(self):
        return f"{self.room.name} - {self.title} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"

class TimetableAdjustment(models.Model):
    ADJUSTMENT_TYPES = (
        ('substitution', 'Teacher Substitution'),
        ('room_change', 'Room Change'),
        ('cancellation', 'Class Cancellation'),
        ('time_change', 'Time Change'),
        ('special_event', 'Special Event'),
        ('emergency', 'Emergency Adjustment'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timetable_entry = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE, related_name='adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    
    # Adjustment details
    original_teacher = models.ForeignKey('accounts.TeacherProfile', on_delete=models.CASCADE, related_name='original_adjustments')
    substitute_teacher = models.ForeignKey('accounts.TeacherProfile', on_delete=models.CASCADE, null=True, blank=True, related_name='substitute_adjustments')
    original_room = models.CharField(max_length=50, blank=True, null=True)
    new_room = models.CharField(max_length=50, blank=True, null=True)
    original_time = models.CharField(max_length=100, blank=True, null=True)
    new_time = models.CharField(max_length=100, blank=True, null=True)
    
    # Date range
    adjustment_date = models.DateField()
    effective_from = models.DateTimeField(null=True, blank=True)
    effective_to = models.DateTimeField(null=True, blank=True)
    
    # Reason and notes
    reason = models.TextField()
    notes = models.TextField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)
    
    # Approval
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_adjustments')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_adjustments')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Timetable Adjustment"
        verbose_name_plural = "Timetable Adjustments"
        ordering = ['-adjustment_date', 'timetable_entry']
        indexes = [
            models.Index(fields=['adjustment_date', 'is_active']),
        ]

    def __str__(self):
        return f"{self.adjustment_type} - {self.timetable_entry} - {self.adjustment_date}"

class SpecialSchedule(models.Model):
    SPECIAL_TYPES = (
        ('exam', 'Examination Schedule'),
        ('event', 'Special Event'),
        ('holiday', 'Holiday Schedule'),
        ('staff_development', 'Staff Development'),
        ('parent_meeting', 'Parent-Teacher Meeting'),
        ('sports_day', 'Sports Day'),
        ('cultural_day', 'Cultural Day'),
        ('other', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE)
    term = models.ForeignKey('academics.AcademicTerm', on_delete=models.CASCADE, null=True, blank=True)
    
    # Schedule details
    title = models.CharField(max_length=200)
    special_type = models.CharField(max_length=20, choices=SPECIAL_TYPES)
    description = models.TextField(blank=True, null=True)
    
    # Timing
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    # Affected entities
    affected_classes = models.ManyToManyField('academics.Class', blank=True)
    affected_teachers = models.ManyToManyField('accounts.TeacherProfile', blank=True)
    is_whole_school = models.BooleanField(default=False)
    
    # Regular timetable handling
    suspend_regular_timetable = models.BooleanField(default=False)
    modified_timetable = models.JSONField(default=dict, blank=True, null=True, help_text="Modified timetable for this period")
    
    # Status
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Special Schedule"
        verbose_name_plural = "Special Schedules"
        ordering = ['-start_date', 'title']

    def __str__(self):
        return f"{self.title} - {self.start_date} to {self.end_date}"

class TimetableConflict(models.Model):
    CONFLICT_TYPES = (
        ('teacher_double_booking', 'Teacher Double Booking'),
        ('room_double_booking', 'Room Double Booking'),
        ('class_double_booking', 'Class Double Booking'),
        ('teacher_unavailable', 'Teacher Unavailable'),
        ('room_unavailable', 'Room Unavailable'),
        ('time_conflict', 'Time Conflict'),
    )

    SEVERITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conflict_type = models.CharField(max_length=30, choices=CONFLICT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    
    # Conflicting entries
    timetable_entry_1 = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE, related_name='conflicts_as_first')
    timetable_entry_2 = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE, related_name='conflicts_as_second', null=True, blank=True)
    room_booking = models.ForeignKey(RoomBooking, on_delete=models.CASCADE, null=True, blank=True)
    
    # Conflict details
    conflict_date = models.DateField()
    conflict_time = models.CharField(max_length=100)
    description = models.TextField()
    
    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True, null=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Timetable Conflict"
        verbose_name_plural = "Timetable Conflicts"
        ordering = ['-conflict_date', 'severity']
        indexes = [
            models.Index(fields=['conflict_date', 'is_resolved']),
        ]

    def __str__(self):
        return f"{self.conflict_type} - {self.conflict_date} - {self.severity}"

class TeacherAvailability(models.Model):
    AVAILABILITY_TYPES = (
        ('regular', 'Regular Availability'),
        ('leave', 'Leave'),
        ('meeting', 'Meeting'),
        ('professional_development', 'Professional Development'),
        ('other', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey('accounts.TeacherProfile', on_delete=models.CASCADE, related_name='availabilities')
    
    # Availability details
    availability_type = models.CharField(max_length=30, choices=AVAILABILITY_TYPES, default='regular')
    day_of_week = models.CharField(max_length=10, choices=Timetable.DAY_CHOICES, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    # For specific date ranges
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_all_day = models.BooleanField(default=False)
    
    # Details
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Status
    is_available = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Teacher Availability"
        verbose_name_plural = "Teacher Availabilities"
        ordering = ['teacher', 'start_date', 'day_of_week']
        indexes = [
            models.Index(fields=['teacher', 'is_available', 'start_date']),
        ]

    def __str__(self):
        if self.day_of_week:
            return f"{self.teacher.user.get_full_name()} - {self.day_of_week} - {'Available' if self.is_available else 'Unavailable'}"
        return f"{self.teacher.user.get_full_name()} - {self.start_date} to {self.end_date} - {'Available' if self.is_available else 'Unavailable'}"