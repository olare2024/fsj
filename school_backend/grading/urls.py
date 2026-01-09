from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'grading-scales', views.GradingScaleViewSet)
router.register(r'grading-periods', views.GradingPeriodViewSet)
router.register(r'assessment-types', views.AssessmentTypeViewSet)
router.register(r'assessments', views.AssessmentViewSet)
router.register(r'student-grades', views.StudentGradeViewSet)
router.register(r'subject-grades', views.SubjectGradeViewSet)
router.register(r'report-cards', views.ReportCardViewSet)
router.register(r'gradebooks', views.GradebookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('statistics/', views.GradeStatisticsView.as_view(), name='grade-statistics'),
    path('performance-trends/', views.PerformanceTrendView.as_view(), name='performance-trends'),
    path('dashboard/', views.grading_dashboard, name='grading-dashboard'),
]