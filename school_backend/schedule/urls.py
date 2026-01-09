# schedule/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'curricula', views.CurriculumViewSet, basename='curriculum')
router.register(r'grade-levels', views.GradeLevelViewSet, basename='gradelevel')
router.register(r'curriculum-subjects', views.CurriculumSubjectMappingViewSet, basename='curriculumsubject')
router.register(r'periods', views.PeriodViewSet, basename='period')
router.register(r'timetables', views.TimetableViewSet, basename='timetable')
router.register(r'breaks', views.BreakTimeViewSet, basename='break')

urlpatterns = [
    path('', include(router.urls)),
    path('periods/create/', views.PeriodCreateView.as_view(), name='period-create'),
    path('generate-timetable/', views.TimetableGeneratorView.as_view(), name='generate-timetable'),
    path('legacy/generate-timetable/', views.run_generate_timetable, name='legacy-generate-timetable'),
]