from django.http import JsonResponse
from django.core.management import call_command
from django.db.models import Q
from io import StringIO
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Period, Curriculum, GradeLevel, Timetable, BreakTime, CurriculumSubjectMapping
from .serializers import (
    PeriodSerializer, CurriculumSerializer, GradeLevelSerializer,
    TimetableSerializer, TimetableDetailSerializer, BreakTimeSerializer,
    CurriculumSubjectMappingSerializer, CurriculumTimetableSerializer,
    BulkPeriodCreateSerializer
)
from academic.models import AllocatedSubject


class CurriculumViewSet(viewsets.ModelViewSet):
    queryset = Curriculum.objects.filter(is_active=True)
    serializer_class = CurriculumSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def grade_levels(self, request, pk=None):
        """Get all grade levels for a specific curriculum"""
        curriculum = self.get_object()
        grade_levels = GradeLevel.objects.filter(curriculum=curriculum)
        serializer = GradeLevelSerializer(grade_levels, many=True)
        return Response(serializer.data)


class GradeLevelViewSet(viewsets.ModelViewSet):
    queryset = GradeLevel.objects.all()
    serializer_class = GradeLevelSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['curriculum', 'grade']


class CurriculumSubjectMappingViewSet(viewsets.ModelViewSet):
    queryset = CurriculumSubjectMapping.objects.all()
    serializer_class = CurriculumSubjectMappingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['curriculum', 'grade_level', 'is_core']


class PeriodCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Support both allocated_subject and direct curriculum assignment
        allocated_subject_id = request.data.get("allocated_subject")
        curriculum_id = request.data.get("curriculum_id")
        grade_level_id = request.data.get("grade_level_id")

        if allocated_subject_id:
            try:
                allocated_subject = AllocatedSubject.objects.get(id=allocated_subject_id)
            except AllocatedSubject.DoesNotExist:
                return Response(
                    {"error": "AllocatedSubject not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            serializer = PeriodSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(allocated_subject=allocated_subject)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Direct creation with curriculum and grade level
            serializer = PeriodSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.filter(is_active=True)
    serializer_class = PeriodSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['day_of_week', 'classroom', 'curriculum', 'grade_level', 'teacher']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by curriculum if provided
        curriculum = self.request.query_params.get('curriculum')
        if curriculum:
            queryset = queryset.filter(curriculum__name=curriculum)
        
        # Filter by grade level if provided
        grade_level = self.request.query_params.get('grade_level')
        if grade_level:
            queryset = queryset.filter(grade_level__grade=grade_level)
        
        return queryset

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create periods"""
        serializer = BulkPeriodCreateSerializer(data=request.data)
        if serializer.is_valid():
            periods_data = serializer.validated_data['periods_data']
            created_periods = []
            errors = []

            for period_data in periods_data:
                period_serializer = PeriodSerializer(data=period_data)
                if period_serializer.is_valid():
                    period = period_serializer.save()
                    created_periods.append(period_serializer.data)
                else:
                    errors.append({
                        'data': period_data,
                        'errors': period_serializer.errors
                    })

            response_data = {
                'created_count': len(created_periods),
                'created_periods': created_periods,
                'error_count': len(errors),
                'errors': errors
            }

            status_code = status.HTTP_201_CREATED if created_periods else status.HTTP_400_BAD_REQUEST
            return Response(response_data, status=status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_curriculum(self, request):
        """Get periods filtered by curriculum and grade level"""
        curriculum_name = request.query_params.get('curriculum')
        grade = request.query_params.get('grade')

        if not curriculum_name:
            return Response(
                {"error": "Curriculum parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset().filter(curriculum__name=curriculum_name)
        
        if grade:
            queryset = queryset.filter(grade_level__grade=grade)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['curriculum', 'grade_level', 'term', 'academic_year', 'is_active']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TimetableDetailSerializer
        return TimetableSerializer

    @action(detail=False, methods=['post'])
    def generate_curriculum_timetable(self, request):
        """Generate timetable for specific curriculum and grade level"""
        serializer = CurriculumTimetableSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            curriculum_name = data['curriculum']
            grade_level = data['grade_level']
            term = data['term']
            academic_year = data['academic_year']

            try:
                curriculum = Curriculum.objects.get(name=curriculum_name)
                grade_level_obj = GradeLevel.objects.get(
                    curriculum=curriculum, 
                    grade=grade_level
                )

                # Check if timetable already exists
                timetable, created = Timetable.objects.get_or_create(
                    curriculum=curriculum,
                    grade_level=grade_level_obj,
                    term=term,
                    academic_year=academic_year,
                    defaults={
                        'name': f"{curriculum.get_name_display()} - Grade {grade_level} - Term {term} {academic_year}"
                    }
                )

                if created:
                    message = "Timetable created successfully."
                else:
                    message = "Timetable already exists."

                return Response({
                    "message": message,
                    "timetable": TimetableSerializer(timetable).data
                }, status=status.HTTP_201_CREATED)

            except Curriculum.DoesNotExist:
                return Response(
                    {"error": f"Curriculum '{curriculum_name}' not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            except GradeLevel.DoesNotExist:
                return Response(
                    {"error": f"Grade level {grade_level} not found for curriculum '{curriculum_name}'."},
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a timetable (deactivate others for same curriculum/grade/term)"""
        timetable = self.get_object()
        
        # Deactivate other timetables for same curriculum, grade level, and term
        Timetable.objects.filter(
            curriculum=timetable.curriculum,
            grade_level=timetable.grade_level,
            term=timetable.term,
            academic_year=timetable.academic_year
        ).update(is_active=False)
        
        # Activate this timetable
        timetable.is_active = True
        timetable.save()
        
        return Response({
            "message": "Timetable activated successfully.",
            "timetable": TimetableSerializer(timetable).data
        })

    @action(detail=True, methods=['post'])
    def add_period(self, request, pk=None):
        """Add a period to timetable"""
        timetable = self.get_object()
        period_id = request.data.get('period_id')
        
        try:
            period = Period.objects.get(id=period_id)
            timetable.periods.add(period)
            return Response({
                "message": "Period added to timetable successfully."
            })
        except Period.DoesNotExist:
            return Response(
                {"error": "Period not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class BreakTimeViewSet(viewsets.ModelViewSet):
    queryset = BreakTime.objects.all()
    serializer_class = BreakTimeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['timetable', 'break_type']


class TimetableGeneratorView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        """
        Enhanced timetable generation with curriculum support
        """
        output = StringIO()
        try:
            # Get generation parameters
            curriculum = request.data.get('curriculum')
            grade_level = request.data.get('grade_level')
            term = request.data.get('term')
            academic_year = request.data.get('academic_year')

            command_args = []
            if curriculum:
                command_args.extend(['--curriculum', curriculum])
            if grade_level:
                command_args.extend(['--grade-level', str(grade_level)])
            if term:
                command_args.extend(['--term', str(term)])
            if academic_year:
                command_args.extend(['--academic-year', academic_year])

            call_command("generate_timetable", *command_args, stdout=output)
            
            return JsonResponse({
                "status": "success", 
                "message": output.getvalue(),
                "parameters": {
                    "curriculum": curriculum,
                    "grade_level": grade_level,
                    "term": term,
                    "academic_year": academic_year
                }
            })
        except Exception as e:
            return JsonResponse({
                "status": "error", 
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


def run_generate_timetable(request):
    """
    Legacy endpoint - redirects to new API view
    """
    view = TimetableGeneratorView()
    return view.post(request)