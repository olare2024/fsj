import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from .models import TeacherProfile, TeacherDocument, TeacherAttendance

logger = logging.getLogger(__name__)


def get_teacher_summary(teacher_id):
    """Get comprehensive teacher summary"""
    try:
        teacher = TeacherProfile.objects.get(id=teacher_id)
        
        # Get attendance summary for current month
        today = timezone.now().date()
        first_day = today.replace(day=1)
        
        monthly_attendance = TeacherAttendance.objects.filter(
            teacher=teacher,
            date__gte=first_day,
            date__lte=today
        )
        
        present_days = monthly_attendance.filter(status='present').count()
        absent_days = monthly_attendance.filter(status='absent').count()
        leave_days = monthly_attendance.filter(status='leave').count()
        
        # Get current assignments
        current_year = timezone.now().year
        current_assignments = teacher.assignments.filter(
            is_active=True,
            academic_year__year=current_year
        )
        
        # Get upcoming leaves
        upcoming_leaves = teacher.leave_applications.filter(
            status='approved',
            start_date__gte=today
        )[:5]
        
        # Get recent trainings
        recent_trainings = teacher.trainings.filter(
            status='completed'
        ).order_by('-end_date')[:5]
        
        # Get document status
        documents = teacher.documents.filter(is_active=True)
        verified_docs = documents.filter(status='verified').count()
        pending_docs = documents.filter(status='pending').count()
        expiring_docs = documents.filter(
            expiry_date__range=[today, today + timedelta(days=30)]
        ).count()
        
        return {
            'teacher': {
                'id': teacher.id,
                'name': teacher.full_name,
                'tsc_number': teacher.tsc_number,
                'department': str(teacher.department) if teacher.department else None,
                'designation': teacher.get_designation_display(),
                'teaching_level': teacher.get_teaching_level_display(),
                'tsc_compliant': teacher.tsc_compliant,
                'cbc_trained': teacher.cbc_trained,
                'tpd_status': {
                    'current_module': teacher.tpd_current_module,
                    'last_completed': teacher.tpd_last_completed_date,
                    'next_renewal': teacher.tpd_next_renewal_date,
                    'is_valid': teacher.tpd_next_renewal_date and teacher.tpd_next_renewal_date >= today
                }
            },
            'attendance': {
                'month': today.strftime('%B %Y'),
                'present_days': present_days,
                'absent_days': absent_days,
                'leave_days': leave_days,
                'working_days': today.day,
                'attendance_rate': (present_days / today.day * 100) if today.day > 0 else 0
            },
            'workload': teacher.calculate_workload(),
            'assignments': {
                'total': current_assignments.count(),
                'subjects': current_assignments.values('subject').distinct().count(),
                'classes': current_assignments.values('class_assigned').distinct().count(),
                'weekly_periods': sum(a.weekly_periods for a in current_assignments),
                'details': list(current_assignments.values(
                    'title', 'weekly_periods', 'subject__name', 'class_assigned__name'
                ))
            },
            'documents': {
                'total': documents.count(),
                'verified': verified_docs,
                'pending': pending_docs,
                'expiring': expiring_docs,
                'completion_rate': (verified_docs / documents.count() * 100) if documents.count() > 0 else 0
            },
            'leaves': {
                'upcoming': list(upcoming_leaves.values(
                    'leave_type', 'start_date', 'end_date', 'days_requested'
                )),
                'remaining_annual': 21 - teacher.leave_applications.filter(
                    leave_type='annual',
                    status='approved'
                ).count()
            },
            'professional_development': {
                'recent_trainings': list(recent_trainings.values(
                    'title', 'organizer', 'end_date', 'training_type'
                )),
                'tpd_module': teacher.tpd_current_module,
                'next_renewal': teacher.tpd_next_renewal_date
            },
            'performance': {
                'rating': teacher.performance_rating,
                'last_appraisal': teacher.last_appraisal_date,
                'next_appraisal': teacher.next_appraisal_date,
                'appraisal_score': teacher.appraisal_score
            }
        }
    except TeacherProfile.DoesNotExist:
        logger.error(f"Teacher with id {teacher_id} does not exist")
        return None


def calculate_teacher_workload(teacher_id):
    """Calculate teacher's total workload"""
    try:
        teacher = TeacherProfile.objects.get(id=teacher_id)
        return teacher.calculate_workload()
    except TeacherProfile.DoesNotExist:
        return None


def generate_tsc_compliance_report():
    """Generate TSC compliance report for all teachers"""
    teachers = TeacherProfile.objects.filter(is_active=True)
    
    report = {
        'total_teachers': teachers.count(),
        'compliant_teachers': teachers.filter(tsc_compliant=True).count(),
        'non_compliant_teachers': teachers.filter(tsc_compliant=False).count(),
        'compliance_rate': 0,
        'details': []
    }
    
    if teachers.count() > 0:
        report['compliance_rate'] = (report['compliant_teachers'] / teachers.count() * 100)
    
    for teacher in teachers:
        report['details'].append({
            'teacher_id': teacher.id,
            'teacher_name': teacher.full_name,
            'tsc_number': teacher.tsc_number,
            'department': str(teacher.department) if teacher.department else '',
            'tsc_compliant': teacher.tsc_compliant,
            'tsc_status': teacher.get_tsc_status_display(),
            'cbc_trained': teacher.cbc_trained,
            'tpd_module': teacher.tpd_current_module,
            'tpd_renewal_date': teacher.tpd_next_renewal_date,
            'missing_requirements': _get_missing_requirements(teacher)
        })
    
    return report


def _get_missing_requirements(teacher):
    """Get missing TSC requirements for a teacher"""
    missing = []
    
    if not teacher.tsc_number:
        missing.append('TSC Number')
    
    if teacher.tsc_status not in ['registered', 'provisional']:
        missing.append(f'Valid TSC Status (current: {teacher.get_tsc_status_display()})')
    
    if not teacher.highest_qualification:
        missing.append('Highest Qualification')
    
    if not teacher.kcse_mean_grade:
        missing.append('KCSE Mean Grade')
    
    if teacher.teaching_level == 'junior_secondary' and not teacher.cbc_trained:
        missing.append('CBC Training')
    
    if teacher.tpd_next_renewal_date and teacher.tpd_next_renewal_date < timezone.now().date():
        missing.append('Valid TPD License')
    
    # Check required documents
    required_docs = ['tsc_certificate', 'good_conduct', 'academic_certificate']
    for doc_type in required_docs:
        if not teacher.documents.filter(
            document_type=doc_type,
            status='verified',
            is_active=True
        ).exists():
            missing.append(f'{doc_type.replace("_", " ").title()}')
    
    return missing


def export_attendance_report(start_date, end_date, department_id=None):
    """Export attendance report for the given period"""
    attendance_records = TeacherAttendance.objects.filter(
        date__range=[start_date, end_date],
        is_active=True
    )
    
    if department_id:
        attendance_records = attendance_records.filter(
            teacher__department_id=department_id
        )
    
    # Group by teacher
    report = {}
    for record in attendance_records:
        teacher_id = record.teacher.id
        
        if teacher_id not in report:
            report[teacher_id] = {
                'teacher_name': record.teacher.full_name,
                'tsc_number': record.teacher.tsc_number,
                'department': str(record.teacher.department) if record.teacher.department else '',
                'attendance_days': {},
                'summary': {
                    'present': 0,
                    'absent': 0,
                    'leave': 0,
                    'late': 0,
                    'total_days': 0
                }
            }
        
        # Update day record
        report[teacher_id]['attendance_days'][record.date] = {
            'status': record.get_status_display(),
            'check_in': record.check_in_time,
            'check_out': record.check_out_time,
            'working_hours': float(record.working_hours),
            'is_late': record.is_late,
            'is_full_day': record.is_full_day
        }
        
        # Update summary
        report[teacher_id]['summary']['total_days'] += 1
        
        if record.status == 'present':
            report[teacher_id]['summary']['present'] += 1
            if record.is_late:
                report[teacher_id]['summary']['late'] += 1
        elif record.status == 'absent':
            report[teacher_id]['summary']['absent'] += 1
        elif record.status == 'leave':
            report[teacher_id]['summary']['leave'] += 1
    
    # Calculate rates
    for teacher_id, data in report.items():
        total = data['summary']['total_days']
        present = data['summary']['present']
        
        if total > 0:
            data['summary']['attendance_rate'] = (present / total * 100)
            data['summary']['punctuality_rate'] = (
                (present - data['summary']['late']) / present * 100
            ) if present > 0 else 0
    
    return list(report.values())