from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Curriculum, CBCStrand, CBCSubStrand, ICSESubject,
    AmericanStandard, AmericanCourse, CurriculumMapping,
    CurriculumImplementation, LearningObjective, ResourceLibrary,
    ProfessionalDevelopment
)
from .serializers import (
    CurriculumSerializer, CBCStrandSerializer, CBCSubStrandSerializer,
    ICSESubjectSerializer, AmericanStandardSerializer, AmericanCourseSerializer,
    CurriculumMappingSerializer, CurriculumImplementationSerializer,
    LearningObjectiveSerializer, ResourceLibrarySerializer,
    ProfessionalDevelopmentSerializer, CurriculumOverviewSerializer,
    CrossCurriculumAnalysisSerializer
)
from accounts.permissions import IsAdminUser, IsCurriculumCoordinatorUser, IsHeadTeacherUser

# Curriculum Management Views
class CurriculumListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CurriculumSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'full_name', 'description']
    ordering_fields = ['name', 'implementation_date']
    ordering = ['name']

    def get_queryset(self):
        return Curriculum.objects.select_related('coordinator').all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permission() for permission in [IsAdminUser | IsCurriculumCoordinatorUser]]
        return [permission() for permission in self.permission_classes]

class CurriculumDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsCurriculumCoordinatorUser]
    serializer_class = CurriculumSerializer
    queryset = Curriculum.objects.all()
    lookup_field = 'pk'

# CBC Curriculum Views
class CBCStrandListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CBCStrandSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['learning_area']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['learning_area', 'code']
    ordering = ['learning_area', 'code']

    def get_queryset(self):
        return CBCStrand.objects.select_related('curriculum').all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permission() for permission in [IsAdminUser | IsCurriculumCoordinatorUser]]
        return [permission() for permission in self.permission_classes]

class CBCStrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsCurriculumCoordinatorUser]
    serializer_class = CBCStrandSerializer
    queryset = CBCStrand.objects.all()
    lookup_field = 'pk'

class CBCSubStrandListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CBCSubStrandSerializer
    
    def get_queryset(self):
        strand_id = self.kwargs.get('strand_id')
        if strand_id:
            return CBCSubStrand.objects.filter(strand_id=strand_id).select_related('strand')
        return CBCSubStrand.objects.select_related('strand').all()

class CBCSubStrandByStrandView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, strand_id):
        sub_strands = CBCSubStrand.objects.filter(strand_id=strand_id).select_related('strand')
        serializer = CBCSubStrandSerializer(sub_strands, many=True)
        return Response(serializer.data)

# ICSE Curriculum Views
class ICSESubjectListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ICSESubjectSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['subject_group', 'is_compulsory', 'has_practical']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['subject_group', 'name']
    ordering = ['subject_group', 'name']

    def get_queryset(self):
        return ICSESubject.objects.select_related('curriculum').all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permission() for permission in [IsAdminUser | IsCurriculumCoordinatorUser]]
        return [permission() for permission in self.permission_classes]

class ICSESubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsCurriculumCoordinatorUser]
    serializer_class = ICSESubjectSerializer
    queryset = ICSESubject.objects.all()
    lookup_field = 'pk'

class ICSESyllabusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, subject_id):
        try:
            subject = ICSESubject.objects.get(id=subject_id)
            syllabus_data = {
                'subject': ICSESubjectSerializer(subject).data,
                'syllabus_content': subject.syllabus_content,
                'assessment_structure': {
                    'theory_marks': subject.theory_marks,
                    'practical_marks': subject.practical_marks,
                    'total_marks': subject.total_marks
                },
                'recommended_books': {
                    'prescribed': subject.prescribed_books,
                    'reference': subject.reference_books
                }
            }
            return Response(syllabus_data)
        except ICSESubject.DoesNotExist:
            return Response(
                {'error': 'ICSE Subject not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

# American Curriculum Views
class AmericanStandardListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AmericanStandardSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['domain', 'grade_level', 'complexity_level']
    search_fields = ['standard_code', 'description', 'cluster']
    ordering_fields = ['domain', 'grade_level', 'standard_code']
    ordering = ['domain', 'grade_level', 'standard_code']

    def get_queryset(self):
        return AmericanStandard.objects.select_related('curriculum').all()

class AmericanCourseListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AmericanCourseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course_type', 'credit_type', 'is_active']
    search_fields = ['name', 'course_code', 'description']
    ordering_fields = ['credit_type', 'course_type', 'name']
    ordering = ['credit_type', 'course_type', 'name']

    def get_queryset(self):
        return AmericanCourse.objects.select_related('curriculum').prefetch_related('prerequisites').all()

# Curriculum Mapping Views
class CurriculumMappingListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CurriculumMappingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['source_curriculum', 'target_curriculum', 'mapping_strength', 'is_verified']
    search_fields = ['source_component', 'target_component', 'source_identifier', 'target_identifier']
    ordering_fields = ['source_curriculum', 'target_curriculum']
    ordering = ['source_curriculum', 'target_curriculum']

    def get_queryset(self):
        return CurriculumMapping.objects.select_related(
            'source_curriculum', 'target_curriculum', 'verified_by'
        ).all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permission() for permission in [IsAdminUser | IsCurriculumCoordinatorUser]]
        return [permission() for permission in self.permission_classes]

class CurriculumMappingDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsCurriculumCoordinatorUser]
    serializer_class = CurriculumMappingSerializer
    queryset = CurriculumMapping.objects.all()
    lookup_field = 'pk'

# Curriculum Implementation Views
class CurriculumImplementationListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CurriculumImplementationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['curriculum', 'class_enrolled', 'academic_year', 'implementation_status', 'is_primary']
    search_fields = ['class_enrolled__name', 'curriculum__name']
    ordering_fields = ['academic_year', 'class_enrolled', 'implementation_date']
    ordering = ['-academic_year', 'class_enrolled']

    def get_queryset(self):
        return CurriculumImplementation.objects.select_related(
            'curriculum', 'class_enrolled', 'academic_year', 'lead_teacher__user', 'grading_system_used'
        ).prefetch_related('supporting_teachers__user').all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permission() for permission in [IsAdminUser | IsCurriculumCoordinatorUser | IsHeadTeacherUser]]
        return [permission() for permission in self.permission_classes]

class CurriculumImplementationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsCurriculumCoordinatorUser | IsHeadTeacherUser]
    serializer_class = CurriculumImplementationSerializer
    queryset = CurriculumImplementation.objects.all()
    lookup_field = 'pk'

# Learning Objectives Views
class LearningObjectiveListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LearningObjectiveSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['curriculum', 'subject', 'bloom_level']
    search_fields = ['code', 'description']
    ordering_fields = ['curriculum', 'code']
    ordering = ['curriculum', 'code']

    def get_queryset(self):
        return LearningObjective.objects.select_related('curriculum', 'subject').all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permission() for permission in [IsAdminUser | IsCurriculumCoordinatorUser]]
        return [permission() for permission in self.permission_classes]

# Resource Library Views
class ResourceLibraryListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ResourceLibrarySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['curriculum', 'resource_type', 'is_approved']
    search_fields = ['title', 'author', 'description', 'publisher']
    ordering_fields = ['curriculum', 'resource_type', 'title']
    ordering = ['curriculum', 'resource_type', 'title']

    def get_queryset(self):
        return ResourceLibrary.objects.select_related('curriculum', 'approved_by').all()

    def perform_create(self, serializer):
        serializer.save()

class ResourceLibraryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ResourceLibrarySerializer
    queryset = ResourceLibrary.objects.all()
    lookup_field = 'pk'

# Professional Development Views
class ProfessionalDevelopmentListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfessionalDevelopmentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['curriculum', 'development_type', 'is_completed']
    search_fields = ['title', 'description', 'facilitator']
    ordering_fields = ['start_date', 'title']
    ordering = ['-start_date']

    def get_queryset(self):
        return ProfessionalDevelopment.objects.select_related('curriculum').prefetch_related('target_teachers__user').all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permission() for permission in [IsAdminUser | IsCurriculumCoordinatorUser]]
        return [permission() for permission in self.permission_classes]

# Analysis and Reporting Views
class CurriculumOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total_curricula = Curriculum.objects.filter(is_active=True).count()
        active_implementations = CurriculumImplementation.objects.filter(
            implementation_status='in_progress'
        ).count()
        
        cbc_strands_count = CBCStrand.objects.count()
        icse_subjects_count = ICSESubject.objects.count()
        american_standards_count = AmericanStandard.objects.count()
        resource_count = ResourceLibrary.objects.filter(is_approved=True).count()
        
        recent_implementations = CurriculumImplementation.objects.select_related(
            'curriculum', 'class_enrolled', 'academic_year'
        ).order_by('-implementation_date')[:5]
        
        overview_data = {
            'total_curricula': total_curricula,
            'active_implementations': active_implementations,
            'cbc_strands_count': cbc_strands_count,
            'icse_subjects_count': icse_subjects_count,
            'american_standards_count': american_standards_count,
            'resource_count': resource_count,
            'recent_implementations': recent_implementations
        }
        
        serializer = CurriculumOverviewSerializer(overview_data)
        return Response(serializer.data)

class CrossCurriculumAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsCurriculumCoordinatorUser]

    def get(self, request):
        source_curriculum_id = request.GET.get('source_curriculum')
        target_curriculum_id = request.GET.get('target_curriculum')
        
        if not source_curriculum_id or not target_curriculum_id:
            return Response(
                {'error': 'Both source_curriculum and target_curriculum are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            source_curriculum = Curriculum.objects.get(id=source_curriculum_id)
            target_curriculum = Curriculum.objects.get(id=target_curriculum_id)
            
            mappings = CurriculumMapping.objects.filter(
                source_curriculum=source_curriculum,
                target_curriculum=target_curriculum
            )
            
            mapping_count = mappings.count()
            strong_mappings = mappings.filter(mapping_strength__in=['exact', 'close']).count()
            weak_mappings = mappings.filter(mapping_strength__in=['partial', 'supplementary']).count()
            
            # Calculate coverage percentage (this would be more sophisticated in reality)
            total_components = 100  # This would be calculated based on actual components
            coverage_percentage = (mapping_count / total_components * 100) if total_components > 0 else 0
            
            analysis_data = {
                'source_curriculum': source_curriculum,
                'target_curriculum': target_curriculum,
                'mapping_count': mapping_count,
                'coverage_percentage': round(coverage_percentage, 2),
                'strong_mappings': strong_mappings,
                'weak_mappings': weak_mappings
            }
            
            serializer = CrossCurriculumAnalysisSerializer(analysis_data)
            return Response(serializer.data)
            
        except Curriculum.DoesNotExist:
            return Response(
                {'error': 'One or both curricula not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def curriculum_resources_search(request):
    """Search resources across all curricula"""
    query = request.GET.get('q', '')
    curriculum_id = request.GET.get('curriculum')
    resource_type = request.GET.get('resource_type')
    grade_level = request.GET.get('grade_level')
    
    resources = ResourceLibrary.objects.filter(is_approved=True)
    
    if query:
        resources = resources.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(author__icontains=query) |
            Q(publisher__icontains=query)
        )
    
    if curriculum_id:
        resources = resources.filter(curriculum_id=curriculum_id)
    
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    
    if grade_level:
        resources = resources.filter(grade_levels__contains=[grade_level])
    
    serializer = ResourceLibrarySerializer(resources[:50], many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def teacher_curriculum_assignments(request, teacher_id):
    """Get curriculum assignments for a specific teacher"""
    try:
        from teachers.models import TeacherProfile
        teacher = TeacherProfile.objects.get(id=teacher_id)
        
        # Get implementations where teacher is lead or supporting
        lead_implementations = CurriculumImplementation.objects.filter(
            lead_teacher=teacher
        ).select_related('curriculum', 'class_enrolled', 'academic_year')
        
        supporting_implementations = CurriculumImplementation.objects.filter(
            supporting_teachers=teacher
        ).select_related('curriculum', 'class_enrolled', 'academic_year')
        
        response_data = {
            'teacher': teacher.user.get_full_name(),
            'lead_curricula': CurriculumImplementationSerializer(lead_implementations, many=True).data,
            'supporting_curricula': CurriculumImplementationSerializer(supporting_implementations, many=True).data
        }
        
        return Response(response_data)
        
    except TeacherProfile.DoesNotExist:
        return Response(
            {'error': 'Teacher not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

class CurriculumProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, implementation_id):
        try:
            implementation = CurriculumImplementation.objects.get(id=implementation_id)
            
            # This would integrate with actual progress tracking
            # For now, return basic progress information
            progress_data = {
                'implementation': CurriculumImplementationSerializer(implementation).data,
                'progress_metrics': {
                    'syllabus_coverage': 65,  # Percentage
                    'assessment_completion': 80,  # Percentage
                    'resource_utilization': 45,  # Percentage
                    'teacher_satisfaction': 85  # Percentage
                },
                'milestones': [
                    {'name': 'Curriculum Orientation', 'completed': True, 'date': '2024-01-15'},
                    {'name': 'First Assessment', 'completed': True, 'date': '2024-02-20'},
                    {'name': 'Mid-term Review', 'completed': False, 'date': '2024-04-15'},
                    {'name': 'Final Assessment', 'completed': False, 'date': '2024-06-30'}
                ]
            }
            
            return Response(progress_data)
            
        except CurriculumImplementation.DoesNotExist:
            return Response(
                {'error': 'Curriculum implementation not found.'},
                status=status.HTTP_404_NOT_FOUND
            )