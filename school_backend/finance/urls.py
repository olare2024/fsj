from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'settings', views.FinancialSettingsViewSet, basename='financialsettings')
router.register(r'receipt-allocations', views.ReceiptAllocationViewSet)
router.register(r'payment-allocations', views.PaymentAllocationViewSet)
router.register(r'fee-structures', views.FeeStructureViewSet)
router.register(r'debts', views.DebtRecordViewSet)
router.register(r'receipts', views.ReceiptViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'payment-records', views.PaymentRecordViewSet)
router.register(r'installment-plans', views.InstallmentPlanViewSet)
router.register(r'discounts', views.DiscountViewSet)
router.register(r'waivers', views.WaiverViewSet)
router.register(r'budgets', views.BudgetViewSet)
router.register(r'reports', views.FinancialReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Dashboard
    path('dashboard/', views.financial_dashboard, name='financial-dashboard'),
    
    # Reports
    path('reports/fee-collection/', views.fee_collection_report, name='fee-collection-report'),
    path('reports/expenses/', views.expense_report, name='expense-report'),
    
    # Student financial summary
    path('students/<uuid:student_id>/financial-summary/', views.student_financial_summary, name='student-financial-summary'),
    
    # Export endpoints
    path('export/receipts-csv/', views.export_receipts_csv, name='export-receipts-csv'),
    path('export/payments-csv/', views.export_payments_csv, name='export-payments-csv'),
    
    # Additional endpoints
    path('payments/pending-approval/', views.PaymentViewSet.as_view({'get': 'pending_approval'}), name='pending-approval-payments'),
    path('installment-plans/overdue/', views.InstallmentPlanViewSet.as_view({'get': 'overdue'}), name='overdue-installments'),
    path('budgets/current/', views.BudgetViewSet.as_view({'get': 'current'}), name='current-budget'),
    path('fee-structures/by-grade-term/', views.FeeStructureViewSet.as_view({'get': 'by_grade_and_term'}), name='fee-structure-by-grade-term'),
    
    # Receipts summary
    path('receipts/daily-summary/', views.ReceiptViewSet.as_view({'get': 'daily_summary'}), name='receipts-daily-summary'),
]

# Add namespace for reverse URL lookups
app_name = 'finance'