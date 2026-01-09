# finance/serializers.py
"""
Finance Serializers for Delvok Academy School Management System
Kenya-specific finance serializers with M-Pesa, CBC, and 8-4-4 support
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging
from decimal import Decimal, ROUND_HALF_UP

from .models import PaymentRecord 

from administration.models import  School
from academics.models import AcademicTerm, AcademicYear
from accounts.models import User
from accounts.serializers import UserSerializer
from administration.serializers import  SchoolSerializer
from academics.serializers import AcademicTermSerializer, AcademicYearSerializer, ClassSerializer
from .models import (
    ReceiptAllocation, PaymentAllocation, FeeStructure, DebtRecord,
    Receipt, Payment, PaymentRecord, FinancialReport, Budget,
    TaxConfiguration, ComplianceRecord, FinancialDashboard,
    KenyaPaymentMethod, PaymentStatus, FeeCategory,
    FinancialUtils, InstallmentPlan, Discount, Waiver, FinancialAuditLog
)

logger = logging.getLogger(__name__)


# ==================== ALLOCATION SERIALIZERS ====================
class ReceiptAllocationSerializer(serializers.ModelSerializer):
    """Serializer for Receipt Allocation"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_active_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ReceiptAllocation
        fields = [
            'id', 'name', 'abbr', 'description', 'category', 'category_display',
            'default_amount', 'is_optional', 'applies_to_boarding', 
            'applies_to_day_scholars', 'is_active', 'is_active_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_active_display(self, obj):
        return _("Active") if obj.is_active else _("Inactive")


class PaymentAllocationSerializer(serializers.ModelSerializer):
    """Serializer for Payment Allocation"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    spent_this_year = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    budget_utilization = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    remaining_budget = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentAllocation
        fields = [
            'id', 'name', 'abbr', 'description', 'category', 'category_display',
            'has_budget_limit', 'annual_budget', 'is_active', 'spent_this_year',
            'budget_utilization', 'remaining_budget', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'spent_this_year', 'budget_utilization']
    
    def get_remaining_budget(self, obj):
        if obj.has_budget_limit and obj.annual_budget:
            remaining = obj.annual_budget - obj.spent_this_year
            return max(Decimal('0.00'), remaining)
        return None
    
    def validate_annual_budget(self, value):
        if value and value < 0:
            raise serializers.ValidationError(_("Annual budget cannot be negative."))
        return value


# ==================== FEE STRUCTURE SERIALIZERS ====================
class FeeComponentSerializer(serializers.Serializer):
    """Serializer for individual fee components"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    required = serializers.BooleanField(default=True)
    description = serializers.CharField(required=False, allow_blank=True)


class FeeStructureSerializer(serializers.ModelSerializer):
    """Serializer for Fee Structure"""
    term = AcademicTermSerializer(read_only=True)
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        write_only=True,
        source='term'
    )
    
    curriculum_display = serializers.CharField(source='get_curriculum_display', read_only=True)
    grade_level_display = serializers.CharField(source='get_grade_level_display', read_only=True)
    
    fee_components = serializers.JSONField(required=False)
    installment_due_dates = serializers.JSONField(required=False)
    
    total_fees = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    mandatory_fees = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    is_current = serializers.SerializerMethodField()
    
    class Meta:
        model = FeeStructure
        fields = [
            'id', 'name', 'curriculum', 'curriculum_display', 'grade_level', 
            'grade_level_display', 'term', 'term_id', 'fee_components',
            'installment_allowed', 'max_installments', 'installment_due_dates',
            'early_payment_discount', 'early_payment_deadline', 'sibling_discount',
            'is_active', 'effective_from', 'effective_to', 'total_fees',
            'mandatory_fees', 'is_current', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_fees', 'mandatory_fees']
    
    def get_is_current(self, obj):
        today = timezone.now().date()
        if obj.effective_to and obj.effective_from:
            return obj.effective_from <= today <= obj.effective_to
        return obj.is_active
    
    def validate(self, data):
        # Validate effective dates
        effective_from = data.get('effective_from')
        effective_to = data.get('effective_to')
        
        if effective_to and effective_from and effective_to < effective_from:
            raise serializers.ValidationError({
                'effective_to': _('Effective to date must be after effective from date.')
            })
        
        # Validate early payment deadline
        early_deadline = data.get('early_payment_deadline')
        if early_deadline and effective_from and early_deadline < effective_from:
            raise serializers.ValidationError({
                'early_payment_deadline': _('Early payment deadline cannot be before effective from date.')
            })
        
        return data


# ==================== DEBT MANAGEMENT SERIALIZERS ====================
class DebtRecordSerializer(serializers.ModelSerializer):
    """Serializer for Debt Record"""
    student = UserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'),
        write_only=True,
        source='student'
    )
    
    term = AcademicTermSerializer(read_only=True)
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        write_only=True,
        source='term'
    )
    
    fee_structure = FeeStructureSerializer(read_only=True)
    fee_structure_id = serializers.PrimaryKeyRelatedField(
        queryset=FeeStructure.objects.all(),
        write_only=True,
        source='fee_structure',
        required=False,
        allow_null=True
    )
    
    # Computed fields
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    paid_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    amount_added = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    # Status indicators
    is_overdue_display = serializers.SerializerMethodField()
    installment_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = DebtRecord
        fields = [
            'id', 'student', 'student_id', 'term', 'term_id', 'fee_structure', 'fee_structure_id',
            'original_amount', 'amount_paid', 'discounts_applied', 'late_penalty_applied',
            'is_installment_plan', 'current_installment', 'total_installments',
            'installment_amount', 'due_date', 'is_overdue', 'is_overdue_display',
            'overdue_days', 'next_installment_due', 'payment_plan', 'is_reversed',
            'reversed_on', 'reversed_by', 'requires_parent_meeting', 'sent_reminder_sms',
            'sent_reminder_email', 'last_reminder_sent', 'balance', 'paid_percentage',
            'amount_added', 'installment_progress', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'balance', 'paid_percentage', 'amount_added',
            'is_overdue', 'overdue_days', 'reversed_on', 'reversed_by'
        ]
    
    def get_is_overdue_display(self, obj):
        return _("Overdue") if obj.is_overdue else _("Current")
    
    def get_installment_progress(self, obj):
        if obj.is_installment_plan:
            return {
                'current': obj.current_installment,
                'total': obj.total_installments,
                'percentage': int((obj.current_installment / obj.total_installments) * 100) if obj.total_installments > 0 else 0
            }
        return None
    
    def validate(self, data):
        # Validate installment plan consistency
        is_installment = data.get('is_installment_plan', self.instance.is_installment_plan if self.instance else False)
        total_installments = data.get('total_installments', self.instance.total_installments if self.instance else 1)
        
        if is_installment and total_installments < 2:
            raise serializers.ValidationError({
                'total_installments': _('Total installments must be at least 2 for installment plans.')
            })
        
        # Validate due date
        due_date = data.get('due_date')
        if due_date and due_date < timezone.now().date():
            raise serializers.ValidationError({
                'due_date': _('Due date cannot be in the past.')
            })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        # Auto-calculate installment amount if installment plan
        if validated_data.get('is_installment_plan', False):
            original_amount = validated_data.get('original_amount', Decimal('0.00'))
            total_installments = validated_data.get('total_installments', 1)
            validated_data['installment_amount'] = (original_amount / total_installments).quantize(Decimal('0.01'))
        
        return super().create(validated_data)


# ==================== RECEIPT SERIALIZERS ====================
class ReceiptSerializer(serializers.ModelSerializer):
    """Serializer for Receipt"""
    payer_name = serializers.CharField(required=True)
    student = UserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'),
        write_only=True,
        source='student'
    )
    
    term = AcademicTermSerializer(read_only=True)
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        write_only=True,
        source='term'
    )
    
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        write_only=True,
        source='academic_year',
        required=False
    )
    
    paid_for = ReceiptAllocationSerializer(read_only=True)
    paid_for_id = serializers.PrimaryKeyRelatedField(
        queryset=ReceiptAllocation.objects.all(),
        write_only=True,
        source='paid_for'
    )
    
    received_by_name = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()
    reconciled_by_name = serializers.SerializerMethodField()
    
    paid_through_display = serializers.CharField(source='get_paid_through_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # M-Pesa specific
    mpesa_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Receipt
        fields = [
            'id', 'receipt_number', 'date', 'payer_name', 'payer_phone', 'payer_email',
            'student', 'student_id', 'term', 'term_id', 'academic_year', 'academic_year_id',
            'paid_for', 'paid_for_id', 'amount', 'paid_through', 'paid_through_display',
            'mpesa_transaction_id', 'mpesa_confirmation_code', 'mpesa_phone_number',
            'mpesa_transaction_time', 'bank_reference', 'bank_name', 'bank_account_number',
            'status', 'status_display', 'received_by', 'received_by_name', 'verified_by',
            'verified_by_name', 'verified_at', 'notes', 'is_printed', 'printed_at',
            'printed_count', 'is_reconciled', 'reconciled_at', 'reconciled_by',
            'reconciled_by_name', 'mpesa_details', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'receipt_number', 'created_at', 'updated_at', 'received_by', 'verified_by',
            'verified_at', 'printed_at', 'reconciled_by', 'reconciled_at'
        ]
    
    def get_received_by_name(self, obj):
        return obj.received_by.get_full_name() if obj.received_by else None
    
    def get_verified_by_name(self, obj):
        return obj.verified_by.get_full_name() if obj.verified_by else None
    
    def get_reconciled_by_name(self, obj):
        return obj.reconciled_by.get_full_name() if obj.reconciled_by else None
    
    def get_mpesa_details(self, obj):
        if obj.paid_through == KenyaPaymentMethod.MPESA:
            return {
                'transaction_id': obj.mpesa_transaction_id,
                'confirmation_code': obj.mpesa_confirmation_code,
                'phone_number': obj.mpesa_phone_number,
                'transaction_time': obj.mpesa_transaction_time
            }
        return None
    
    def validate(self, data):
        amount = data.get('amount', Decimal('0.00'))
        if amount <= 0:
            raise serializers.ValidationError({
                'amount': _('Amount must be greater than zero.')
            })
        
        # Validate M-Pesa details if M-Pesa payment
        if data.get('paid_through') == KenyaPaymentMethod.MPESA:
            if not data.get('mpesa_transaction_id'):
                raise serializers.ValidationError({
                    'mpesa_transaction_id': _('M-Pesa transaction ID is required for M-Pesa payments.')
                })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        # Set received_by to current user
        validated_data['received_by'] = self.context['request'].user
        
        # Set status to completed by default (can be changed)
        validated_data['status'] = PaymentStatus.COMPLETED
        
        # Generate academic year if not provided
        if not validated_data.get('academic_year') and validated_data.get('term'):
            validated_data['academic_year'] = validated_data['term'].academic_year
        
        return super().create(validated_data)


# ==================== PAYMENT SERIALIZERS ====================
class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment/Expense"""
    allocation = PaymentAllocationSerializer(read_only=True)
    allocation_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentAllocation.objects.all(),
        write_only=True,
        source='allocation'
    )
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # User references
    submitted_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    authorized_by_name = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()
    
    # Budget tracking
    budget_utilization = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_number', 'date', 'description', 'paid_to', 'paid_to_phone',
            'paid_to_email', 'allocation', 'allocation_id', 'category', 'category_display',
            'amount', 'tax_amount', 'total_amount', 'payment_method', 'payment_method_display',
            'bank_name', 'bank_account_number', 'bank_reference', 'mpesa_transaction_id',
            'mpesa_confirmation_code', 'cheque_number', 'cheque_date', 'status',
            'status_display', 'requires_approval', 'approved_by', 'approved_by_name',
            'approved_at', 'authorized_by', 'authorized_by_name', 'verified_by',
            'verified_by_name', 'verified_at', 'submitted_by', 'submitted_by_name',
            'submitted_at', 'supporting_documents', 'invoice_number', 'is_reconciled',
            'reconciled_at', 'notes', 'internal_notes', 'budget_utilization',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'payment_number', 'created_at', 'updated_at', 'total_amount',
            'submitted_by', 'submitted_at', 'approved_by', 'approved_at',
            'authorized_by', 'verified_by', 'verified_at', 'reconciled_at'
        ]
    
    def get_submitted_by_name(self, obj):
        return obj.submitted_by.get_full_name() if obj.submitted_by else None
    
    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None
    
    def get_authorized_by_name(self, obj):
        return obj.authorized_by.get_full_name() if obj.authorized_by else None
    
    def get_verified_by_name(self, obj):
        return obj.verified_by.get_full_name() if obj.verified_by else None
    
    def get_budget_utilization(self, obj):
        if obj.allocation and obj.allocation.has_budget_limit and obj.allocation.annual_budget:
            spent = obj.allocation.spent_this_year
            return (spent / obj.allocation.annual_budget * 100).quantize(Decimal('0.01'))
        return None
    
    def validate(self, data):
        amount = data.get('amount', Decimal('0.00'))
        tax_amount = data.get('tax_amount', Decimal('0.00'))
        
        if amount <= 0:
            raise serializers.ValidationError({
                'amount': _('Amount must be greater than zero.')
            })
        
        if tax_amount < 0:
            raise serializers.ValidationError({
                'tax_amount': _('Tax amount cannot be negative.')
            })
        
        # Calculate total amount
        data['total_amount'] = amount + tax_amount
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        # Set submitted_by to current user
        validated_data['submitted_by'] = self.context['request'].user
        
        # Set default status
        if validated_data.get('requires_approval', False):
            validated_data['status'] = PaymentStatus.PENDING
        else:
            validated_data['status'] = PaymentStatus.COMPLETED
        
        return super().create(validated_data)


# ==================== BUDGET SERIALIZERS ====================
class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for Budget management"""
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        write_only=True,
        source='academic_year'
    )
    
    allocated_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    
    # Status indicators
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_current = serializers.SerializerMethodField()
    
    # Computed fields
    remaining_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    utilization_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'description', 'academic_year', 'academic_year_id',
            'department', 'budget_category', 'allocated_amount', 'spent_amount',
            'remaining_balance', 'utilization_rate', 'start_date', 'end_date',
            'status', 'status_display', 'allocated_by', 'allocated_by_name',
            'allocated_at', 'approved_by', 'approved_by_name', 'approved_at',
            'notes', 'is_current', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'remaining_balance', 'utilization_rate',
            'allocated_by', 'allocated_at', 'approved_by', 'approved_at'
        ]
    
    def get_allocated_by_name(self, obj):
        return obj.allocated_by.get_full_name() if obj.allocated_by else None
    
    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None
    
    def get_is_current(self, obj):
        today = timezone.now().date()
        return obj.start_date <= today <= obj.end_date
    
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if end_date < start_date:
            raise serializers.ValidationError({
                'end_date': _('End date must be after start date.')
            })
        
        allocated_amount = data.get('allocated_amount', Decimal('0.00'))
        if allocated_amount <= 0:
            raise serializers.ValidationError({
                'allocated_amount': _('Allocated amount must be greater than zero.')
            })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        # Set allocated_by to current user
        validated_data['allocated_by'] = self.context['request'].user
        validated_data['allocated_at'] = timezone.now()
        
        # Set default status if not provided
        if not validated_data.get('status'):
            validated_data['status'] = 'draft'
        
        return super().create(validated_data)


# ==================== FINANCIAL REPORT SERIALIZERS ====================
class FinancialReportSerializer(serializers.ModelSerializer):
    """Serializer for Financial Reports"""
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    generated_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    
    # Formatted amounts
    total_income_formatted = serializers.SerializerMethodField()
    total_expenses_formatted = serializers.SerializerMethodField()
    net_profit_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialReport
        fields = [
            'id', 'report_type', 'report_type_display', 'title', 'description',
            'period_start', 'period_end', 'report_data', 'total_income',
            'total_income_formatted', 'total_expenses', 'total_expenses_formatted',
            'net_profit', 'net_profit_formatted', 'generated_by', 'generated_by_name',
            'generated_at', 'is_approved', 'approved_by', 'approved_by_name',
            'approved_at', 'exported_formats', 'last_exported', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'generated_by', 'generated_at',
            'approved_by', 'approved_at', 'last_exported'
        ]
    
    def get_generated_by_name(self, obj):
        return obj.generated_by.get_full_name() if obj.generated_by else None
    
    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None
    
    def get_total_income_formatted(self, obj):
        return FinancialUtils.format_currency(obj.total_income)
    
    def get_total_expenses_formatted(self, obj):
        return FinancialUtils.format_currency(obj.total_expenses)
    
    def get_net_profit_formatted(self, obj):
        return FinancialUtils.format_currency(obj.net_profit)
    
    def validate(self, data):
        period_start = data.get('period_start')
        period_end = data.get('period_end')
        
        if period_end < period_start:
            raise serializers.ValidationError({
                'period_end': _('Period end date must be after period start date.')
            })
        
        return data


# ==================== DASHBOARD AND ANALYTICS SERIALIZERS ====================
class FinancialDashboardSerializer(serializers.ModelSerializer):
    """Serializer for Financial Dashboard"""
    
    # Formatted metrics
    total_receipts_today_formatted = serializers.SerializerMethodField()
    total_payments_today_formatted = serializers.SerializerMethodField()
    cash_balance_formatted = serializers.SerializerMethodField()
    outstanding_debt_formatted = serializers.SerializerMethodField()
    
    # Status indicators
    fee_collection_status = serializers.SerializerMethodField()
    budget_status = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialDashboard
        fields = [
            'id', 'dashboard_date', 'total_receipts_today', 'total_receipts_today_formatted',
            'total_payments_today', 'total_payments_today_formatted', 'cash_balance',
            'cash_balance_formatted', 'fee_collection_rate', 'outstanding_debt',
            'outstanding_debt_formatted', 'pending_approvals', 'term_metrics',
            'daily_trends', 'generated_at', 'last_refreshed', 'is_current',
            'fee_collection_status', 'budget_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_receipts_today_formatted(self, obj):
        return FinancialUtils.format_currency(obj.total_receipts_today)
    
    def get_total_payments_today_formatted(self, obj):
        return FinancialUtils.format_currency(obj.total_payments_today)
    
    def get_cash_balance_formatted(self, obj):
        return FinancialUtils.format_currency(obj.cash_balance)
    
    def get_outstanding_debt_formatted(self, obj):
        return FinancialUtils.format_currency(obj.outstanding_debt)
    
    def get_fee_collection_status(self, obj):
        if obj.fee_collection_rate >= 90:
            return 'excellent'
        elif obj.fee_collection_rate >= 75:
            return 'good'
        elif obj.fee_collection_rate >= 60:
            return 'fair'
        else:
            return 'poor'
    
    def get_budget_status(self, obj):
        # Check if any allocation is over budget
        # This would need additional logic
        return 'on_track'


class FinancialSummarySerializer(serializers.Serializer):
    """Serializer for financial summary data"""
    period = serializers.CharField()
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    fee_collection_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    outstanding_debt = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Breakdowns
    income_breakdown = serializers.DictField(child=serializers.DecimalField(max_digits=12, decimal_places=2))
    expense_breakdown = serializers.DictField(child=serializers.DecimalField(max_digits=12, decimal_places=2))
    
    # Trends
    monthly_trend = serializers.ListField(child=serializers.DictField())
    comparison_with_previous = serializers.DictField()


class DebtSummarySerializer(serializers.Serializer):
    """Serializer for debt summary"""
    total_debt = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_outstanding = serializers.DecimalField(max_digits=12, decimal_places=2)
    collection_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Breakdown by class/grade
    by_class = serializers.ListField(child=serializers.DictField())
    by_curriculum = serializers.DictField()
    overdue_debts = serializers.IntegerField()
    
    # Top debtors
    top_debtors = serializers.ListField(child=serializers.DictField())


# ==================== COMPLIANCE AND TAX SERIALIZERS ====================
class TaxConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for Tax Configuration"""
    is_active_display = serializers.SerializerMethodField()
    applies_to_display = serializers.CharField(source='get_applies_to_display', read_only=True)
    
    class Meta:
        model = TaxConfiguration
        fields = [
            'id', 'tax_name', 'tax_rate', 'applies_to', 'applies_to_display',
            'kra_pin_required', 'tax_code', 'effective_from', 'effective_to',
            'is_active', 'is_active_display', 'auto_calculate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_active_display(self, obj):
        return _("Active") if obj.is_active else _("Inactive")
    
    def validate(self, data):
        effective_from = data.get('effective_from')
        effective_to = data.get('effective_to')
        
        if effective_to and effective_to < effective_from:
            raise serializers.ValidationError({
                'effective_to': _('Effective to date must be after effective from date.')
            })
        
        tax_rate = data.get('tax_rate', Decimal('0.00'))
        if tax_rate < 0 or tax_rate > 100:
            raise serializers.ValidationError({
                'tax_rate': _('Tax rate must be between 0 and 100 percent.')
            })
        
        return data


class ComplianceRecordSerializer(serializers.ModelSerializer):
    """Serializer for Compliance Records"""
    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    responsible_person_name = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()
    
    # Status indicators
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = ComplianceRecord
        fields = [
            'id', 'record_type', 'record_type_display', 'title', 'description',
            'due_date', 'completion_date', 'status', 'status_display',
            'responsible_person', 'responsible_person_name', 'verified_by',
            'verified_by_name', 'supporting_documents', 'evidence_of_compliance',
            'notes', 'next_review_date', 'kra_filing', 'kra_reference',
            'ministry_registration', 'ministry_reference', 'is_overdue',
            'days_until_due', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_responsible_person_name(self, obj):
        return obj.responsible_person.get_full_name() if obj.responsible_person else None
    
    def get_verified_by_name(self, obj):
        return obj.verified_by.get_full_name() if obj.verified_by else None
    
    def get_is_overdue(self, obj):
        if obj.status not in ['completed', 'cancelled'] and obj.due_date:
            return obj.due_date < timezone.now().date()
        return False
    
    def get_days_until_due(self, obj):
        if obj.due_date and obj.status not in ['completed', 'cancelled']:
            delta = obj.due_date - timezone.now().date()
            return delta.days
        return None
    
    def validate(self, data):
        due_date = data.get('due_date')
        completion_date = data.get('completion_date')
        
        if completion_date and due_date and completion_date < due_date:
            raise serializers.ValidationError({
                'completion_date': _('Completion date cannot be before due date.')
            })
        
        return data


# ==================== PAYMENT RECORD SERIALIZERS ====================
class PaymentRecordSerializer(serializers.ModelSerializer):
    """Serializer for Payment Record"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    receipt_number = serializers.CharField(read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = PaymentRecord
        fields = [
            'id', 'student', 'student_name', 'fee_structure', 'amount_paid',
            'payment_date', 'payment_method', 'payment_method_display',
            'receipt_number', 'verified', 'verified_by', 'verification_date',
            'remarks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['receipt_number', 'verified', 'verified_by', 'verification_date']

    def create(self, validated_data):
        # Generate receipt number if not provided
        if 'receipt_number' not in validated_data:
            import uuid
            validated_data['receipt_number'] = f"REC-{uuid.uuid4().hex[:8].upper()}"
        
        # Set payment date to now if not provided
        if 'payment_date' not in validated_data:
            validated_data['payment_date'] = timezone.now()
        
        return super().create(validated_data)


# ==================== PAYMENT PLAN SERIALIZERS ====================
class PaymentPlanSerializer(serializers.Serializer):
    """Serializer for payment plan setup"""
    installments = serializers.IntegerField(min_value=2, max_value=12, required=True)
    due_dates = serializers.ListField(
        child=serializers.DateField(),
        required=True
    )
    
    def validate(self, data):
        installments = data.get('installments')
        due_dates = data.get('due_dates')
        
        if len(due_dates) != installments:
            raise serializers.ValidationError({
                'due_dates': f'Number of due dates ({len(due_dates)}) must match number of installments ({installments}).'
            })
        
        # Check if due dates are in chronological order
        for i in range(len(due_dates) - 1):
            if due_dates[i] >= due_dates[i + 1]:
                raise serializers.ValidationError({
                    'due_dates': 'Due dates must be in chronological order.'
                })
        
        return data


# ==================== BULK OPERATION SERIALIZERS ====================
class BulkReceiptCreateSerializer(serializers.Serializer):
    """Serializer for bulk receipt creation"""
    student_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='student')),
        required=True
    )
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        required=True
    )
    paid_for_id = serializers.PrimaryKeyRelatedField(
        queryset=ReceiptAllocation.objects.all(),
        required=True
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    paid_through = serializers.ChoiceField(choices=KenyaPaymentMethod.choices, required=True)
    payer_name = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        amount = data.get('amount')
        if amount <= 0:
            raise serializers.ValidationError({
                'amount': 'Amount must be greater than zero.'
            })
        
        return data


class BulkPaymentApplySerializer(serializers.Serializer):
    """Serializer for bulk payment application to debts"""
    debt_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=DebtRecord.objects.all()),
        required=True
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    payment_date = serializers.DateField(default=timezone.now)
    payment_method = serializers.ChoiceField(choices=KenyaPaymentMethod.choices, required=True)
    reference = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        amount = data.get('amount')
        if amount <= 0:
            raise serializers.ValidationError({
                'amount': 'Amount must be greater than zero.'
            })
        
        return data


from .models import FinancialSettings

class FinancialSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialSettings
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']



        # Add these serializers to your existing finance/serializers.py file

# ==================== INSTALLMENT PLAN SERIALIZERS ====================
class InstallmentPlanSerializer(serializers.ModelSerializer):
    """Serializer for Installment Plan"""
    student = UserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'),
        write_only=True,
        source='student'
    )
    
    term = AcademicTermSerializer(read_only=True)
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        write_only=True,
        source='term'
    )
    
    debt_record = DebtRecordSerializer(read_only=True)
    debt_record_id = serializers.PrimaryKeyRelatedField(
        queryset=DebtRecord.objects.all(),
        write_only=True,
        source='debt_record',
        required=False,
        allow_null=True
    )
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    is_overdue = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = InstallmentPlan
        fields = [
            'id', 'installment_number', 'student', 'student_id', 'term', 'term_id',
            'debt_record', 'debt_record_id', 'due_date', 'amount_due', 'amount_paid',
            'payment_date', 'payment_method', 'payment_method_display', 'reference',
            'status', 'status_display', 'notes', 'is_active', 'created_at',
            'updated_at', 'is_overdue', 'days_overdue'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'is_overdue', 'days_overdue',
            'payment_date', 'status'
        ]
    
    def get_is_overdue(self, obj):
        if obj.status == 'pending' and obj.due_date:
            return obj.due_date < timezone.now().date()
        return False
    
    def get_days_overdue(self, obj):
        if self.get_is_overdue(obj):
            return (timezone.now().date() - obj.due_date).days
        return 0
    
    def validate(self, data):
        due_date = data.get('due_date')
        amount_due = data.get('amount_due', Decimal('0.00'))
        
        if due_date and due_date < timezone.now().date():
            raise serializers.ValidationError({
                'due_date': 'Due date cannot be in the past.'
            })
        
        if amount_due <= 0:
            raise serializers.ValidationError({
                'amount_due': 'Amount due must be greater than zero.'
            })
        
        return data


# ==================== DISCOUNT SERIALIZERS ====================
class DiscountSerializer(serializers.ModelSerializer):
    """Serializer for Discounts"""
    student = UserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'),
        write_only=True,
        source='student'
    )
    
    term = AcademicTermSerializer(read_only=True)
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        write_only=True,
        source='term',
        required=False,
        allow_null=True
    )
    
    debt_record = DebtRecordSerializer(read_only=True)
    debt_record_id = serializers.PrimaryKeyRelatedField(
        queryset=DebtRecord.objects.all(),
        write_only=True,
        source='debt_record',
        required=False,
        allow_null=True
    )
    
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    approved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Discount
        fields = [
            'id', 'student', 'student_id', 'term', 'term_id', 'debt_record',
            'debt_record_id', 'discount_type', 'discount_type_display',
            'discount_amount', 'discount_percentage', 'reason', 'status',
            'status_display', 'approved_by', 'approved_by_name', 'approved_at',
            'approval_notes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'approved_by', 'approved_at'
        ]
    
    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None
    
    def validate(self, data):
        discount_amount = data.get('discount_amount', Decimal('0.00'))
        discount_percentage = data.get('discount_percentage', Decimal('0.00'))
        
        if discount_amount < 0:
            raise serializers.ValidationError({
                'discount_amount': 'Discount amount cannot be negative.'
            })
        
        if discount_percentage < 0 or discount_percentage > 100:
            raise serializers.ValidationError({
                'discount_percentage': 'Discount percentage must be between 0 and 100.'
            })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        # Set discount amount based on percentage if applicable
        discount_percentage = validated_data.get('discount_percentage')
        if discount_percentage and not validated_data.get('discount_amount'):
            # Calculate discount amount from debt record or fee structure
            debt_record = validated_data.get('debt_record')
            if debt_record:
                validated_data['discount_amount'] = (
                    debt_record.original_amount * discount_percentage / 100
                ).quantize(Decimal('0.01'))
        
        # Set default status if not provided
        if not validated_data.get('status'):
            validated_data['status'] = 'pending'
        
        return super().create(validated_data)


# ==================== WAIVER SERIALIZERS ====================
class WaiverSerializer(serializers.ModelSerializer):
    """Serializer for Fee Waivers"""
    student = UserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'),
        write_only=True,
        source='student'
    )
    
    term = AcademicTermSerializer(read_only=True)
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        write_only=True,
        source='term',
        required=False,
        allow_null=True
    )
    
    debt_record = DebtRecordSerializer(read_only=True)
    debt_record_id = serializers.PrimaryKeyRelatedField(
        queryset=DebtRecord.objects.all(),
        write_only=True,
        source='debt_record',
        required=False,
        allow_null=True
    )
    
    waiver_type_display = serializers.CharField(source='get_waiver_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    approved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Waiver
        fields = [
            'id', 'student', 'student_id', 'term', 'term_id', 'debt_record',
            'debt_record_id', 'waiver_type', 'waiver_type_display', 'waiver_amount',
            'reason', 'supporting_documents', 'status', 'status_display',
            'approved_by', 'approved_by_name', 'approved_at', 'approval_notes',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'approved_by', 'approved_at'
        ]
    
    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None
    
    def validate(self, data):
        waiver_amount = data.get('waiver_amount', Decimal('0.00'))
        
        if waiver_amount < 0:
            raise serializers.ValidationError({
                'waiver_amount': 'Waiver amount cannot be negative.'
            })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        # Set default status if not provided
        if not validated_data.get('status'):
            validated_data['status'] = 'pending'
        
        return super().create(validated_data)


# ==================== AUDIT LOG SERIALIZERS ====================
class FinancialAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for Financial Audit Logs"""
    user_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    entity_type_display = serializers.CharField(source='get_entity_type_display', read_only=True)
    
    formatted_timestamp = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialAuditLog
        fields = [
            'id', 'timestamp', 'formatted_timestamp', 'user', 'user_name',
            'action', 'action_display', 'entity_type', 'entity_type_display',
            'entity_id', 'old_value', 'new_value', 'ip_address', 'user_agent',
            'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() if obj.user else 'System'
    
    def get_formatted_timestamp(self, obj):
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Format JSON fields for readability
        if data.get('old_value'):
            try:
                import json
                data['old_value'] = json.loads(data['old_value'])
            except (json.JSONDecodeError, TypeError):
                pass
        
        if data.get('new_value'):
            try:
                import json
                data['new_value'] = json.loads(data['new_value'])
            except (json.JSONDecodeError, TypeError):
                pass
        
        return data


class ExportReceiptsSerializer(serializers.Serializer):
    """Serializer for receipts export request"""
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    format = serializers.ChoiceField(choices=['csv', 'excel', 'pdf', 'json'], default='csv')
    include_fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=['receipt_number', 'date', 'student', 'amount', 'status']
    )
    
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if end_date < start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        return data


class ExportPaymentsSerializer(serializers.Serializer):
    """Serializer for payments export request"""
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    format = serializers.ChoiceField(choices=['csv', 'excel', 'pdf', 'json'], default='csv')
    category = serializers.CharField(required=False)
    
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if end_date < start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        return data


class ExportDebtsSerializer(serializers.Serializer):
    """Serializer for debts export request"""
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        required=False
    )
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        required=False
    )
    format = serializers.ChoiceField(choices=['csv', 'excel', 'pdf', 'json'], default='csv')
    include_overdue_only = serializers.BooleanField(default=False)
    
    def validate(self, data):
        if not data.get('term_id') and not data.get('academic_year_id'):
            raise serializers.ValidationError(
                'Either term_id or academic_year_id is required.'
            )
        return data


# ==================== IMPORT SERIALIZERS ====================

class ImportFeeStructureSerializer(serializers.Serializer):
    """Serializer for fee structure import"""
    file = serializers.FileField(required=True)
    file_type = serializers.ChoiceField(choices=['csv', 'excel'], default='csv')
    overwrite_existing = serializers.BooleanField(default=False)
    
    def validate_file(self, value):
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError('File size must be less than 5MB.')
        
        # Validate file extension
        valid_extensions = ['.csv', '.xlsx', '.xls']
        import os
        ext = os.path.splitext(value.name)[1]
        if ext.lower() not in valid_extensions:
            raise serializers.ValidationError(f'Unsupported file format. Valid formats: {", ".join(valid_extensions)}')
        
        return value


class ImportStudentFinanceSerializer(serializers.Serializer):
    """Serializer for student finance data import"""
    file = serializers.FileField(required=True)
    file_type = serializers.ChoiceField(choices=['csv', 'excel'], default='csv')
    import_type = serializers.ChoiceField(
        choices=['receipts', 'payments', 'debts', 'all'],
        default='receipts'
    )
    
    def validate_file(self, value):
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError('File size must be less than 10MB.')
        
        return value


# ==================== WEBHOOK SERIALIZERS ====================

class MpesaWebhookSerializer(serializers.Serializer):
    """Serializer for M-Pesa webhook data"""
    transaction_id = serializers.CharField(max_length=100, required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    phone_number = serializers.CharField(max_length=20, required=True)
    reference = serializers.CharField(max_length=100, required=False)
    timestamp = serializers.DateTimeField(required=True)
    result_code = serializers.IntegerField(required=True)
    result_desc = serializers.CharField(max_length=255, required=True)


class BankWebhookSerializer(serializers.Serializer):
    """Serializer for bank webhook data"""
    transaction_id = serializers.CharField(max_length=100, required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    account_number = serializers.CharField(max_length=50, required=True)
    reference = serializers.CharField(max_length=100, required=False)
    bank_name = serializers.CharField(max_length=100, required=True)
    transaction_date = serializers.DateField(required=True)


# ==================== UTILITY SERIALIZERS ====================

class ReceiptNumberGeneratorSerializer(serializers.Serializer):
    """Serializer for receipt number generation request"""
    prefix = serializers.CharField(max_length=10, required=False, default='RC')
    date = serializers.DateField(required=False, default=timezone.now)


class PaymentNumberGeneratorSerializer(serializers.Serializer):
    """Serializer for payment number generation request"""
    prefix = serializers.CharField(max_length=10, required=False, default='PM')
    date = serializers.DateField(required=False, default=timezone.now)


# ==================== SUMMARY SERIALIZERS ====================

class FinancialPeriodSummarySerializer(serializers.Serializer):
    """Serializer for financial period summary"""
    period = serializers.CharField()
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    fee_collection_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    outstanding_debt = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Breakdown
    income_by_category = serializers.DictField(
        child=serializers.DecimalField(max_digits=12, decimal_places=2)
    )
    expenses_by_category = serializers.DictField(
        child=serializers.DecimalField(max_digits=12, decimal_places=2)
    )
    
    # Trends
    daily_trends = serializers.ListField(
        child=serializers.DictField()
    )


class DebtAnalyticsSerializer(serializers.Serializer):
    """Serializer for debt analytics"""
    total_debtors = serializers.IntegerField()
    total_debt_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_debt_per_student = serializers.DecimalField(max_digits=10, decimal_places=2)
    collection_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    overdue_debts = serializers.IntegerField()
    overdue_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Class-wise breakdown
    class_breakdown = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Curriculum-wise breakdown
    curriculum_breakdown = serializers.DictField(
        child=serializers.DecimalField(max_digits=12, decimal_places=2)
    )