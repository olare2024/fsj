from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from .models import (
    FinancialSettings, ReceiptAllocation, PaymentAllocation,
    FeeStructure, DebtRecord, Receipt, Payment, PaymentRecord,
    InstallmentPlan, Discount, Waiver, Budget, FinancialReport
)

from academics.models import AcademicTerm

User = get_user_model()


class FinancialSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialSettings
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'updated_by')


class ReceiptAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptAllocation
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class PaymentAllocationSerializer(serializers.ModelSerializer):
    spent_this_year = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    budget_utilization = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = PaymentAllocation
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class FeeStructureSerializer(serializers.ModelSerializer):
    total_fees = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    mandatory_fees = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    grade_level_name = serializers.CharField(source='grade_level.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    
    class Meta:
        model = FeeStructure
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate(self, data):
        if data.get('effective_to') and data.get('effective_from'):
            if data['effective_from'] > data['effective_to']:
                raise serializers.ValidationError({
                    "effective_to": "Effective to date must be after effective from date"
                })
        
        if data.get('installment_allowed') and data.get('max_installments', 1) < 2:
            raise serializers.ValidationError({
                "max_installments": "Maximum installments must be at least 2 when installments are allowed"
            })
        
        return data


class DebtRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    term_name = serializers.CharField(source='term.name', read_only=True)
    fee_structure_name = serializers.CharField(source='fee_structure.name', read_only=True)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    paid_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = DebtRecord
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'balance', 'paid_percentage')
    
    def get_student_name(self, obj):
        return obj.student.get_full_name()
    
    def validate(self, data):
        # Validate that student is actually a student
        student = data.get('student') or (self.instance.student if self.instance else None)
        if student and student.role != 'student':
            raise serializers.ValidationError({
                "student": "User must have role 'student'"
            })
        
        return data


class ReceiptSerializer(serializers.ModelSerializer):
    receipt_number = serializers.CharField(read_only=True)
    student_name = serializers.SerializerMethodField()
    term_name = serializers.CharField(source='term.name', read_only=True)
    paid_for_name = serializers.CharField(source='paid_for.name', read_only=True)
    received_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Receipt
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'receipt_number', 'academic_year')
    
    def get_student_name(self, obj):
        return obj.student.get_full_name()
    
    def get_received_by_name(self, obj):
        return obj.received_by.get_full_name() if obj.received_by else None
    
    def validate(self, data):
        # Set academic year from term if not provided
        term = data.get('term') or (self.instance.term if self.instance else None)
        if term and not data.get('academic_year'):
            data['academic_year'] = term.academic_year
        
        # Validate M-Pesa details
        if data.get('paid_through') == 'M-Pesa' and not data.get('mpesa_transaction_id'):
            raise serializers.ValidationError({
                "mpesa_transaction_id": "M-Pesa transaction ID is required for M-Pesa payments"
            })
        
        return data
    
    def create(self, validated_data):
        # Auto-generate receipt number
        validated_data['receipt_number'] = Receipt.generate_receipt_number(validated_data)
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    payment_number = serializers.CharField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    submitted_by_name = serializers.SerializerMethodField()
    allocation_name = serializers.CharField(source='allocation.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'payment_number', 
                           'total_amount', 'submitted_at', 'submitted_by')
    
    def get_submitted_by_name(self, obj):
        return obj.submitted_by.get_full_name() if obj.submitted_by else None
    
    def validate(self, data):
        # Calculate total amount
        amount = data.get('amount', 0)
        tax_amount = data.get('tax_amount', 0)
        data['total_amount'] = amount + tax_amount
        
        # Validate payment method specific fields
        payment_method = data.get('payment_method')
        
        if payment_method == 'M-Pesa' and not data.get('mpesa_transaction_id'):
            raise serializers.ValidationError({
                "mpesa_transaction_id": "M-Pesa transaction ID is required for M-Pesa payments"
            })
        
        if payment_method == 'Cheque' and not data.get('cheque_number'):
            raise serializers.ValidationError({
                "cheque_number": "Cheque number is required for cheque payments"
            })
        
        return data
    
    def create(self, validated_data):
        # Set submitted by to current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['submitted_by'] = request.user
        
        # Auto-generate payment number
        validated_data['payment_number'] = Payment.generate_payment_number(validated_data)
        return super().create(validated_data)


class PaymentRecordSerializer(serializers.ModelSerializer):
    payment_number = serializers.CharField(source='payment.payment_number', read_only=True)
    receipt_number = serializers.CharField(source='receipt.receipt_number', read_only=True)
    allocated_by_name = serializers.SerializerMethodField()
    allocation_category_name = serializers.CharField(source='allocation_category.name', read_only=True)
    
    class Meta:
        model = PaymentRecord
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'allocation_date', 'allocated_by')
    
    def get_allocated_by_name(self, obj):
        return obj.allocated_by.get_full_name() if obj.allocated_by else None


class InstallmentPlanSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    term_name = serializers.CharField(source='term.name', read_only=True)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = InstallmentPlan
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'balance', 'is_overdue')
    
    def get_student_name(self, obj):
        return obj.student.get_full_name()
    
    def validate(self, data):
        # Validate installment number uniqueness
        student = data.get('student')
        term = data.get('term')
        installment_number = data.get('installment_number')
        
        if student and term and installment_number:
            existing = InstallmentPlan.objects.filter(
                student=student,
                term=term,
                installment_number=installment_number
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError({
                    "installment_number": "Installment number must be unique for each student and term"
                })
        
        return data


class DiscountSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    term_name = serializers.CharField(source='term.name', read_only=True)
    approved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Discount
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'approved_at')
    
    def get_student_name(self, obj):
        return obj.student.get_full_name()
    
    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None
    
    def validate(self, data):
        # Set default term if not provided
        if not data.get('term'):
            current_term = AcademicTerm.objects.filter(is_current=True, is_active=True).first()
            if current_term:
                data['term'] = current_term
        
        return data


class WaiverSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    term_name = serializers.CharField(source='term.name', read_only=True)
    approved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Waiver
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'approved_at')
    
    def get_student_name(self, obj):
        return obj.student.get_full_name()
    
    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None
    
    def validate(self, data):
        # Set default term if not provided
        if not data.get('term'):
            current_term = AcademicTerm.objects.filter(is_current=True, is_active=True).first()
            if current_term:
                data['term'] = current_term
        
        return data


class BudgetSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    total_budget = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    actual_spent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    variance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    is_on_track = serializers.BooleanField(read_only=True)
    approved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'total_budget', 
                           'actual_spent', 'variance_percentage', 'is_on_track', 
                           'approved_at')
    
    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None
    
    def validate(self, data):
        # Calculate total budget from items
        budget_items = data.get('budget_items', [])
        if budget_items:
            total = Decimal('0.00')
            for item in budget_items:
                total += Decimal(str(item.get('amount', 0)))
            data['total_budget'] = total
        
        return data


class FinancialReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialReport
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'generated_at', 
                           'total_income', 'total_expenses', 'net_profit', 
                           'approved_at')
    
    def get_generated_by_name(self, obj):
        return obj.generated_by.get_full_name() if obj.generated_by else None
    
    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None
    
    def validate(self, data):
        if data.get('period_start') and data.get('period_end'):
            if data['period_start'] > data['period_end']:
                raise serializers.ValidationError({
                    "period_end": "Period end date must be after period start date"
                })
        
        return data
    
    def create(self, validated_data):
        # Set generated by to current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['generated_by'] = request.user
        
        return super().create(validated_data)


# Dashboard Serializers
class FinancialDashboardSerializer(serializers.Serializer):
    """Serializer for financial dashboard data"""
    total_receipts_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_payments_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    cash_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    fee_collection_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    outstanding_debt = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_approvals = serializers.IntegerField()
    recent_receipts = ReceiptSerializer(many=True)
    recent_payments = PaymentSerializer(many=True)
    overdue_debts = DebtRecordSerializer(many=True)


# Report Serializers
class FeeCollectionReportSerializer(serializers.Serializer):
    """Serializer for fee collection report"""
    period = serializers.CharField()
    total_fees = serializers.DecimalField(max_digits=12, decimal_places=2)
    collected_fees = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_fees = serializers.DecimalField(max_digits=12, decimal_places=2)
    collection_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    grade_level_breakdown = serializers.DictField()
    payment_method_breakdown = serializers.DictField()


class ExpenseReportSerializer(serializers.Serializer):
    """Serializer for expense report"""
    period = serializers.CharField()
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    category_breakdown = serializers.DictField()
    allocation_breakdown = serializers.DictField()
    top_expenses = PaymentSerializer(many=True)