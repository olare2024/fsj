from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.utils import timezone
from decimal import Decimal
import csv
from django.http import HttpResponse

from .models import (
    FinancialSettings, ReceiptAllocation, PaymentAllocation,
    FeeStructure, DebtRecord, Receipt, Payment, PaymentRecord,
    InstallmentPlan, Discount, Waiver, Budget, FinancialReport,
    FinancialAuditLog
)


# ==================== INLINE ADMIN CLASSES ====================
class PaymentRecordInline(admin.TabularInline):
    model = PaymentRecord
    extra = 0
    fields = ('payment', 'allocated_amount', 'allocation_category', 'allocation_date')
    readonly_fields = ('payment', 'allocated_amount', 'allocation_category', 'allocation_date')


class InstallmentPlanInline(admin.TabularInline):
    model = InstallmentPlan
    extra = 0
    fields = ('installment_number', 'due_date', 'amount_due', 'amount_paid', 'status')
    readonly_fields = ('balance', 'is_overdue')
    
    def balance(self, obj):
        return obj.balance
    balance.short_description = 'Balance'
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'


# ==================== ADMIN CLASSES ====================
@admin.register(FinancialSettings)
class FinancialSettingsAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'currency', 'tax_rate', 'late_payment_fee')
    fieldsets = (
        ('School Information', {
            'fields': ('school_name', 'currency', 'currency_symbol')
        }),
        ('Fee Settings', {
            'fields': ('tax_rate', 'late_payment_fee', 'late_payment_days', 'installment_fee')
        }),
        ('M-Pesa Settings', {
            'fields': ('mpesa_shortcode', 'mpesa_passkey', 'mpesa_callback_url'),
            'classes': ('collapse',)
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'bank_account_number', 'bank_account_name', 'bank_branch'),
            'classes': ('collapse',)
        }),
        ('Notification Settings', {
            'fields': ('enable_auto_reminders', 'reminder_days_before', 
                      'enable_late_fees', 'enable_sms_notifications', 'enable_email_notifications'),
            'classes': ('collapse',)
        }),
        ('Document Settings', {
            'fields': ('receipt_prefix', 'payment_prefix', 'invoice_prefix'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Only allow one settings instance"""
        if FinancialSettings.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(ReceiptAllocation)
class ReceiptAllocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'default_amount', 'is_optional', 'is_active')
    list_filter = ('category', 'is_optional', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)


@admin.register(PaymentAllocation)
class PaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'has_budget_limit', 'annual_budget', 'is_active')
    list_filter = ('category', 'has_budget_limit', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('spent_this_year', 'budget_utilization')
    
    def spent_this_year(self, obj):
        return obj.spent_this_year
    spent_this_year.short_description = 'Spent This Year'
    
    def budget_utilization(self, obj):
        return f"{obj.budget_utilization}%"
    budget_utilization.short_description = 'Budget Utilization'


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade_level', 'term', 'curriculum', 'total_fees', 'is_active')
    list_filter = ('curriculum', 'grade_level', 'term__academic_year', 'is_active')
    search_fields = ('name', 'grade_level__name')
    readonly_fields = ('total_fees', 'mandatory_fees')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'curriculum', 'grade_level', 'term')
        }),
        ('Fee Components', {
            'fields': ('fee_components', 'total_fees', 'mandatory_fees')
        }),
        ('Payment Plans', {
            'fields': ('installment_allowed', 'max_installments', 'installment_due_dates')
        }),
        ('Discounts', {
            'fields': ('early_payment_discount', 'early_payment_deadline', 'sibling_discount')
        }),
        ('Status', {
            'fields': ('is_active', 'effective_from', 'effective_to')
        }),
    )
    
    def total_fees(self, obj):
        return f"KSh {obj.total_fees:,.2f}"
    total_fees.short_description = 'Total Fees'
    
    def mandatory_fees(self, obj):
        return f"KSh {obj.mandatory_fees:,.2f}"
    mandatory_fees.short_description = 'Mandatory Fees'


@admin.register(DebtRecord)
class DebtRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'term', 'original_amount', 'amount_paid', 'balance', 
                    'is_overdue', 'is_installment_plan', 'status_display')
    list_filter = ('term', 'is_overdue', 'is_installment_plan', 'term__academic_year')
    search_fields = ('student__first_name', 'student__last_name', 'student__username')
    readonly_fields = ('balance', 'paid_percentage', 'next_installment_due')
    inlines = [InstallmentPlanInline]
    actions = ['send_payment_reminders', 'apply_late_penalty']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student', 'term', 'fee_structure')
        }),
        ('Financial Details', {
            'fields': ('original_amount', 'amount_paid', 'discounts_applied', 
                      'late_penalty_applied', 'balance', 'paid_percentage')
        }),
        ('Installment Plan', {
            'fields': ('is_installment_plan', 'current_installment', 'total_installments',
                      'installment_amount', 'next_installment_due', 'payment_plan')
        }),
        ('Payment Tracking', {
            'fields': ('due_date', 'is_overdue', 'overdue_days')
        }),
        ('Reminders', {
            'fields': ('requires_parent_meeting', 'sent_reminder_sms', 
                      'sent_reminder_email', 'last_reminder_sent'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_reversed', 'reversed_on', 'reversed_by')
        }),
    )
    
    def balance(self, obj):
        return f"KSh {obj.balance:,.2f}"
    balance.short_description = 'Balance'
    
    def status_display(self, obj):
        if obj.is_reversed:
            return 'Reversed'
        elif obj.balance == Decimal('0.00'):
            return 'Paid'
        elif obj.is_overdue:
            return 'Overdue'
        else:
            return 'Pending'
    status_display.short_description = 'Status'
    
    def send_payment_reminders(self, request, queryset):
        count = 0
        for debt in queryset:
            try:
                debt.send_reminder(sms=True, email=True)
                count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error sending reminder for {debt}: {str(e)}',
                    messages.ERROR
                )
        
        self.message_user(
            request,
            f'{count} payment reminders sent successfully.',
            messages.SUCCESS
        )
    send_payment_reminders.short_description = "Send payment reminders"
    
    def apply_late_penalty(self, request, queryset):
        count = 0
        for debt in queryset:
            try:
                debt.apply_late_penalty()
                count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error applying penalty for {debt}: {str(e)}',
                    messages.ERROR
                )
        
        self.message_user(
            request,
            f'Late penalty applied to {count} debt records.',
            messages.SUCCESS
        )
    apply_late_penalty.short_description = "Apply late payment penalty"


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'date', 'student', 'payer_name', 
                    'amount', 'paid_through', 'status', 'is_printed')
    list_filter = ('status', 'paid_through', 'date', 'term')
    search_fields = ('receipt_number', 'student__first_name', 
                    'student__last_name', 'payer_name')
    readonly_fields = ('receipt_number', 'created_at', 'updated_at')
    fieldsets = (
        ('Receipt Information', {
            'fields': ('receipt_number', 'date', 'student', 'term', 'academic_year')
        }),
        ('Payer Information', {
            'fields': ('payer_name', 'payer_phone', 'payer_email')
        }),
        ('Payment Details', {
            'fields': ('paid_for', 'amount', 'paid_through')
        }),
        ('M-Pesa Details', {
            'fields': ('mpesa_transaction_id', 'mpesa_confirmation_code', 
                      'mpesa_phone_number', 'mpesa_transaction_time'),
            'classes': ('collapse',)
        }),
        ('Bank Transfer Details', {
            'fields': ('bank_reference', 'bank_name', 'bank_account_number'),
            'classes': ('collapse',)
        }),
        ('Status & Verification', {
            'fields': ('status', 'received_by', 'verified_by', 'verified_at')
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_printed', 'printed_at', 'printed_count',
                      'is_reconciled', 'reconciled_at', 'reconciled_by'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_printed', 'export_receipts_csv']
    
    def mark_as_printed(self, request, queryset):
        count = 0
        for receipt in queryset:
            receipt.mark_printed()
            count += 1
        
        self.message_user(
            request,
            f'{count} receipts marked as printed.',
            messages.SUCCESS
        )
    mark_as_printed.short_description = "Mark as printed"
    
    def export_receipts_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="receipts_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Receipt Number', 'Date', 'Student Name', 'Payer Name',
            'Amount', 'Payment Method', 'Status', 'Purpose'
        ])
        
        for receipt in queryset:
            writer.writerow([
                receipt.receipt_number,
                receipt.date,
                receipt.student.get_full_name(),
                receipt.payer_name,
                receipt.amount,
                receipt.get_paid_through_display(),
                receipt.get_status_display(),
                receipt.paid_for.name
            ])
        
        return response
    export_receipts_csv.short_description = "Export selected receipts to CSV"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_number', 'date', 'paid_to', 'description',
                    'total_amount', 'payment_method', 'status', 'requires_approval')
    list_filter = ('status', 'payment_method', 'date', 'category', 'requires_approval')
    search_fields = ('payment_number', 'paid_to', 'description', 'invoice_number')
    readonly_fields = ('payment_number', 'total_amount', 'submitted_at')
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_number', 'date', 'description')
        }),
        ('Payee Information', {
            'fields': ('paid_to', 'paid_to_phone', 'paid_to_email')
        }),
        ('Allocation & Category', {
            'fields': ('allocation', 'category')
        }),
        ('Financial Details', {
            'fields': ('amount', 'tax_amount', 'total_amount')
        }),
        ('Payment Method', {
            'fields': ('payment_method', 'bank_name', 'bank_account_number', 
                      'bank_reference', 'mpesa_transaction_id', 'mpesa_confirmation_code',
                      'cheque_number', 'cheque_date')
        }),
        ('Approval & Verification', {
            'fields': ('status', 'requires_approval', 'approved_by', 'approved_at',
                      'authorized_by', 'verified_by', 'verified_at')
        }),
        ('Submission', {
            'fields': ('submitted_by', 'submitted_at')
        }),
        ('Documents & Reconciliation', {
            'fields': ('supporting_documents', 'invoice_number', 
                      'is_reconciled', 'reconciled_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes', 'internal_notes'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_payments', 'mark_as_paid', 'export_payments_csv']
    
    def approve_payments(self, request, queryset):
        count = 0
        for payment in queryset:
            if payment.requires_approval and payment.status == PaymentStatus.PENDING:
                payment.approve(request.user, "Approved via admin")
                count += 1
        
        self.message_user(
            request,
            f'{count} payments approved.',
            messages.SUCCESS
        )
    approve_payments.short_description = "Approve selected payments"
    
    def mark_as_paid(self, request, queryset):
        count = 0
        for payment in queryset:
            if payment.status == PaymentStatus.PENDING:
                payment.mark_as_paid(request.user)
                count += 1
        
        self.message_user(
            request,
            f'{count} payments marked as paid.',
            messages.SUCCESS
        )
    mark_as_paid.short_description = "Mark as paid"
    
    def export_payments_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payments_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Payment Number', 'Date', 'Paid To', 'Description',
            'Amount', 'Tax', 'Total', 'Payment Method', 'Status', 'Category'
        ])
        
        for payment in queryset:
            writer.writerow([
                payment.payment_number,
                payment.date,
                payment.paid_to,
                payment.description[:50],
                payment.amount,
                payment.tax_amount,
                payment.total_amount,
                payment.get_payment_method_display(),
                payment.get_status_display(),
                payment.get_category_display()
            ])
        
        return response
    export_payments_csv.short_description = "Export selected payments to CSV"


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('payment', 'receipt', 'debt_record', 'allocated_amount', 
                    'allocation_date', 'is_reconciled')
    list_filter = ('allocation_date', 'is_reconciled', 'allocation_category')
    search_fields = ('payment__payment_number', 'receipt__receipt_number', 
                    'debt_record__student__first_name')
    readonly_fields = ('allocation_date', 'allocated_by')


@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ('installment_number', 'student', 'term', 'due_date', 
                    'amount_due', 'amount_paid', 'balance', 'status', 'is_overdue_display')
    list_filter = ('status', 'term', 'payment_method', 'due_date')
    search_fields = ('student__first_name', 'student__last_name', 'reference')
    readonly_fields = ('balance', 'is_overdue')
    actions = ['mark_as_paid_action']
    
    def balance(self, obj):
        return f"KSh {obj.balance:,.2f}"
    balance.short_description = 'Balance'
    
    def is_overdue_display(self, obj):
        return obj.is_overdue
    is_overdue_display.boolean = True
    is_overdue_display.short_description = 'Overdue'
    
    def mark_as_paid_action(self, request, queryset):
        count = 0
        for installment in queryset:
            if installment.status in ['pending', 'partially_paid']:
                installment.mark_as_paid(
                    amount=installment.amount_due,
                    payment_date=timezone.now().date(),
                    payment_method='cash',
                    reference=f"Admin payment {timezone.now().strftime('%Y%m%d%H%M%S')}"
                )
                count += 1
        
        self.message_user(
            request,
            f'{count} installments marked as paid.',
            messages.SUCCESS
        )
    mark_as_paid_action.short_description = "Mark selected as paid"


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('student', 'discount_type', 'discount_amount', 
                    'term', 'status', 'approved_by')
    list_filter = ('discount_type', 'status', 'term')
    search_fields = ('student__first_name', 'student__last_name', 'reason')
    readonly_fields = ('approved_at',)
    actions = ['approve_discounts', 'reject_discounts']
    
    def approve_discounts(self, request, queryset):
        count = 0
        for discount in queryset:
            if discount.status == 'pending':
                discount.status = 'approved'
                discount.approved_by = request.user
                discount.approved_at = timezone.now()
                discount.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} discounts approved.',
            messages.SUCCESS
        )
    approve_discounts.short_description = "Approve selected discounts"
    
    def reject_discounts(self, request, queryset):
        count = 0
        for discount in queryset:
            if discount.status == 'pending':
                discount.status = 'rejected'
                discount.approved_by = request.user
                discount.approved_at = timezone.now()
                discount.approval_notes = f"Rejected by {request.user.get_full_name()}"
                discount.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} discounts rejected.',
            messages.SUCCESS
        )
    reject_discounts.short_description = "Reject selected discounts"


@admin.register(Waiver)
class WaiverAdmin(admin.ModelAdmin):
    list_display = ('student', 'waiver_type', 'waiver_amount', 
                    'term', 'status', 'approved_by')
    list_filter = ('waiver_type', 'status', 'term')
    search_fields = ('student__first_name', 'student__last_name', 'reason')
    readonly_fields = ('approved_at',)
    actions = ['approve_waivers', 'reject_waivers']
    
    def approve_waivers(self, request, queryset):
        count = 0
        for waiver in queryset:
            if waiver.status == 'pending':
                waiver.status = 'approved'
                waiver.approved_by = request.user
                waiver.approved_at = timezone.now()
                waiver.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} waivers approved.',
            messages.SUCCESS
        )
    approve_waivers.short_description = "Approve selected waivers"
    
    def reject_waivers(self, request, queryset):
        count = 0
        for waiver in queryset:
            if waiver.status == 'pending':
                waiver.status = 'rejected'
                waiver.approved_by = request.user
                waiver.approved_at = timezone.now()
                waiver.approval_notes = f"Rejected by {request.user.get_full_name()}"
                waiver.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} waivers rejected.',
            messages.SUCCESS
        )
    reject_waivers.short_description = "Reject selected waivers"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'term', 'total_budget', 
                    'actual_spent', 'variance_percentage', 'is_approved')
    list_filter = ('academic_year', 'is_approved')
    search_fields = ('name', 'academic_year__name')
    readonly_fields = ('total_budget', 'actual_spent', 'variance_percentage', 'is_on_track')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'academic_year', 'term')
        }),
        ('Budget Details', {
            'fields': ('budget_items', 'total_budget', 'allocated_amount')
        }),
        ('Actual Spending', {
            'fields': ('actual_spent', 'variance_percentage', 'is_on_track')
        }),
        ('Approval', {
            'fields': ('is_approved', 'approved_by', 'approved_at')
        }),
    )
    
    actions = ['approve_budgets', 'update_actual_spending']
    
    def approve_budgets(self, request, queryset):
        count = 0
        for budget in queryset:
            if not budget.is_approved:
                budget.is_approved = True
                budget.approved_by = request.user
                budget.approved_at = timezone.now()
                budget.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} budgets approved.',
            messages.SUCCESS
        )
    approve_budgets.short_description = "Approve selected budgets"
    
    def update_actual_spending(self, request, queryset):
        count = 0
        for budget in queryset:
            budget.update_actual_spent()
            count += 1
        
        self.message_user(
            request,
            f'Actual spending updated for {count} budgets.',
            messages.SUCCESS
        )
    update_actual_spending.short_description = "Update actual spending"


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'period_start', 'period_end',
                    'total_income', 'total_expenses', 'net_profit', 'is_approved')
    list_filter = ('report_type', 'is_approved', 'period_start')
    search_fields = ('title', 'description')
    readonly_fields = ('generated_at', 'generated_by', 'total_income', 
                      'total_expenses', 'net_profit')
    fieldsets = (
        ('Report Information', {
            'fields': ('report_type', 'title', 'description')
        }),
        ('Period', {
            'fields': ('period_start', 'period_end')
        }),
        ('Report Data', {
            'fields': ('report_data',)
        }),
        ('Summary Statistics', {
            'fields': ('total_income', 'total_expenses', 'net_profit')
        }),
        ('Generation Details', {
            'fields': ('generated_by', 'generated_at')
        }),
        ('Approval', {
            'fields': ('is_approved', 'approved_by', 'approved_at')
        }),
        ('Export Details', {
            'fields': ('exported_formats', 'last_exported'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reports', 'export_reports_csv']
    
    def approve_reports(self, request, queryset):
        count = 0
        for report in queryset:
            if not report.is_approved:
                report.is_approved = True
                report.approved_by = request.user
                report.approved_at = timezone.now()
                report.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} reports approved.',
            messages.SUCCESS
        )
    approve_reports.short_description = "Approve selected reports"
    
    def export_reports_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="financial_reports_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Title', 'Report Type', 'Period Start', 'Period End',
            'Total Income', 'Total Expenses', 'Net Profit', 'Status'
        ])
        
        for report in queryset:
            writer.writerow([
                report.title,
                report.get_report_type_display(),
                report.period_start,
                report.period_end,
                report.total_income,
                report.total_expenses,
                report.net_profit,
                'Approved' if report.is_approved else 'Pending'
            ])
        
        return response
    export_reports_csv.short_description = "Export selected reports to CSV"


@admin.register(FinancialAuditLog)
class FinancialAuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'entity_type', 'entity_id')
    list_filter = ('action', 'entity_type', 'timestamp')
    search_fields = ('user__username', 'entity_id', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action', 'entity_type', 'entity_id',
                      'old_value', 'new_value', 'ip_address', 'user_agent')
    
    def has_add_permission(self, request):
        """Disable adding audit logs manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable changing audit logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only allow superusers to delete audit logs"""
        return request.user.is_superuser