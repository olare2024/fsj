# grading/views.py - FIXED VERSION
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.db.models import Q, Count, Avg, Max, Min, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import pandas as pd
import json
from datetime import datetime
import logging

from .models import (
    GradingScale, GradingPeriod, AssessmentType, Assessment,
    StudentGrade, SubjectGrade, ReportCard, Gradebook
)
from .serializers import (
    GradingScaleSerializer, GradingPeriodSerializer, AssessmentTypeSerializer,
    AssessmentSerializer, StudentGradeSerializer, BulkStudentGradeSerializer,
    SubjectGradeSerializer, ReportCardSerializer, GradebookSerializer,
    GradeStatisticsSerializer, PerformanceTrendSerializer
)
# Import User instead of Student
from accounts.models import User
from academics.models import Subject, Class
from .permissions import (
    IsTeacher, IsPrincipal, IsAdminOrTeacher,
    IsAdminOrPrincipal, IsStudentOwner, IsParentOrStudent
)

logger = logging.getLogger(__name__)

# Helper function to get students
def get_student_queryset():
    """Get all student users"""
    return User.objects.filter(role=User.Role.STUDENT, is_active=True)

# ==================== GRADING SCALE VIEWS ====================
class GradingScaleViewSet(viewsets.ModelViewSet):
    queryset = GradingScale.objects.filter(is_active=True)
    serializer_class = GradingScaleSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPrincipal]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'grade', 'remark']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['GET'])
    def calculate_grade(self, request):
        """Calculate grade based on percentage"""
        percentage = request.query_params.get('percentage')
        if not percentage:
            return Response({'error': 'Percentage is required'}, status=400)
        
        try:
            percentage = float(percentage)
        except ValueError:
            return Response({'error': 'Invalid percentage'}, status=400)
        
        grading_scale = GradingScale.objects.filter(
            is_active=True,
            min_score__lte=percentage,
            max_score__gte=percentage
        ).first()
        
        if grading_scale:
            serializer = self.get_serializer(grading_scale)
            return Response(serializer.data)
        return Response({'error': 'No matching grading scale found'}, status=404)

# ==================== GRADING PERIOD VIEWS ====================
class GradingPeriodViewSet(viewsets.ModelViewSet):
    queryset = GradingPeriod.objects.all()
    serializer_class = GradingPeriodSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPrincipal]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['term', 'academic_year', 'is_active', 'is_finalized']
    search_fields = ['name', 'academic_year']
    
    @action(detail=False, methods=['GET'])
    def current(self, request):
        """Get current grading period"""
        today = datetime.now().date()
        current_period = GradingPeriod.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_active=True
        ).first()
        
        if current_period:
            serializer = self.get_serializer(current_period)
            return Response(serializer.data)
        return Response({'detail': 'No current grading period'}, status=404)

# ==================== ASSESSMENT TYPE VIEWS ====================
class AssessmentTypeViewSet(viewsets.ModelViewSet):
    queryset = AssessmentType.objects.filter(is_active=True)
    serializer_class = AssessmentTypeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code', 'description']

# ==================== ASSESSMENT VIEWS ====================
class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['subject', 'class_level', 'grading_period', 'is_published']
    search_fields = ['name', 'subject__name', 'class_level__name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by teacher's subjects if not admin
        if not self.request.user.is_staff and self.request.user.role == 'teacher':
            teacher_subjects = Subject.objects.filter(teacher=self.request.user)
            queryset = queryset.filter(subject__in=teacher_subjects)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['POST'])
    def publish(self, request, pk=None):
        """Publish an assessment"""
        assessment = self.get_object()
        
        if assessment.is_published:
            return Response({'detail': 'Assessment already published'}, status=400)
        
        assessment.is_published = True
        assessment.published_at = datetime.now()
        assessment.save()
        
        serializer = self.get_serializer(assessment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def grades(self, request, pk=None):
        """Get all grades for this assessment"""
        assessment = self.get_object()
        student_grades = StudentGrade.objects.filter(assessment=assessment)
        serializer = StudentGradeSerializer(student_grades, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'], parser_classes=[MultiPartParser])
    def import_grades(self, request, pk=None):
        """Import grades from CSV/Excel file"""
        assessment = self.get_object()
        
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=400)
        
        file = request.FILES['file']
        
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                df = pd.read_excel(file)
            else:
                return Response({'error': 'Unsupported file format'}, status=400)
            
            required_columns = ['student_id', 'marks_obtained']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response({'error': f'Missing columns: {missing_columns}'}, status=400)
            
            imported_count = 0
            errors = []
            
            with transaction.atomic():
                for _, row in df.iterrows():
                    try:
                        # Use User model instead of Student
                        student = User.objects.get(id=row['student_id'])
                        
                        # Check if user is a student
                        if student.role != User.Role.STUDENT:
                            errors.append(f"User {student.admission_number} is not a student")
                            continue
                        
                        # Check if student is in the class level
                        if not assessment.class_level.students.filter(id=student.id).exists():
                            errors.append(f"Student {student.admission_number} not in class")
                            continue
                        
                        student_grade, created = StudentGrade.objects.update_or_create(
                            student=student,
                            assessment=assessment,
                            defaults={
                                'marks_obtained': float(row['marks_obtained']),
                                'graded_by': request.user,
                                'graded_at': datetime.now(),
                                'is_absent': row.get('is_absent', False),
                                'is_exempted': row.get('is_exempted', False),
                                'comments': row.get('comments', '')
                            }
                        )
                        imported_count += 1
                    except User.DoesNotExist:
                        errors.append(f"Student with ID {row['student_id']} not found")
                    except Exception as e:
                        errors.append(f"Error importing grade for student {row.get('student_id', 'Unknown')}: {str(e)}")
            
            response_data = {
                'imported_count': imported_count,
                'error_count': len(errors),
                'errors': errors[:10]  # Limit errors in response
            }
            
            if errors:
                return Response(response_data, status=207)  # Multi-status
            return Response(response_data)
            
        except Exception as e:
            return Response({'error': f'Error processing file: {str(e)}'}, status=400)
    
    @action(detail=True, methods=['GET'])
    def export_grades(self, request, pk=None):
        """Export grades to CSV"""
        assessment = self.get_object()
        student_grades = StudentGrade.objects.filter(assessment=assessment)
        
        # Create DataFrame
        data = []
        for grade in student_grades:
            data.append({
                'student_id': grade.student.id,
                'admission_number': grade.student.admission_number,
                'student_name': grade.student.get_full_name(),
                'marks_obtained': grade.marks_obtained,
                'percentage': grade.percentage,
                'grade': grade.grade,
                'is_absent': grade.is_absent,
                'is_exempted': grade.is_exempted,
                'comments': grade.comments
            })
        
        df = pd.DataFrame(data)
        
        # Create HTTP response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="grades_{assessment.name}_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        df.to_csv(response, index=False)
        return response

# ==================== STUDENT GRADE VIEWS ====================
class StudentGradeViewSet(viewsets.ModelViewSet):
    queryset = StudentGrade.objects.all()
    serializer_class = StudentGradeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher | IsStudentOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['student', 'assessment', 'grade', 'is_absent', 'is_exempted']
    search_fields = ['student__admission_number', 'student__first_name', 'student__last_name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by teacher's assessments if teacher
        if self.request.user.role == 'teacher':
            teacher_assessments = Assessment.objects.filter(created_by=self.request.user)
            queryset = queryset.filter(assessment__in=teacher_assessments)
        
        # Filter by student if student
        elif self.request.user.role == 'student':
            queryset = queryset.filter(student=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(graded_by=self.request.user, graded_at=datetime.now())
    
    @action(detail=False, methods=['POST'])
    def bulk_create(self, request):
        """Bulk create/update student grades"""
        serializer = BulkStudentGradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        assessment = data['assessment']
        grades_data = data['grades']
        
        created_count = 0
        updated_count = 0
        errors = []
        
        with transaction.atomic():
            for grade_data in grades_data:
                try:
                    # Use User model instead of Student
                    student = User.objects.get(id=grade_data['student_id'])
                    
                    # Check if user is a student
                    if student.role != User.Role.STUDENT:
                        errors.append(f"User {student.admission_number} is not a student")
                        continue
                    
                    # Check if student is in the class level
                    if not assessment.class_level.students.filter(id=student.id).exists():
                        errors.append(f"Student {student.admission_number} not in class")
                        continue
                    
                    marks_obtained = float(grade_data['marks_obtained'])
                    
                    student_grade, created = StudentGrade.objects.update_or_create(
                        student=student,
                        assessment=assessment,
                        defaults={
                            'marks_obtained': marks_obtained,
                            'graded_by': request.user,
                            'graded_at': datetime.now(),
                            'is_absent': grade_data.get('is_absent', 'false').lower() == 'true',
                            'is_exempted': grade_data.get('is_exempted', 'false').lower() == 'true',
                            'comments': grade_data.get('comments', '')
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                        
                except User.DoesNotExist:
                    errors.append(f"Student with ID {grade_data['student_id']} not found")
                except Exception as e:
                    errors.append(f"Error processing grade for student {grade_data.get('student_id', 'Unknown')}: {str(e)}")
        
        response_data = {
            'created_count': created_count,
            'updated_count': updated_count,
            'error_count': len(errors),
            'errors': errors[:10]
        }
        
        if errors:
            return Response(response_data, status=207)
        return Response(response_data, status=201)

# ==================== SUBJECT GRADE VIEWS ====================
class SubjectGradeViewSet(viewsets.ModelViewSet):
    queryset = SubjectGrade.objects.all()
    serializer_class = SubjectGradeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher | IsStudentOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['student', 'subject', 'class_level', 'grading_period', 'is_finalized']
    search_fields = ['student__admission_number', 'subject__name', 'grade']
    
    @action(detail=True, methods=['POST'])
    def finalize(self, request, pk=None):
        """Finalize subject grade"""
        subject_grade = self.get_object()
        
        if subject_grade.is_finalized:
            return Response({'detail': 'Grade already finalized'}, status=400)
        
        # Calculate overall grade
        subject_grade.calculate_overall_grade()
        subject_grade.is_finalized = True
        subject_grade.finalized_by = request.user
        subject_grade.finalized_at = datetime.now()
        subject_grade.save()
        
        serializer = self.get_serializer(subject_grade)
        return Response(serializer.data)
    
    @action(detail=False, methods=['POST'])
    def calculate_all(self, request):
        """Calculate grades for all students in a subject and grading period"""
        subject_id = request.data.get('subject_id')
        grading_period_id = request.data.get('grading_period_id')
        
        if not subject_id or not grading_period_id:
            return Response({'error': 'subject_id and grading_period_id are required'}, status=400)
        
        try:
            subject = Subject.objects.get(id=subject_id)
            grading_period = GradingPeriod.objects.get(id=grading_period_id)
        except (Subject.DoesNotExist, GradingPeriod.DoesNotExist):
            return Response({'error': 'Subject or Grading Period not found'}, status=404)
        
        # Get all class levels for this subject
        class_levels = Class.objects.filter(subjects=subject)
        
        calculated_count = 0
        
        with transaction.atomic():
            for class_level in class_levels:
                # Get all students in this class level
                students = User.objects.filter(
                    role=User.Role.STUDENT,
                    current_class=class_level.name,
                    is_active=True
                )
                
                for student in students:
                    # Get or create subject grade
                    subject_grade, created = SubjectGrade.objects.get_or_create(
                        student=student,
                        subject=subject,
                        class_level=class_level,
                        grading_period=grading_period
                    )
                    
                    # Calculate overall grade
                    subject_grade.calculate_overall_grade()
                    subject_grade.save()
                    calculated_count += 1
        
        return Response({
            'message': f'Calculated grades for {calculated_count} students',
            'calculated_count': calculated_count
        })

# ==================== REPORT CARD VIEWS ====================
class ReportCardViewSet(viewsets.ModelViewSet):
    queryset = ReportCard.objects.all()
    serializer_class = ReportCardSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPrincipal | IsParentOrStudent]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['student', 'grading_period', 'class_level', 'status']
    search_fields = ['student__admission_number', 'student__first_name', 'student__last_name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by student if student
        if self.request.user.role == 'student':
            queryset = queryset.filter(student=self.request.user)
        
        # Filter by parent's children if parent
        elif self.request.user.role == 'parent':
            children = self.request.user.parent.children.all()
            queryset = queryset.filter(student__in=children)
        
        return queryset
    
    @action(detail=True, methods=['POST'])
    def publish(self, request, pk=None):
        """Publish a report card"""
        report_card = self.get_object()
        
        if report_card.status == 'published':
            return Response({'detail': 'Report card already published'}, status=400)
        
        # Calculate overall performance
        report_card.calculate_overall()
        
        # Update attendance data (you'll need to integrate with attendance app)
        # This is a placeholder - implement based on your attendance system
        report_card.attendance_days = 100
        report_card.days_present = 90
        report_card.attendance_percentage = 90
        
        report_card.status = 'published'
        report_card.published_by = request.user
        report_card.published_at = datetime.now()
        report_card.save()
        
        serializer = self.get_serializer(report_card)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def add_comment(self, request, pk=None):
        """Add comment to report card"""
        report_card = self.get_object()
        comment_type = request.data.get('type')  # teacher, principal, parent
        comment = request.data.get('comment')
        
        if not comment_type or not comment:
            return Response({'error': 'type and comment are required'}, status=400)
        
        if comment_type == 'teacher' and request.user.role in ['teacher', 'admin']:
            report_card.teacher_comments = comment
        elif comment_type == 'principal' and request.user.role in ['principal', 'admin']:
            report_card.principal_comments = comment
        elif comment_type == 'parent' and request.user.role == 'parent':
            report_card.parent_comments = comment
        else:
            return Response({'error': 'Unauthorized to add this type of comment'}, status=403)
        
        report_card.save()
        serializer = self.get_serializer(report_card)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def download(self, request, pk=None):
        """Download report card as PDF"""
        # This would generate a PDF report
        # For now, return JSON with a message
        return Response({'message': 'PDF download endpoint - implement PDF generation'})

# ==================== GRADEBOOK VIEWS ====================
class GradebookViewSet(viewsets.ModelViewSet):
    queryset = Gradebook.objects.all()
    serializer_class = GradebookSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['teacher', 'subject', 'class_level', 'grading_period', 'is_published']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by teacher if not admin
        if not self.request.user.is_staff and self.request.user.role == 'teacher':
            queryset = queryset.filter(teacher=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['GET'])
    def overview(self, request, pk=None):
        """Get gradebook overview with statistics"""
        gradebook = self.get_object()
        
        # Get all assessments
        assessments = Assessment.objects.filter(
            subject=gradebook.subject,
            class_level=gradebook.class_level,
            grading_period=gradebook.grading_period
        )
        
        # Get all students in the class
        students = User.objects.filter(
            role=User.Role.STUDENT,
            current_class=gradebook.class_level.name,
            is_active=True
        )
        
        # Prepare data
        data = {
            'gradebook': GradebookSerializer(gradebook).data,
            'total_students': students.count(),
            'total_assessments': assessments.count(),
            'assessments': AssessmentSerializer(assessments, many=True).data,
            'students': []
        }
        
        # Add student performance data
        for student in students:
            student_data = {
                'id': student.id,
                'admission_number': student.admission_number,
                'name': student.get_full_name(),
                'grades': [],
                'average_percentage': 0
            }
            
            total_percentage = 0
            grade_count = 0
            
            for assessment in assessments:
                try:
                    grade = StudentGrade.objects.get(student=student, assessment=assessment)
                    student_data['grades'].append({
                        'assessment': assessment.name,
                        'marks': f"{grade.marks_obtained}/{assessment.total_marks}",
                        'percentage': float(grade.percentage) if grade.percentage else None,
                        'grade': grade.grade
                    })
                    
                    if grade.percentage:
                        total_percentage += float(grade.percentage)
                        grade_count += 1
                except StudentGrade.DoesNotExist:
                    student_data['grades'].append({
                        'assessment': assessment.name,
                        'marks': 'Not graded',
                        'percentage': None,
                        'grade': None
                    })
            
            if grade_count > 0:
                student_data['average_percentage'] = total_percentage / grade_count
            
            data['students'].append(student_data)
        
        return Response(data)

# ==================== STATISTICS & ANALYTICS VIEWS ====================
class GradeStatisticsView(generics.GenericAPIView):
    """View for grade statistics and analytics"""
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    
    def get(self, request):
        """Get overall grade statistics"""
        subject_id = request.query_params.get('subject_id')
        class_level_id = request.query_params.get('class_level_id')
        grading_period_id = request.query_params.get('grading_period_id')
        
        # Build filters
        filters = {}
        if subject_id:
            filters['subject_id'] = subject_id
        if class_level_id:
            filters['class_level_id'] = class_level_id
        if grading_period_id:
            filters['grading_period_id'] = grading_period_id
        
        # Get subject grades
        subject_grades = SubjectGrade.objects.filter(**filters, is_finalized=True)
        
        if not subject_grades.exists():
            return Response({'error': 'No finalized grades found'}, status=404)
        
        # Calculate statistics
        total_students = subject_grades.values('student').distinct().count()
        total_subjects = subject_grades.count()
        
        # Average percentage
        avg_percentage = subject_grades.aggregate(avg=Avg('percentage'))['avg'] or 0
        
        # Highest and lowest percentages
        highest = subject_grades.aggregate(max=Max('percentage'))['max'] or 0
        lowest = subject_grades.aggregate(min=Min('percentage'))['min'] or 0
        
        # Grade distribution
        grade_distribution = subject_grades.values('grade').annotate(count=Count('id')).order_by('grade')
        grade_dist = {item['grade']: item['count'] for item in grade_distribution}
        
        # Pass rate (assuming passing grade is C and above)
        passing_grades = ['A', 'B', 'C']
        pass_count = subject_grades.filter(grade__in=passing_grades).count()
        pass_rate = (pass_count / total_subjects * 100) if total_subjects > 0 else 0
        
        # Prepare response
        statistics = {
            'total_students': total_students,
            'total_assessments': total_subjects,
            'average_percentage': round(avg_percentage, 2),
            'highest_percentage': round(highest, 2),
            'lowest_percentage': round(lowest, 2),
            'grade_distribution': grade_dist,
            'pass_rate': round(pass_rate, 2)
        }
        
        serializer = GradeStatisticsSerializer(statistics)
        return Response(serializer.data)

class PerformanceTrendView(generics.GenericAPIView):
    """View for performance trends over time"""
    permission_classes = [IsAuthenticated, IsAdminOrPrincipal]
    
    def get(self, request):
        """Get performance trends"""
        student_id = request.query_params.get('student_id')
        subject_id = request.query_params.get('subject_id')
        class_level_id = request.query_params.get('class_level_id')
        
        filters = {}
        if student_id:
            filters['student_id'] = student_id
        if subject_id:
            filters['subject_id'] = subject_id
        if class_level_id:
            filters['class_level_id'] = class_level_id
        
        # Get all grading periods
        grading_periods = GradingPeriod.objects.filter(is_finalized=True).order_by('end_date')
        
        trends = []
        
        for period in grading_periods:
            period_filters = filters.copy()
            period_filters['grading_period'] = period
            
            subject_grades = SubjectGrade.objects.filter(**period_filters, is_finalized=True)
            
            if subject_grades.exists():
                avg_percentage = subject_grades.aggregate(avg=Avg('percentage'))['avg'] or 0
                student_count = subject_grades.values('student').distinct().count()
                
                # Find top performer
                top_performer_grade = subject_grades.order_by('-percentage').first()
                top_performer = top_performer_grade.student.get_full_name() if top_performer_grade else "N/A"
                top_percentage = top_performer_grade.percentage if top_performer_grade else 0
                
                trends.append({
                    'grading_period': period.name,
                    'average_percentage': round(avg_percentage, 2),
                    'student_count': student_count,
                    'top_performer': top_performer,
                    'top_percentage': round(top_percentage, 2)
                })
        
        serializer = PerformanceTrendSerializer(trends, many=True)
        return Response(serializer.data)

# ==================== DASHBOARD VIEWS ====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def grading_dashboard(request):
    """Dashboard overview for grading"""
    user = request.user
    
    if user.role == 'teacher':
        # Teacher dashboard
        gradebooks = Gradebook.objects.filter(teacher=user, is_published=False)
        pending_assessments = Assessment.objects.filter(created_by=user, is_published=False)
        recent_grades = StudentGrade.objects.filter(graded_by=user).order_by('-graded_at')[:10]
        
        data = {
            'gradebook_count': gradebooks.count(),
            'pending_assessments': pending_assessments.count(),
            'recent_grades': StudentGradeSerializer(recent_grades, many=True).data
        }
        
    elif user.role == 'student':
        # Student dashboard
        recent_grades = StudentGrade.objects.filter(student=user).order_by('-graded_at')[:10]
        report_cards = ReportCard.objects.filter(student=user, status='published').order_by('-published_at')[:5]
        
        data = {
            'recent_grades': StudentGradeSerializer(recent_grades, many=True).data,
            'report_cards': ReportCardSerializer(report_cards, many=True).data
        }
    
    elif user.role == 'parent':
        # Parent dashboard
        children = user.parent.children.all()
        recent_report_cards = ReportCard.objects.filter(student__in=children, status='published').order_by('-published_at')[:5]
        
        data = {
            'children_count': children.count(),
            'recent_report_cards': ReportCardSerializer(recent_report_cards, many=True).data
        }
    
    else:  # Admin/Principal
        # Admin dashboard
        total_students = User.objects.filter(role=User.Role.STUDENT, is_active=True).count()
        total_assessments = Assessment.objects.count()
        total_report_cards = ReportCard.objects.count()
        
        data = {
            'total_students': total_students,
            'total_assessments': total_assessments,
            'total_report_cards': total_report_cards,
            'grading_periods': GradingPeriodSerializer(GradingPeriod.objects.filter(is_active=True), many=True).data
        }
    
    return Response(data)