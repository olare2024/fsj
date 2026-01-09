from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import pandas as pd
import json

from .models import (
    StudentAttendance, TeacherAttendance, StaffAttendance,
    AttendanceSchedule, AttendanceRule, AttendanceReport,
    AttendanceException, BulkAttendanceUpload
)
from .serializers import (
    StudentAttendanceSerializer, TeacherAttendanceSerializer, StaffAttendanceSerializer,
    AttendanceScheduleSerializer, AttendanceRuleSerializer, AttendanceReportSerializer,
    AttendanceExceptionSerializer, BulkAttendanceUploadSerializer,
    BulkAttendanceCreateSerializer, AttendanceStatisticsSerializer,
    ClassAttendanceSummarySerializer
)
from accounts.permissions import IsAdminUser, IsTeacherUser, IsHeadTeacherUser

# Student Attendance Views
class AttendanceRecordView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser | IsAdminUser | IsHeadTeacherUser]

    def post(self, request):
        """Record single student attendance"""
        serializer = StudentAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            # Check if attendance already exists for this student-date-session
            existing_attendance = StudentAttendance.objects.filter(
                student_id=serializer.validated_data['student'].id,
                date=serializer.validated_data['date'],
                session=serializer.validated_data.get('session', 'full_day')
            ).first()
            
            if existing_attendance:
                return Response(
                    {'error': 'Attendance already recorded for this student on this date.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            attendance = serializer.save(recorded_by=request.user)
            return Response(StudentAttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BulkAttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser | IsAdminUser | IsHeadTeacherUser]

    def post(self, request):
        """Record attendance for multiple students at once"""
        serializer = BulkAttendanceCreateSerializer(data=request.data)
        if serializer.is_valid():
            class_enrolled_id = serializer.validated_data['class_enrolled']
            date = serializer.validated_data['date']
            session = serializer.validated_data['session']
            attendance_data = serializer.validated_data['attendance_data']
            
            results = {
                'successful': [],
                'failed': []
            }
            
            for record in attendance_data:
                try:
                    # Check if attendance already exists
                    existing = StudentAttendance.objects.filter(
                        student_id=record['student_id'],
                        date=date,
                        session=session
                    ).exists()
                    
                    if existing:
                        results['failed'].append({
                            'student_id': record['student_id'],
                            'error': 'Attendance already exists'
                        })
                        continue
                    
                    attendance = StudentAttendance.objects.create(
                        student_id=record['student_id'],
                        class_enrolled_id=class_enrolled_id,
                        date=date,
                        session=session,
                        status=record['status'],
                        time_in=record.get('time_in'),
                        time_out=record.get('time_out'),
                        late_minutes=record.get('late_minutes', 0),
                        reason=record.get('reason'),
                        recorded_by=request.user
                    )
                    
                    results['successful'].append({
                        'student_id': record['student_id'],
                        'attendance_id': str(attendance.id)
                    })
                    
                except Exception as e:
                    results['failed'].append({
                        'student_id': record['student_id'],
                        'error': str(e)
                    })
            
            return Response(results, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClassAttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, class_id):
        """Get attendance for a specific class on a specific date or date range"""
        date = request.GET.get('date')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not date and not (start_date and end_date):
            return Response(
                {'error': 'Either date or start_date and end_date are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if date:
                attendances = StudentAttendance.objects.filter(
                    class_enrolled_id=class_id,
                    date=date
                ).select_related('student__user', 'recorded_by')
            else:
                attendances = StudentAttendance.objects.filter(
                    class_enrolled_id=class_id,
                    date__range=[start_date, end_date]
                ).select_related('student__user', 'recorded_by')
            
            serializer = StudentAttendanceSerializer(attendances, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class AttendanceListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentAttendanceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student', 'class_enrolled', 'academic_year', 'term', 'date', 'status']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['date', 'student__user__first_name']
    ordering = ['-date', 'student__user__first_name']

    def get_queryset(self):
        if self.request.user.role in ['admin', 'head_teacher', 'teacher']:
            return StudentAttendance.objects.select_related(
                'student__user', 'class_enrolled', 'academic_year', 'term', 'recorded_by'
            ).all()
        elif hasattr(self.request.user, 'student_profile'):
            return StudentAttendance.objects.filter(student=self.request.user.student_profile)
        elif hasattr(self.request.user, 'parent_profile'):
            # Return attendance for all students of this parent
            student_ids = self.request.user.parent_profile.students.values_list('id', flat=True)
            return StudentAttendance.objects.filter(student_id__in=student_ids)
        else:
            return StudentAttendance.objects.none()

class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacherUser | IsAdminUser | IsHeadTeacherUser]
    serializer_class = StudentAttendanceSerializer
    queryset = StudentAttendance.objects.all()
    lookup_field = 'pk'

# Attendance Reports
class StudentAttendanceReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):
        """Generate attendance report for a specific student"""
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        academic_year_id = request.GET.get('academic_year')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get attendance records
            attendances = StudentAttendance.objects.filter(
                student_id=student_id,
                date__range=[start_date, end_date]
            )
            
            if academic_year_id:
                attendances = attendances.filter(academic_year_id=academic_year_id)
            
            # Calculate statistics
            total_days = attendances.count()
            present_days = attendances.filter(status__in=['present', 'late']).count()
            absent_days = attendances.filter(status='absent').count()
            late_days = attendances.filter(status='late').count()
            excused_days = attendances.filter(status__in=['excused', 'sick', 'emergency']).count()
            
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            # Monthly trend
            monthly_trend = attendances.extra(
                {'month': "EXTRACT(month FROM date)"}
            ).values('month').annotate(
                present_count=Count('id', filter=Q(status__in=['present', 'late'])),
                total_count=Count('id')
            ).order_by('month')
            
            statistics = {
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'late_days': late_days,
                'excused_days': excused_days,
                'attendance_percentage': round(attendance_percentage, 2),
                'average_daily_attendance': present_days,
                'trend_data': list(monthly_trend)
            }
            
            serializer = AttendanceStatisticsSerializer(statistics)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ClassAttendanceReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, class_id):
        """Generate attendance report for a specific class"""
        date = request.GET.get('date')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not date and not (start_date and end_date):
            return Response(
                {'error': 'Either date or start_date and end_date are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from academics.models import Class
            class_obj = Class.objects.get(id=class_id)
            
            if date:
                # Single day report
                attendances = StudentAttendance.objects.filter(
                    class_enrolled_id=class_id,
                    date=date
                )
                
                present_count = attendances.filter(status__in=['present', 'late']).count()
                absent_count = attendances.filter(status='absent').count()
                late_count = attendances.filter(status='late').count()
                total_students = attendances.count()
                
                attendance_percentage = (present_count / total_students * 100) if total_students > 0 else 0
                
                summary = {
                    'class_info': {
                        'id': class_obj.id,
                        'name': class_obj.name,
                        'class_teacher': class_obj.class_teacher.user.get_full_name() if class_obj.class_teacher else None
                    },
                    'total_students': total_students,
                    'present_count': present_count,
                    'absent_count': absent_count,
                    'late_count': late_count,
                    'attendance_percentage': round(attendance_percentage, 2),
                    'date': date
                }
                
            else:
                # Date range report
                attendances = StudentAttendance.objects.filter(
                    class_enrolled_id=class_id,
                    date__range=[start_date, end_date]
                )
                
                # More complex calculations for date range
                student_attendance_stats = attendances.values('student').annotate(
                    total_days=Count('id'),
                    present_days=Count('id', filter=Q(status__in=['present', 'late'])),
                    attendance_percentage=Count('id', filter=Q(status__in=['present', 'late'])) * 100.0 / Count('id')
                )
                
                summary = {
                    'class_info': {
                        'id': class_obj.id,
                        'name': class_obj.name
                    },
                    'period': f"{start_date} to {end_date}",
                    'total_students': student_attendance_stats.count(),
                    'average_attendance_percentage': student_attendance_stats.aggregate(
                        avg=Avg('attendance_percentage')
                    )['avg'] or 0,
                    'student_details': list(student_attendance_stats)
                }
            
            return Response(summary)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class DailyAttendanceReportView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsHeadTeacherUser]

    def get(self, request):
        """Generate daily attendance report for the whole school"""
        date = request.GET.get('date', timezone.now().date())
        
        try:
            # Get all classes
            from academics.models import Class
            classes = Class.objects.filter(is_active=True)
            
            report_data = []
            total_present = 0
            total_students = 0
            
            for class_obj in classes:
                attendances = StudentAttendance.objects.filter(
                    class_enrolled=class_obj,
                    date=date
                )
                
                present_count = attendances.filter(status__in=['present', 'late']).count()
                total_class_students = attendances.count()
                
                attendance_percentage = (present_count / total_class_students * 100) if total_class_students > 0 else 0
                
                report_data.append({
                    'class_name': class_obj.name,
                    'class_teacher': class_obj.class_teacher.user.get_full_name() if class_obj.class_teacher else 'Not Assigned',
                    'total_students': total_class_students,
                    'present_count': present_count,
                    'absent_count': total_class_students - present_count,
                    'attendance_percentage': round(attendance_percentage, 2)
                })
                
                total_present += present_count
                total_students += total_class_students
            
            overall_percentage = (total_present / total_students * 100) if total_students > 0 else 0
            
            return Response({
                'date': date,
                'overall_attendance': {
                    'total_students': total_students,
                    'total_present': total_present,
                    'total_absent': total_students - total_present,
                    'attendance_percentage': round(overall_percentage, 2)
                },
                'class_breakdown': report_data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class MonthlyAttendanceReportView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsHeadTeacherUser]

    def get(self, request):
        """Generate monthly attendance report"""
        year = request.GET.get('year', timezone.now().year)
        month = request.GET.get('month', timezone.now().month)
        
        try:
            start_date = datetime(int(year), int(month), 1).date()
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(int(year), int(month) + 1, 1).date() - timedelta(days=1)
            
            # Get attendance data
            attendances = StudentAttendance.objects.filter(
                date__range=[start_date, end_date]
            )
            
            # Calculate monthly statistics
            daily_attendance = attendances.values('date').annotate(
                present_count=Count('id', filter=Q(status__in=['present', 'late'])),
                total_count=Count('id')
            ).order_by('date')
            
            class_breakdown = attendances.values('class_enrolled__name').annotate(
                present_count=Count('id', filter=Q(status__in=['present', 'late'])),
                total_count=Count('id'),
                attendance_percentage=Count('id', filter=Q(status__in=['present', 'late'])) * 100.0 / Count('id')
            ).order_by('class_enrolled__name')
            
            return Response({
                'period': f"{year}-{month:02d}",
                'start_date': start_date,
                'end_date': end_date,
                'daily_attendance': list(daily_attendance),
                'class_breakdown': list(class_breakdown),
                'summary': {
                    'total_attendance_days': daily_attendance.count(),
                    'average_daily_attendance': daily_attendance.aggregate(
                        avg=Avg('present_count')
                    )['avg'] or 0
                }
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class TermAttendanceReportView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsHeadTeacherUser]

    def get(self, request):
        """Generate term-wise attendance report"""
        academic_year_id = request.GET.get('academic_year')
        term_id = request.GET.get('term')
        
        if not academic_year_id or not term_id:
            return Response(
                {'error': 'academic_year and term are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from academics.models import AcademicTerm
            term = AcademicTerm.objects.get(id=term_id)
            
            attendances = StudentAttendance.objects.filter(
                academic_year_id=academic_year_id,
                term_id=term_id,
                date__range=[term.start_date, term.end_date]
            )
            
            # Student-wise breakdown
            student_stats = attendances.values(
                'student__user__first_name',
                'student__user__last_name',
                'student__admission_number',
                'class_enrolled__name'
            ).annotate(
                total_days=Count('id'),
                present_days=Count('id', filter=Q(status__in=['present', 'late'])),
                attendance_percentage=Count('id', filter=Q(status__in=['present', 'late'])) * 100.0 / Count('id')
            ).order_by('class_enrolled__name', 'student__user__first_name')
            
            # Class-wise summary
            class_summary = attendances.values('class_enrolled__name').annotate(
                total_students=Count('student', distinct=True),
                average_attendance=Avg(
                    Count('id', filter=Q(status__in=['present', 'late'])) * 100.0 / Count('id')
                )
            )
            
            return Response({
                'academic_year': term.academic_year.name,
                'term': term.get_name_display(),
                'period': f"{term.start_date} to {term.end_date}",
                'student_statistics': list(student_stats),
                'class_summary': list(class_summary),
                'overall_statistics': {
                    'total_attendance_records': attendances.count(),
                    'total_students': student_stats.count(),
                    'average_attendance_percentage': student_stats.aggregate(
                        avg=Avg('attendance_percentage')
                    )['avg'] or 0
                }
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

# Attendance Statistics
class StudentAttendanceStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):
        """Get attendance statistics for a specific student"""
        try:
            attendances = StudentAttendance.objects.filter(student_id=student_id)
            
            # Overall statistics
            total_days = attendances.count()
            present_days = attendances.filter(status__in=['present', 'late']).count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            # Current month statistics
            current_month_start = timezone.now().replace(day=1).date()
            current_month_attendances = attendances.filter(date__gte=current_month_start)
            current_month_total = current_month_attendances.count()
            current_month_present = current_month_attendances.filter(status__in=['present', 'late']).count()
            current_month_percentage = (current_month_present / current_month_total * 100) if current_month_total > 0 else 0
            
            # Recent attendance (last 10 records)
            recent_attendance = attendances.order_by('-date')[:10]
            
            stats = {
                'overall': {
                    'total_days': total_days,
                    'present_days': present_days,
                    'attendance_percentage': round(attendance_percentage, 2)
                },
                'current_month': {
                    'total_days': current_month_total,
                    'present_days': current_month_present,
                    'attendance_percentage': round(current_month_percentage, 2)
                },
                'recent_attendance': StudentAttendanceSerializer(recent_attendance, many=True).data
            }
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ClassAttendanceStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, class_id):
        """Get attendance statistics for a specific class"""
        try:
            attendances = StudentAttendance.objects.filter(class_enrolled_id=class_id)
            
            # Current date statistics
            today = timezone.now().date()
            today_attendance = attendances.filter(date=today)
            today_present = today_attendance.filter(status__in=['present', 'late']).count()
            today_total = today_attendance.count()
            
            # Current week statistics
            week_start = today - timedelta(days=today.weekday())
            week_attendance = attendances.filter(date__gte=week_start)
            week_stats = week_attendance.values('date').annotate(
                present_count=Count('id', filter=Q(status__in=['present', 'late'])),
                total_count=Count('id')
            ).order_by('date')
            
            # Monthly trend
            monthly_trend = attendances.extra(
                {'month': "EXTRACT(month FROM date)"}
            ).values('month').annotate(
                attendance_percentage=Count('id', filter=Q(status__in=['present', 'late'])) * 100.0 / Count('id')
            ).order_by('month')
            
            stats = {
                'today': {
                    'date': today,
                    'present_count': today_present,
                    'total_count': today_total,
                    'attendance_percentage': round((today_present / today_total * 100), 2) if today_total > 0 else 0
                },
                'current_week': list(week_stats),
                'monthly_trend': list(monthly_trend)
            }
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class SchoolAttendanceStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsHeadTeacherUser]

    def get(self, request):
        """Get overall school attendance statistics"""
        try:
            # Today's statistics
            today = timezone.now().date()
            today_attendance = StudentAttendance.objects.filter(date=today)
            today_present = today_attendance.filter(status__in=['present', 'late']).count()
            today_total = today_attendance.count()
            
            # Weekly statistics
            week_start = today - timedelta(days=today.weekday())
            week_attendance = StudentAttendance.objects.filter(date__gte=week_start)
            weekly_average = week_attendance.values('date').annotate(
                daily_percentage=Count('id', filter=Q(status__in=['present', 'late'])) * 100.0 / Count('id')
            ).aggregate(avg=Avg('daily_percentage'))['avg'] or 0
            
            # Monthly statistics
            month_start = today.replace(day=1)
            month_attendance = StudentAttendance.objects.filter(date__gte=month_start)
            monthly_average = month_attendance.values('date').annotate(
                daily_percentage=Count('id', filter=Q(status__in=['present', 'late'])) * 100.0 / Count('id')
            ).aggregate(avg=Avg('daily_percentage'))['avg'] or 0
            
            # Class-wise breakdown
            class_stats = StudentAttendance.objects.filter(date=today).values(
                'class_enrolled__name'
            ).annotate(
                present_count=Count('id', filter=Q(status__in=['present', 'late'])),
                total_count=Count('id'),
                percentage=Count('id', filter=Q(status__in=['present', 'late'])) * 100.0 / Count('id')
            ).order_by('class_enrolled__name')
            
            stats = {
                'date': today,
                'overall': {
                    'present_count': today_present,
                    'total_count': today_total,
                    'attendance_percentage': round((today_present / today_total * 100), 2) if today_total > 0 else 0
                },
                'averages': {
                    'weekly': round(weekly_average, 2),
                    'monthly': round(monthly_average, 2)
                },
                'class_breakdown': list(class_stats)
            }
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

# Teacher and Staff Attendance Views
class TeacherAttendanceListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsHeadTeacherUser]
    serializer_class = TeacherAttendanceSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['teacher', 'date', 'status']
    ordering_fields = ['date', 'teacher__user__first_name']
    ordering = ['-date']

    def get_queryset(self):
        return TeacherAttendance.objects.select_related('teacher__user', 'recorded_by').all()

class StaffAttendanceListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsHeadTeacherUser]
    serializer_class = StaffAttendanceSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['staff_member', 'date', 'status', 'staff_category']
    ordering_fields = ['date', 'staff_member__first_name']
    ordering = ['-date']

    def get_queryset(self):
        return StaffAttendance.objects.select_related('staff_member', 'recorded_by').all()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_calendar(request):
    """Get attendance data for calendar view"""
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if not start_date or not end_date:
        return Response(
            {'error': 'start and end dates are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get student attendance for the period
        if request.user.role in ['admin', 'head_teacher', 'teacher']:
            attendances = StudentAttendance.objects.filter(
                date__range=[start_date, end_date]
            ).select_related('student__user', 'class_enrolled')
        elif hasattr(request.user, 'student_profile'):
            attendances = StudentAttendance.objects.filter(
                student=request.user.student_profile,
                date__range=[start_date, end_date]
            )
        else:
            attendances = StudentAttendance.objects.none()
        
        calendar_events = []
        for attendance in attendances:
            color_map = {
                'present': '#10B981',  # Green
                'absent': '#EF4444',   # Red
                'late': '#F59E0B',     # Yellow
                'excused': '#6B7280',  # Gray
                'sick': '#8B5CF6',     # Purple
                'emergency': '#DC2626' # Dark red
            }
            
            calendar_events.append({
                'id': str(attendance.id),
                'title': f"{attendance.student.user.get_full_name()} - {attendance.status.upper()}",
                'start': attendance.date.isoformat(),
                'color': color_map.get(attendance.status, '#6B7280'),
                'extendedProps': {
                    'type': 'attendance',
                    'status': attendance.status,
                    'class': attendance.class_enrolled.name,
                    'student': attendance.student.user.get_full_name()
                }
            })
        
        return Response(calendar_events)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )