from django.urls import path
from . import views

urlpatterns = [
    # Curriculum Management
    path('curriculums/', views.CurriculumListView.as_view(), name='curriculum-list'),
    path('curriculums/<uuid:pk>/', views.CurriculumDetailView.as_view(), name='curriculum-detail'),
    
    # CBC Curriculum
    path('cbc/strands/', views.CBCStrandListView.as_view(), name='cbc-strand-list'),
    path('cbc/strands/<uuid:pk>/', views.CBCStrandDetailView.as_view(), name='cbc-strand-detail'),
    path('cbc/strands/<uuid:strand_id>/sub-strands/', views.CBCSubStrandByStrandView.as_view(), name='cbc-substrand-list'),
    path('cbc/sub-strands/', views.CBCSubStrandListView.as_view(), name='cbc-all-substrands'),
    
    # ICSE Curriculum
    path('icse/subjects/', views.ICSESubjectListView.as_view(), name='icse-subject-list'),
    path('icse/subjects/<uuid:pk>/', views.ICSESubjectDetailView.as_view(), name='icse-subject-detail'),
    path('icse/subjects/<uuid:subject_id>/syllabus/', views.ICSESyllabusView.as_view(), name='icse-syllabus'),
    
    # American Curriculum
    path('american/standards/', views.AmericanStandardListView.as_view(), name='american-standard-list'),
    path('american/courses/', views.AmericanCourseListView.as_view(), name='american-course-list'),
    
    # Curriculum Mapping
    path('mappings/', views.CurriculumMappingListView.as_view(), name='curriculum-mapping-list'),
    path('mappings/<uuid:pk>/', views.CurriculumMappingDetailView.as_view(), name='curriculum-mapping-detail'),
    
    # Curriculum Implementation
    path('implementations/', views.CurriculumImplementationListView.as_view(), name='curriculum-implementation-list'),
    path('implementations/<uuid:pk>/', views.CurriculumImplementationDetailView.as_view(), name='curriculum-implementation-detail'),
    path('implementations/<uuid:implementation_id>/progress/', views.CurriculumProgressView.as_view(), name='curriculum-progress'),
    
    # Learning Objectives
    path('learning-objectives/', views.LearningObjectiveListView.as_view(), name='learning-objective-list'),
    
    # Resource Library
    path('resources/', views.ResourceLibraryListView.as_view(), name='resource-library-list'),
    path('resources/<uuid:pk>/', views.ResourceLibraryDetailView.as_view(), name='resource-library-detail'),
    path('resources/search/', views.curriculum_resources_search, name='resource-search'),
    
    # Professional Development
    path('professional-development/', views.ProfessionalDevelopmentListView.as_view(), name='professional-development-list'),
    
    # Analysis and Reporting
    path('overview/', views.CurriculumOverviewView.as_view(), name='curriculum-overview'),
    path('analysis/cross-curriculum/', views.CrossCurriculumAnalysisView.as_view(), name='cross-curriculum-analysis'),
    
    # Teacher-specific endpoints
    path('teachers/<uuid:teacher_id>/assignments/', views.teacher_curriculum_assignments, name='teacher-curriculum-assignments'),
]