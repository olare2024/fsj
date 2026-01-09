# finance/admin.py
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse

from .models import (
    # Allocation Models
    ReceiptAllocation, PaymentAllocation,
    
    # Fee Structure
    FeeStructure,
    
    # Debt Management
    DebtRecord,
    
    # Transaction Models
    Receipt, Payment, PaymentRecord,
    
    # Enhanced Features
    InstallmentPlan, Discount, Waiver,
    
    # Financial Reports
    FinancialReport, Budget,
    
    # Tax and Compliance
    TaxConfiguration, ComplianceRecord,
    
    # Analytics and Dashboard
    FinancialDashboard,
    
    # Settings
    FinancialSettings,
    
    # Audit
    FinancialAuditLog,
    
    # Reconciliation
    BankReconciliation, MPesaReconciliation,
    
    # Constants
    KenyaPaymentMethod, PaymentStatus, FeeCategory,
)


# ==================== CUSTOM FILTERS ====================
class StatusFilter(SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return PaymentStatus.choices
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class PaymentMethodFilter(SimpleListFilter):
    title = 'Payment Method'
    parameter_name = 'payment_method'
    
    def lookups(self, request, model_admin):
        return KenyaPaymentMethod.choices
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(paid_through=self.value())
        return queryset


class CategoryFilter(SimpleListFilter):
    title = 'Category'
    parameter_name = 'category'
    
    def lookups(self, request, model_admin):
        return FeeCategory.choices
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category=self.value())
        return queryset


# ==================== MODEL ADMIN CLASSES ====================

@admin.register(ReceiptAllocation)
class ReceiptAllocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'default_amount', 'is_optional', 'is_active')
    list_filter = (CategoryFilter, 'is_optional', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'default_amount')


@admin.register(PaymentAllocation)
class PaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'has_budget_limit', 'annual_budget', 'is_active')
    list_filter = ('category', 'has_budget_limit', 'is_active')
    search_fields = ('name', 'description')


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'curriculum', 'grade_level', 'term', 'is_active')
    list_filter = ('curriculum', 'grade_level', 'term', 'is_active')
    search_fields = ('name',)


@admin.register(DebtRecord)
class DebtRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'term', 'original_amount', 'amount_paid', 'balance', 'is_overdue')
    list_filter = ('term', 'is_overdue')
    search_fields = ('student__first_name', 'student__last_name')
    
    def balance(self, obj):
        return obj.balance
    balance.short_description = 'Balance'


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'date', 'student', 'payer_name', 'amount', 'status')
    list_filter = (StatusFilter, PaymentMethodFilter, 'date')
    search_fields = ('receipt_number', 'payer_name', 'student__first_name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_number', 'date', 'paid_to', 'allocation', 'total_amount', 'status')
    list_filter = (StatusFilter, PaymentMethodFilter, 'date')
    search_fields = ('payment_number', 'paid_to')


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('payment', 'receipt', 'allocated_amount', 'allocation_date')
    search_fields = ('payment__payment_number', 'receipt__receipt_number')


@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ('student', 'installment_number', 'due_date', 'amount_due', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('student__first_name', 'student__last_name')


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('student', 'discount_type', 'discount_amount', 'status')
    list_filter = ('discount_type', 'status')
    search_fields = ('student__first_name', 'student__last_name')


@admin.register(Waiver)
class WaiverAdmin(admin.ModelAdmin):
    list_display = ('student', 'waiver_type', 'waiver_amount', 'status')
    list_filter = ('waiver_type', 'status')
    search_fields = ('student__first_name', 'student__last_name')


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'period_start', 'period_end', 'is_approved')
    list_filter = ('report_type', 'is_approved')
    search_fields = ('title',)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'total_budget', 'is_approved')
    list_filter = ('academic_year', 'is_approved')
    search_fields = ('name',)


@admin.register(TaxConfiguration)
class TaxConfigurationAdmin(admin.ModelAdmin):
    list_display = ('tax_name', 'tax_rate', 'is_active')
    list_editable = ('is_active', 'tax_rate')


@admin.register(ComplianceRecord)
class ComplianceRecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'record_type', 'due_date', 'status')
    list_filter = ('record_type', 'status')
    search_fields = ('title',)


@admin.register(FinancialDashboard)
class FinancialDashboardAdmin(admin.ModelAdmin):
    list_display = ('dashboard_date', 'total_receipts_today', 'total_payments_today')
    list_filter = ('dashboard_date',)


@admin.register(FinancialSettings)
class FinancialSettingsAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'currency', 'tax_rate')
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not FinancialSettings.objects.exists()


@admin.register(FinancialAuditLog)
class FinancialAuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'entity_type')
    list_filter = ('action', 'entity_type')
    search_fields = ('user__username', 'entity_type')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(BankReconciliation)
class BankReconciliationAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'statement_date', 'status')
    list_filter = ('bank_name', 'status')


@admin.register(MPesaReconciliation)
class MPesaReconciliationAdmin(admin.ModelAdmin):
    list_display = ('business_shortcode', 'transaction_date', 'status')
    list_filter = ('business_shortcode', 'status')