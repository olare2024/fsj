# finance/urls.py
"""
Finance URLs for Delvok Academy School Management System
Kenya-specific finance routes with M-Pesa integration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'finance'

# Create a main router
router = DefaultRouter()

# ==================== ALLOCATION ROUTES ====================
router.register(r'receipt-allocations', views.ReceiptAllocationViewSet, basename='receipt-allocation')
router.register(r'payment-allocations', views.PaymentAllocationViewSet, basename='payment-allocation')

# ==================== FEE STRUCTURE ROUTES ====================
router.register(r'fee-structures', views.FeeStructureViewSet, basename='fee-structure')

# ==================== DEBT MANAGEMENT ROUTES ====================
router.register(r'debt-records', views.DebtRecordViewSet, basename='debt-record')

# ==================== RECEIPT ROUTES ====================
router.register(r'receipts', views.ReceiptViewSet, basename='receipt')

# ==================== PAYMENT ROUTES ====================
router.register(r'payments', views.PaymentViewSet, basename='payment')

# ==================== FINANCIAL REPORT ROUTES ====================
router.register(r'financial-reports', views.FinancialReportViewSet, basename='financial-report')

# ==================== API VIEWS ====================
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # ==================== DASHBOARD AND ANALYTICS ====================
    path('dashboard/', views.financial_dashboard, name='financial-dashboard'),
    path('summary/', views.financial_summary, name='financial-summary'),
    path('debt-summary/', views.debt_summary, name='debt-summary'),
    
    # ==================== BULK OPERATIONS ====================
    path('bulk-apply-payments/', views.bulk_apply_payments, name='bulk-apply-payments'),
    path('export-data/', views.export_financial_data, name='export-financial-data'),
    
    # ==================== FINANCIAL YEAR AND UTILITIES ====================
    path('financial-year/', views.get_financial_year, name='get-financial-year'),
    path('payment-methods/', views.get_payment_methods, name='get-payment-methods'),
    path('fee-categories/', views.get_fee_categories, name='get-fee-categories'),
    
    # ==================== REPORTS ====================
    path('reports/fee-collection/', views.FeeCollectionReportView.as_view(), name='fee-collection-report'),
    path('reports/expenditure/', views.ExpenditureReportView.as_view(), name='expenditure-report'),
    
    # ==================== STUDENT PORTAL ====================
    path('student-portal/', views.StudentFinancialPortalView.as_view(), name='student-financial-portal'),
    
    # ==================== MPESA INTEGRATION ====================
    path('mpesa/callback/', views.MpesaCallbackView.as_view(), name='mpesa-callback'),
]

# ==================== CUSTOM URL PATTERNS ====================
# Fee structure specific endpoints
urlpatterns += [
    path('fee-structures/current/', 
         views.FeeStructureViewSet.as_view({'get': 'current_structures'}), 
         name='current-fee-structures'),
    path('fee-structures/by-curriculum/', 
         views.FeeStructureViewSet.as_view({'get': 'by_curriculum'}), 
         name='fee-structures-by-curriculum'),
    path('fee-structures/<uuid:pk>/duplicate/', 
         views.FeeStructureViewSet.as_view({'post': 'duplicate'}), 
         name='duplicate-fee-structure'),
]

# Receipt specific endpoints
urlpatterns += [
    path('receipts/daily-summary/', 
         views.ReceiptViewSet.as_view({'get': 'daily_summary'}), 
         name='daily-receipt-summary'),
    path('receipts/bulk-create/', 
         views.ReceiptViewSet.as_view({'post': 'bulk_create'}), 
         name='bulk-create-receipts'),
    path('receipts/<uuid:pk>/verify/', 
         views.ReceiptViewSet.as_view({'post': 'verify'}), 
         name='verify-receipt'),
    path('receipts/<uuid:pk>/mark-printed/', 
         views.ReceiptViewSet.as_view({'post': 'mark_printed'}), 
         name='mark-receipt-printed'),
    path('receipts/<uuid:pk>/reconcile/', 
         views.ReceiptViewSet.as_view({'post': 'reconcile'}), 
         name='reconcile-receipt'),
]

# Payment specific endpoints
urlpatterns += [
    path('payments/expenditure-summary/', 
         views.PaymentViewSet.as_view({'get': 'expenditure_summary'}), 
         name='expenditure-summary'),
    path('payments/<uuid:pk>/approve/', 
         views.PaymentViewSet.as_view({'post': 'approve'}), 
         name='approve-payment'),
    path('payments/<uuid:pk>/mark-as-paid/', 
         views.PaymentViewSet.as_view({'post': 'mark_as_paid'}), 
         name='mark-payment-paid'),
]

# Debt specific endpoints
urlpatterns += [
    path('debt-records/summary/', 
         views.DebtRecordViewSet.as_view({'get': 'summary'}), 
         name='debt-summary'),
    path('debt-records/by-class/', 
         views.DebtRecordViewSet.as_view({'get': 'by_class'}), 
         name='debt-by-class'),
    path('debt-records/<uuid:pk>/apply-payment/', 
         views.DebtRecordViewSet.as_view({'post': 'apply_payment'}), 
         name='apply-debt-payment'),
    path('debt-records/<uuid:pk>/setup-installment-plan/', 
         views.DebtRecordViewSet.as_view({'post': 'setup_installment_plan'}), 
         name='setup-installment-plan'),
]

# Allocation specific endpoints
urlpatterns += [
    path('receipt-allocations/categories/', 
         views.ReceiptAllocationViewSet.as_view({'get': 'categories'}), 
         name='receipt-allocation-categories'),
    path('receipt-allocations/summary/', 
         views.ReceiptAllocationViewSet.as_view({'get': 'summary'}), 
         name='receipt-allocation-summary'),
    path('payment-allocations/budget-status/', 
         views.PaymentAllocationViewSet.as_view({'get': 'budget_status'}), 
         name='payment-allocation-budget-status'),
]

# Financial report endpoints
urlpatterns += [
    path('financial-reports/generate-daily/', 
         views.FinancialReportViewSet.as_view({'get': 'generate_daily'}), 
         name='generate-daily-report'),
]

# ==================== ADMIN-ONLY ENDPOINTS ====================
# These endpoints are for admin users only
admin_urlpatterns = [
    path('admin/reports/quarterly/', views.QuarterlyReportView.as_view(), name='quarterly-report'),
    path('admin/reports/annual/', views.AnnualReportView.as_view(), name='annual-report'),
    path('admin/audit-logs/', views.FinancialAuditView.as_view(), name='financial-audit'),
    path('admin/settings/', views.FinancialSettingsView.as_view(), name='financial-settings'),
    path('admin/backup/', views.FinancialBackupView.as_view(), name='financial-backup'),
]

# Add admin URLs with appropriate permissions (handled in views)
urlpatterns += admin_urlpatterns

# ==================== PUBLIC ENDPOINTS (for parents/students) ====================
public_urlpatterns = [
    path('public/invoice/', views.PublicInvoiceView.as_view(), name='public-invoice'),
    path('public/fee-structure/', views.PublicFeeStructureView.as_view(), name='public-fee-structure'),
    path('public/payment-methods/', views.PublicPaymentMethodsView.as_view(), name='public-payment-methods'),
]

urlpatterns += public_urlpatterns

# ==================== WEBHOOK ENDPOINTS ====================
# For external services (M-Pesa, banks, etc.)
webhook_urlpatterns = [
    path('webhook/mpesa/', views.MpesaWebhookView.as_view(), name='mpesa-webhook'),
    path('webhook/bank/', views.BankWebhookView.as_view(), name='bank-webhook'),
    path('webhook/sms/', views.SMSWebhookView.as_view(), name='sms-webhook'),
    path('webhook/email/', views.EmailWebhookView.as_view(), name='email-webhook'),
]

urlpatterns += webhook_urlpatterns

# ==================== EXPORT/IMPORT ENDPOINTS ====================
export_import_urlpatterns = [
    path('export/receipts/', views.ReceiptExportView.as_view(), name='export-receipts'),
    path('export/payments/', views.PaymentExportView.as_view(), name='export-payments'),
    path('export/debts/', views.DebtExportView.as_view(), name='export-debts'),
    path('import/fee-structures/', views.FeeStructureImportView.as_view(), name='import-fee-structures'),
    path('import/students/', views.StudentFinanceImportView.as_view(), name='import-student-finance'),
]

urlpatterns += export_import_urlpatterns

# ==================== BUDGET MANAGEMENT ENDPOINTS ====================
budget_urlpatterns = [
    path('budgets/', views.BudgetViewSet.as_view({'get': 'list', 'post': 'create'}), name='budget-list'),
    path('budgets/<uuid:pk>/', views.BudgetViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='budget-detail'),
    path('budgets/<uuid:pk>/approve/', views.BudgetViewSet.as_view({'post': 'approve'}), name='approve-budget'),
    path('budgets/current/', views.BudgetViewSet.as_view({'get': 'current_budgets'}), name='current-budgets'),
]

urlpatterns += budget_urlpatterns

# ==================== COMPLIANCE AND TAX ENDPOINTS ====================
compliance_urlpatterns = [
    path('tax-config/', views.TaxConfigurationViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='tax-config'),
    path('compliance-records/', views.ComplianceRecordViewSet.as_view({'get': 'list', 'post': 'create'}), name='compliance-list'),
    path('compliance-records/<uuid:pk>/', views.ComplianceRecordViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='compliance-detail'),
    path('compliance-records/<uuid:pk>/verify/', views.ComplianceRecordViewSet.as_view({'post': 'verify'}), name='verify-compliance'),
    path('compliance-records/upcoming/', views.ComplianceRecordViewSet.as_view({'get': 'upcoming_compliance'}), name='upcoming-compliance'),
]

urlpatterns += compliance_urlpatterns

# ==================== PAYMENT RECORD ENDPOINTS ====================
payment_record_urlpatterns = [
    path('payment-records/', views.PaymentRecordViewSet.as_view({'get': 'list'}), name='payment-record-list'),
    path('payment-records/<uuid:pk>/', views.PaymentRecordViewSet.as_view({'get': 'retrieve'}), name='payment-record-detail'),
    path('payment-records/by-student/<uuid:student_id>/', views.PaymentRecordViewSet.as_view({'get': 'by_student'}), name='payment-records-by-student'),
    path('payment-records/by-term/<uuid:term_id>/', views.PaymentRecordViewSet.as_view({'get': 'by_term'}), name='payment-records-by-term'),
]

urlpatterns += payment_record_urlpatterns

# ==================== FINANCIAL UTILITY ENDPOINTS ====================
utility_urlpatterns = [
    path('utils/generate-receipt-number/', views.generate_receipt_number, name='generate-receipt-number'),
    path('utils/generate-payment-number/', views.generate_payment_number, name='generate-payment-number'),
    path('utils/calculate-late-penalty/<uuid:debt_id>/', views.calculate_late_penalty, name='calculate-late-penalty'),
    path('utils/calculate-sibling-discount/<uuid:student_id>/', views.calculate_sibling_discount, name='calculate-sibling-discount'),
    path('utils/check-budget-utilization/<uuid:allocation_id>/', views.check_budget_utilization, name='check-budget-utilization'),
]

urlpatterns += utility_urlpatterns

# ==================== NOTIFICATION ENDPOINTS ====================
notification_urlpatterns = [
    path('notifications/fee-reminders/', views.send_fee_reminders, name='send-fee-reminders'),
    path('notifications/overdue-alerts/', views.send_overdue_alerts, name='send-overdue-alerts'),
    path('notifications/receipt-confirmation/<uuid:receipt_id>/', views.send_receipt_confirmation, name='send-receipt-confirmation'),
    path('notifications/payment-confirmation/<uuid:payment_id>/', views.send_payment_confirmation, name='send-payment-confirmation'),
]

urlpatterns += notification_urlpatterns

# ==================== ANALYTICS AND INSIGHTS ENDPOINTS ====================
analytics_urlpatterns = [
    path('analytics/revenue-trends/', views.revenue_trends, name='revenue-trends'),
    path('analytics/expense-trends/', views.expense_trends, name='expense-trends'),
    path('analytics/collection-efficiency/', views.collection_efficiency, name='collection-efficiency'),
    path('analytics/budget-vs-actual/', views.budget_vs_actual, name='budget-vs-actual'),
    path('analytics/top-debtors/', views.top_debtors, name='top-debtors'),
    path('analytics/top-revenue-sources/', views.top_revenue_sources, name='top-revenue-sources'),
]

urlpatterns += analytics_urlpatterns

# ==================== RECONCILIATION ENDPOINTS ====================
reconciliation_urlpatterns = [
    path('reconciliation/bank/', views.bank_reconciliation, name='bank-reconciliation'),
    path('reconciliation/mpesa/', views.mpesa_reconciliation, name='mpesa-reconciliation'),
    path('reconciliation/cash/', views.cash_reconciliation, name='cash-reconciliation'),
    path('reconciliation/process/', views.process_reconciliation, name='process-reconciliation'),
    path('reconciliation/reports/', views.reconciliation_reports, name='reconciliation-reports'),
]

urlpatterns += reconciliation_urlpatterns

# ==================== INSTALLMENT PLAN ENDPOINTS ====================
installment_urlpatterns = [
    path('installments/', views.InstallmentPlanViewSet.as_view({'get': 'list', 'post': 'create'}), name='installment-list'),
    path('installments/<uuid:pk>/', views.InstallmentPlanViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='installment-detail'),
    path('installments/<uuid:pk>/process-payment/', views.InstallmentPlanViewSet.as_view({'post': 'process_payment'}), name='process-installment-payment'),
    path('installments/upcoming/', views.InstallmentPlanViewSet.as_view({'get': 'upcoming_installments'}), name='upcoming-installments'),
    path('installments/overdue/', views.InstallmentPlanViewSet.as_view({'get': 'overdue_installments'}), name='overdue-installments'),
]

urlpatterns += installment_urlpatterns

# ==================== DISCOUNT AND WAIVER ENDPOINTS ====================
discount_urlpatterns = [
    path('discounts/', views.DiscountViewSet.as_view({'get': 'list', 'post': 'create'}), name='discount-list'),
    path('discounts/<uuid:pk>/', views.DiscountViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='discount-detail'),
    path('discounts/<uuid:pk>/approve/', views.DiscountViewSet.as_view({'post': 'approve'}), name='approve-discount'),
    path('discounts/types/', views.DiscountViewSet.as_view({'get': 'discount_types'}), name='discount-types'),
    path('waivers/', views.WaiverViewSet.as_view({'get': 'list', 'post': 'create'}), name='waiver-list'),
    path('waivers/<uuid:pk>/', views.WaiverViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='waiver-detail'),
    path('waivers/<uuid:pk>/approve/', views.WaiverViewSet.as_view({'post': 'approve'}), name='approve-waiver'),
]

urlpatterns += discount_urlpatterns

# ==================== AUDIT AND LOGGING ENDPOINTS ====================
audit_urlpatterns = [
    path('audit-logs/financial/', views.FinancialAuditLogViewSet.as_view({'get': 'list'}), name='financial-audit-logs'),
    path('audit-logs/user/<uuid:user_id>/', views.FinancialAuditLogViewSet.as_view({'get': 'by_user'}), name='user-audit-logs'),
    path('audit-logs/action/<str:action>/', views.FinancialAuditLogViewSet.as_view({'get': 'by_action'}), name='action-audit-logs'),
    path('audit-logs/date-range/', views.FinancialAuditLogViewSet.as_view({'get': 'by_date_range'}), name='date-range-audit-logs'),
]

urlpatterns += audit_urlpatterns

# ==================== API DOCUMENTATION AND HEALTH CHECK ====================
doc_urlpatterns = [
    path('docs/', views.finance_api_docs, name='finance-api-docs'),
    path('health/', views.finance_health_check, name='finance-health-check'),
    path('version/', views.finance_api_version, name='finance-api-version'),
]

urlpatterns += doc_urlpatterns

# ==================== BACKUP AND RECOVERY ENDPOINTS ====================
backup_urlpatterns = [
    path('backup/create/', views.create_financial_backup, name='create-financial-backup'),
    path('backup/restore/', views.restore_financial_backup, name='restore-financial-backup'),
    path('backup/list/', views.list_financial_backups, name='list-financial-backups'),
    path('backup/<uuid:backup_id>/download/', views.download_financial_backup, name='download-financial-backup'),
    path('backup/<uuid:backup_id>/delete/', views.delete_financial_backup, name='delete-financial-backup'),
]

urlpatterns += backup_urlpatterns

# ==================== MOBILE APP SPECIFIC ENDPOINTS ====================
mobile_urlpatterns = [
    path('mobile/dashboard/', views.mobile_financial_dashboard, name='mobile-financial-dashboard'),
    path('mobile/student-balance/<uuid:student_id>/', views.mobile_student_balance, name='mobile-student-balance'),
    path('mobile/make-payment/', views.mobile_make_payment, name='mobile-make-payment'),
    path('mobile/payment-history/', views.mobile_payment_history, name='mobile-payment-history'),
    path('mobile/receipts/', views.mobile_receipts, name='mobile-receipts'),
]

urlpatterns += mobile_urlpatterns

# ==================== BULK SMS AND EMAIL ENDPOINTS ====================
communication_urlpatterns = [
    path('communications/send-fee-statements/', views.send_bulk_fee_statements, name='send-bulk-fee-statements'),
    path('communications/send-receipts/', views.send_bulk_receipts, name='send-bulk-receipts'),
    path('communications/send-overdue-alerts/', views.send_bulk_overdue_alerts, name='send-bulk-overdue-alerts'),
    path('communications/send-payment-reminders/', views.send_bulk_payment_reminders, name='send-bulk-payment-reminders'),
]

urlpatterns += communication_urlpatterns

# ==================== DATA VALIDATION AND CLEANUP ====================
validation_urlpatterns = [
    path('validation/check-duplicates/', views.check_duplicate_transactions, name='check-duplicate-transactions'),
    path('validation/fix-data-issues/', views.fix_financial_data_issues, name='fix-financial-data-issues'),
    path('validation/validate-receipts/', views.validate_receipts, name='validate-receipts'),
    path('validation/validate-payments/', views.validate_payments, name='validate-payments'),
]

urlpatterns += validation_urlpatterns

# ==================== INTEGRATION ENDPOINTS ====================
integration_urlpatterns = [
    path('integrations/school-erp/', views.school_erp_integration, name='school-erp-integration'),
    path('integrations/government-portal/', views.government_portal_integration, name='government-portal-integration'),
    path('integrations/banking-api/', views.banking_api_integration, name='banking-api-integration'),
    path('integrations/sms-gateway/', views.sms_gateway_integration, name='sms-gateway-integration'),
]

urlpatterns += integration_urlpatterns

# ==================== CUSTOM REPORT GENERATION ====================
custom_report_urlpatterns = [
    path('reports/custom/generate/', views.generate_custom_report, name='generate-custom-report'),
    path('reports/custom/templates/', views.list_report_templates, name='list-report-templates'),
    path('reports/custom/templates/<uuid:template_id>/', views.get_report_template, name='get-report-template'),
    path('reports/custom/templates/<uuid:template_id>/run/', views.run_report_template, name='run-report-template'),
]

urlpatterns += custom_report_urlpatterns

# ==================== EXPORT FORMATS ====================
export_format_urlpatterns = [
    path('export/pdf/receipt/<uuid:receipt_id>/', views.export_receipt_pdf, name='export-receipt-pdf'),
    path('export/pdf/invoice/<uuid:student_id>/', views.export_invoice_pdf, name='export-invoice-pdf'),
    path('export/pdf/statement/<uuid:student_id>/', views.export_statement_pdf, name='export-statement-pdf'),
    path('export/excel/financial-report/', views.export_financial_report_excel, name='export-financial-report-excel'),
    path('export/csv/transactions/', views.export_transactions_csv, name='export-transactions-csv'),
]

urlpatterns += export_format_urlpatterns

# ==================== SEARCH AND FILTER ENDPOINTS ====================
search_urlpatterns = [
    path('search/transactions/', views.search_transactions, name='search-transactions'),
    path('search/students/', views.search_students_financial, name='search-students-financial'),
    path('search/receipts/', views.search_receipts_advanced, name='search-receipts-advanced'),
    path('search/payments/', views.search_payments_advanced, name='search-payments-advanced'),
]

urlpatterns += search_urlpatterns

# ==================== BATCH PROCESSING ====================
batch_urlpatterns = [
    path('batch/process-end-of-day/', views.process_end_of_day, name='process-end-of-day'),
    path('batch/process-end-of-month/', views.process_end_of_month, name='process-end-of-month'),
    path('batch/process-end-of-term/', views.process_end_of_term, name='process-end-of-term'),
    path('batch/generate-statements/', views.batch_generate_statements, name='batch-generate-statements'),
    path('batch/calculate-penalties/', views.batch_calculate_penalties, name='batch-calculate-penalties'),
]

urlpatterns += batch_urlpatterns

# ==================== SYSTEM CONFIGURATION ====================
config_urlpatterns = [
    path('config/finance-settings/', views.get_finance_settings, name='get-finance-settings'),
    path('config/update-finance-settings/', views.update_finance_settings, name='update-finance-settings'),
    path('config/tax-rates/', views.get_tax_rates, name='get-tax-rates'),
    path('config/update-tax-rates/', views.update_tax_rates, name='update-tax-rates'),
    path('config/payment-gateways/', views.get_payment_gateways, name='get-payment-gateways'),
    path('config/update-payment-gateways/', views.update_payment_gateways, name='update-payment-gateways'),
]

urlpatterns += config_urlpatterns

# ==================== REAL-TIME UPDATES (WebSockets fallback) ====================
realtime_urlpatterns = [
    path('realtime/updates/', views.get_realtime_updates, name='get-realtime-updates'),
    path('realtime/notifications/', views.get_realtime_notifications, name='get-realtime-notifications'),
    path('realtime/dashboard-data/', views.get_realtime_dashboard_data, name='get-realtime-dashboard-data'),
]

urlpatterns += realtime_urlpatterns

# ==================== DATA VISUALIZATION ENDPOINTS ====================
visualization_urlpatterns = [
    path('visualization/revenue-chart/', views.revenue_chart_data, name='revenue-chart-data'),
    path('visualization/expense-chart/', views.expense_chart_data, name='expense-chart-data'),
    path('visualization/collection-chart/', views.collection_chart_data, name='collection-chart-data'),
    path('visualization/budget-chart/', views.budget_chart_data, name='budget-chart-data'),
    path('visualization/debt-chart/', views.debt_chart_data, name='debt-chart-data'),
]

urlpatterns += visualization_urlpatterns

# ==================== ERROR HANDLING AND DEBUGGING ====================
debug_urlpatterns = [
    path('debug/transaction-flow/', views.debug_transaction_flow, name='debug-transaction-flow'),
    path('debug/data-integrity/', views.debug_data_integrity, name='debug-data-integrity'),
    path('debug/performance-metrics/', views.debug_performance_metrics, name='debug-performance-metrics'),
]

urlpatterns += debug_urlpatterns

# ==================== LEGACY SYSTEM MIGRATION ====================
migration_urlpatterns = [
    path('migrate/old-data/', views.migrate_old_financial_data, name='migrate-old-financial-data'),
    path('migrate/verify/', views.verify_migration, name='verify-migration'),
    path('migrate/rollback/', views.rollback_migration, name='rollback-migration'),
]

urlpatterns += migration_urlpatterns

# ==================== API RATE LIMITING AND MONITORING ====================
monitoring_urlpatterns = [
    path('monitoring/api-usage/', views.get_api_usage_stats, name='get-api-usage-stats'),
    path('monitoring/performance/', views.get_performance_stats, name='get-performance-stats'),
    path('monitoring/errors/', views.get_error_logs, name='get-error-logs'),
]

urlpatterns += monitoring_urlpatterns

# ==================== SECURITY AND ACCESS CONTROL ====================
security_urlpatterns = [
    path('security/access-logs/', views.get_access_logs, name='get-access-logs'),
    path('security/permissions/', views.get_user_permissions, name='get-user-permissions'),
    path('security/audit-trail/', views.get_audit_trail, name='get-audit-trail'),
]

urlpatterns += security_urlpatterns
