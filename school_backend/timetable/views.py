from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Timetable, Period, TimetableEntry, TeacherTimetable, ClassTimetable,
    Room, RoomBooking, TimetableAdjustment, SpecialSchedule,
    TimetableConflict, TeacherAvailability
)
from .serializers import (
    TimetableSerializer, PeriodSerializer, TimetableEntrySerializer,
    TeacherTimetableSerializer, ClassTimetableSerializer, RoomSerializer,
    RoomBookingSerializer, TimetableAdjustmentSerializer, SpecialScheduleSerializer,
    TimetableConflictSerializer, TeacherAvailabilitySerializer,
    TimetableGenerateSerializer, TimetableImportSerializer, DailyTimetableSerializer
)
from accounts.permissions import IsAdminUser, IsTeacherUser, IsHeadTeacherUser

# Timetable Management Views
class TimetableView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get current active timetable"""
        try:
            timetable = Timetable.objects.filter(is_active=True).first()
            if not timetable:
                return Response(
                    {'error': 'No active timetable found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = TimetableSerializer(timetable)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class TimetableGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsHeadTeacherUser]

    def post(self, request):
        """Generate timetable automatically"""
        serializer = TimetableGenerateSerializer(data=request.data)
        if serializer.is_valid():
            # This would implement complex timetable generation logic
            # For now, return a placeholder response
            return Response(
                {'message': 'Timetable generation feature will be implemented soon.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClassTimetableView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, class_id):
        """Get timetable for a specific class"""
        try:
            # Get current active timetable
            timetable = Timetable.objects.filter(is_active=True).first()
            if not timetable:
                return Response(
                    {'error': 'No active timetable found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get class timetable entries
            entries = ClassTimetable.objects.filter(
                class_assigned_id=class_id,
                timetable_entry__timetable=timetable
            ).order_by('day', 'period_number')
            
            # Group by day
            timetable_data = {}
            days_order = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
            
            for day in days_order:
                day_entries = entries.filter(day=day)
                timetable_data[day] = ClassTimetableSerializer(day_entries, many=True).data
            
            return Response({
                'timetable': TimetableSerializer(timetable).data,
                'class_timetable': timetable_data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class TeacherTimetableView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, teacher_id=None):
        """Get timetable for a specific teacher or current teacher"""
        try:
            if teacher_id:
                # Get specific teacher's timetable
                teacher_timetable = TeacherTimetable.objects.filter(teacher_id=teacher_id)
            else:
                # Get current teacher's timetable
                if hasattr(request.user, 'teacher_profile'):
                    teacher_timetable = TeacherTimetable.objects.filter(
                        teacher=request.user.teacher_profile
                    )
                else:
                    return Response(
                        {'error': 'Teacher profile not found.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get current active timetable
            timetable = Timetable.objects.filter(is_active=True).first()
            if timetable:
                teacher_timetable = teacher_timetable.filter(
                    timetable_entry__timetable=timetable
                )
            
            # Group by day
            timetable_data = {}
            days_order = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
            
            for day in days_order:
                day_entries = teacher_timetable.filter(day=day).order_by('period_number')
                timetable_data[day] = TeacherTimetableSerializer(day_entries, many=True).data
            
            return Response({
                'timetable': TimetableSerializer(timetable).data if timetable else None,
                'teacher_timetable': timetable_data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class StudentTimetableView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id=None):
        """Get timetable for a specific student or current student"""
        try:
            if student_id:
                from students.models import StudentProfile
                student = StudentProfile.objects.get(id=student_id)
            else:
                if hasattr(request.user, 'student_profile'):
                    student = request.user.student_profile
                else:
                    return Response(
                        {'error': 'Student profile not found.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get student's current class
            current_enrollment = student.enrollments.filter(status='active').first()
            if not current_enrollment:
                return Response(
                    {'error': 'No active enrollment found for student.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get class timetable
            return ClassTimetableView().get(request, current_enrollment.class_enrolled.id)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

# Room Management Views
class RoomListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['room_type', 'is_active', 'is_bookable']
    search_fields = ['name', 'location', 'facilities']
    ordering_fields = ['name', 'capacity', 'room_type']
    ordering = ['name']

    def get_queryset(self):
        return Room.objects.all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permission() for permission in [IsAdminUser | IsHeadTeacherUser]]
        return [permission() for permission in self.permission_classes]

class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsHeadTeacherUser]
    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    lookup_field = 'pk'

class RoomBookingListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RoomBookingSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['room', 'booking_type', 'status', 'teacher', 'class_assigned']
    ordering_fields = ['start_datetime', 'end_datetime']
    ordering = ['start_datetime']

    def get_queryset(self):
        if self.request.user.role in ['admin', 'head_teacher']:
            return RoomBooking.objects.select_related(
                'room', 'booked_by', 'teacher__user', 'class_assigned', 'approved_by'
            ).all()
        else:
            return RoomBooking.objects.filter(
                Q(booked_by=self.request.user) | Q(teacher__user=self.request.user)
            ).select_related(
                'room', 'booked_by', 'teacher__user', 'class_assigned', 'approved_by'
            )

    def perform_create(self, serializer):
        serializer.save(booked_by=self.request.user)

class RoomAvailabilityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, room_id):
        """Check room availability for a specific date and time"""
        date = request.GET.get('date')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        
        if not date or not start_time or not end_time:
            return Response(
                {'error': 'Date, start_time, and end_time are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            room = Room.objects.get(id=room_id)
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
            target_start = datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M')
            target_end = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M')
            
            # Check for conflicts
            conflicting_bookings = RoomBooking.objects.filter(
                room=room,
                start_datetime__lt=target_end,
                end_datetime__gt=target_start,
                status__in=['scheduled', 'confirmed']
            )
            
            is_available = not conflicting_bookings.exists()
            
            response_data = {
                'room': RoomSerializer(room).data,
                'date': date,
                'start_time': start_time,
                'end_time': end_time,
                'is_available': is_available,
                'conflicting_bookings': RoomBookingSerializer(conflicting_bookings, many=True).data if not is_available else []
            }
            
            return Response(response_data)
            
        except Room.DoesNotExist:
            return Response(
                {'error': 'Room not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': 'Invalid date or time format.'},
                status=status.HTTP_400_BAD_REQUEST
            )

# Timetable Adjustment Views
class TimetableAdjustmentListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TimetableAdjustmentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['adjustment_type', 'is_active', 'is_notified', 'adjustment_date']
    ordering_fields = ['adjustment_date', 'created_at']
    ordering = ['-adjustment_date']

    def get_queryset(self):
        return TimetableAdjustment.objects.select_related(
            'timetable_entry', 'original_teacher__user', 'substitute_teacher__user',
            'requested_by', 'approved_by'
        ).all()

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

class TimetableAdjustmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsHeadTeacherUser]
    serializer_class = TimetableAdjustmentSerializer
    queryset = TimetableAdjustment.objects.all()
    lookup_field = 'pk'

# Special Schedule Views
class SpecialScheduleListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SpecialScheduleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['academic_year', 'term', 'special_type', 'is_published']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'end_date', 'title']
    ordering = ['-start_date']

    def get_queryset(self):
        return SpecialSchedule.objects.select_related(
            'academic_year', 'term', 'created_by'
        ).prefetch_related('affected_classes', 'affected_teachers__user').all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permission() for permission in [IsAdminUser | IsHeadTeacherUser]]
        return [permission() for permission in self.permission_classes]

# Teacher Availability Views
class TeacherAvailabilityListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeacherAvailabilitySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['teacher', 'availability_type', 'is_available', 'is_approved']
    ordering_fields = ['start_date', 'day_of_week']
    ordering = ['teacher', 'start_date']

    def get_queryset(self):
        if self.request.user.role in ['admin', 'head_teacher']:
            return TeacherAvailability.objects.select_related('teacher__user').all()
        elif hasattr(self.request.user, 'teacher_profile'):
            return TeacherAvailability.objects.filter(teacher=self.request.user.teacher_profile)
        else:
            return TeacherAvailability.objects.none()

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'teacher_profile'):
            serializer.save(teacher=self.request.user.teacher_profile)
        else:
            raise serializers.ValidationError("Only teachers can set availability.")

# Timetable Conflict Views
class TimetableConflictListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsHeadTeacherUser]
    serializer_class = TimetableConflictSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['conflict_type', 'severity', 'is_resolved', 'conflict_date']
    ordering_fields = ['conflict_date', 'severity']
    ordering = ['-conflict_date', 'severity']

    def get_queryset(self):
        return TimetableConflict.objects.select_related(
            'timetable_entry_1', 'timetable_entry_2', 'room_booking', 'resolved_by'
        ).all()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def daily_schedule(request):
    """Get daily schedule for a specific date"""
    date_str = request.GET.get('date')
    if not date_str:
        date_str = timezone.now().date().isoformat()
    
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        day_name = target_date.strftime('%A').upper()
        
        # Get current timetable
        timetable = Timetable.objects.filter(is_active=True).first()
        if not timetable:
            return Response(
                {'error': 'No active timetable found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get regular timetable entries for the day
        regular_entries = TimetableEntry.objects.filter(
            timetable=timetable,
            day=day_name,
            is_active=True
        ).select_related('subject', 'teacher__user', 'class_assigned', 'period')
        
        # Check for special schedules
        special_schedules = SpecialSchedule.objects.filter(
            start_date__lte=target_date,
            end_date__gte=target_date,
            is_published=True
        )
        
        # Check for adjustments
        adjustments = TimetableAdjustment.objects.filter(
            adjustment_date=target_date,
            is_active=True
        )
        
        daily_data = {
            'date': target_date,
            'day_name': day_name,
            'regular_entries': TimetableEntrySerializer(regular_entries, many=True).data,
            'special_schedules': SpecialScheduleSerializer(special_schedules, many=True).data,
            'adjustments': TimetableAdjustmentSerializer(adjustments, many=True).data
        }
        
        serializer = DailyTimetableSerializer(daily_data)
        return Response(serializer.data)
        
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD.'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsAdminUser | IsHeadTeacherUser])
def publish_timetable(request, timetable_id):
    """Publish a timetable"""
    try:
        timetable = Timetable.objects.get(id=timetable_id)
        timetable.is_published = True
        timetable.save()
        
        # Precompute teacher and class timetables for performance
        precompute_derived_timetables(timetable)
        
        return Response({'message': 'Timetable published successfully.'})
        
    except Timetable.DoesNotExist:
        return Response(
            {'error': 'Timetable not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

def precompute_derived_timetables(timetable):
    """Precompute teacher and class timetables for better performance"""
    # Clear existing entries
    TeacherTimetable.objects.filter(timetable_entry__timetable=timetable).delete()
    ClassTimetable.objects.filter(timetable_entry__timetable=timetable).delete()
    
    # Get all timetable entries
    entries = TimetableEntry.objects.filter(timetable=timetable, is_active=True)
    
    teacher_timetables = []
    class_timetables = []
    
    for entry in entries:
        # Create teacher timetable entry
        teacher_timetables.append(TeacherTimetable(
            teacher=entry.teacher,
            timetable_entry=entry,
            day=entry.day,
            period_number=entry.period.period_number,
            start_time=entry.period.start_time,
            end_time=entry.period.end_time,
            subject_name=entry.subject.name,
            class_name=entry.class_assigned.name,
            room=entry.room
        ))
        
        # Create class timetable entry
        class_timetables.append(ClassTimetable(
            class_assigned=entry.class_assigned,
            timetable_entry=entry,
            day=entry.day,
            period_number=entry.period.period_number,
            start_time=entry.period.start_time,
            end_time=entry.period.end_time,
            subject_name=entry.subject.name,
            teacher_name=entry.teacher.user.get_full_name(),
            room=entry.room
        ))
    
    # Bulk create for performance
    TeacherTimetable.objects.bulk_create(teacher_timetables)
    ClassTimetable.objects.bulk_create(class_timetables)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def timetable_conflicts_check(request):
    """Check for timetable conflicts"""
    try:
        timetable = Timetable.objects.filter(is_active=True).first()
        if not timetable:
            return Response(
                {'error': 'No active timetable found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        conflicts = check_timetable_conflicts(timetable)
        return Response({
            'timetable': TimetableSerializer(timetable).data,
            'conflicts_found': len(conflicts),
            'conflicts': conflicts
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

def check_timetable_conflicts(timetable):
    """Check for various types of timetable conflicts"""
    conflicts = []
    
    # Get all timetable entries
    entries = TimetableEntry.objects.filter(timetable=timetable, is_active=True)
    
    # Check for teacher double bookings
    teacher_entries = {}
    for entry in entries:
        key = (entry.day, entry.period.period_number, entry.teacher.id)
        if key in teacher_entries:
            conflicts.append({
                'type': 'teacher_double_booking',
                'severity': 'high',
                'teacher': entry.teacher.user.get_full_name(),
                'day': entry.day,
                'period': entry.period.period_number,
                'conflict_between': [
                    f"{teacher_entries[key].class_assigned.name} - {teacher_entries[key].subject.name}",
                    f"{entry.class_assigned.name} - {entry.subject.name}"
                ]
            })
        else:
            teacher_entries[key] = entry
    
    # Check for room double bookings
    room_entries = {}
    for entry in entries:
        if entry.room:
            key = (entry.day, entry.period.period_number, entry.room)
            if key in room_entries:
                conflicts.append({
                    'type': 'room_double_booking',
                    'severity': 'medium',
                    'room': entry.room,
                    'day': entry.day,
                    'period': entry.period.period_number,
                    'conflict_between': [
                        f"{room_entries[key].class_assigned.name} - {room_entries[key].teacher.user.get_full_name()}",
                        f"{entry.class_assigned.name} - {entry.teacher.user.get_full_name()}"
                    ]
                })
            else:
                room_entries[key] = entry
    
    return conflicts