# finance/models.py
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from decimal import Decimal, ROUND_HALF_UP
import uuid
import logging
from datetime import timedelta

# Use your existing models
from accounts.models import User
from administration.models import School
from academics.models import Class, AcademicYear, AcademicTerm

logger = logging.getLogger(__name__)


class BaseFinancialModel(models.Model):
    """Abstract base model for all financial models"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

    def clean(self):
        """Base validation for all financial models"""
        pass


# ==================== ENUMS AND CHOICES ====================
class PaymentStatus(models.TextChoices):
    PENDING = "Pending", "Pending"
    COMPLETED = "Completed", "Completed"
    CANCELLED = "Cancelled", "Cancelled"
    FAILED = "Failed", "Failed"
    REFUNDED = "Refunded", "Refunded"
    PARTIALLY_PAID = "Partially Paid", "Partially Paid"


class KenyaPaymentMethod(models.TextChoices):
    """Kenya-specific payment methods"""
    MPESA = "M-Pesa", "M-Pesa"
    AIRTEL_MONEY = "Airtel Money", "Airtel Money"
    T_KASH = "T-Kash", "T-Kash"
    BANK_TRANSFER = "Bank Transfer", "Bank Transfer"
    CRDB = "CRDB", "CRDB"
    NMB = "NMB", "NMB"
    EQUITY = "Equity", "Equity"
    KCB = "KCB", "KCB"
    COOPERATIVE = "Cooperative Bank", "Cooperative Bank"
    CASH = "Cash", "Cash"
    CHEQUE = "Cheque", "Cheque"
    HATI_MALIPO = "Hati Malipo", "Hati Malipo"
    OTHER = "Other", "Other"


class FeeCategory(models.TextChoices):
    TUITION = "tuition", "Tuition Fees"
    ACTIVITY = "activity", "Activity Fees"
    EXAMINATION = "examination", "Examination Fees"
    BOARDING = "boarding", "Boarding Fees"
    TRANSPORT = "transport", "Transport Fees"
    MEDICAL = "medical", "Medical Fees"
    DEVELOPMENT = "development", "Development Fees"
    CAUTION = "caution", "Caution Money"
    UNIFORM = "uniform", "Uniform Fees"
    LIBRARY = "library", "Library Fees"
    OTHER = "other", "Other Fees"


# ==================== ALLOCATION MODELS ====================
class ReceiptAllocation(BaseFinancialModel):
    """What the receipt is for (e.g., Tuition, Activity Fee, etc.)"""
    name = models.CharField(max_length=255)
    abbr = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Kenya education system categories
    category = models.CharField(
        max_length=50,
        choices=FeeCategory.choices,
        default=FeeCategory.TUITION
    )
    
    # Financial tracking
    default_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Default amount for this allocation"
    )
    is_optional = models.BooleanField(
        default=False,
        help_text="Whether this fee is optional for students"
    )
    applies_to_boarding = models.BooleanField(
        default=False,
        help_text="Whether this fee applies to boarding students only"
    )
    applies_to_day_scholars = models.BooleanField(
        default=True,
        help_text="Whether this fee applies to day scholars"
    )

    class Meta:
        ordering = ['category', 'name']
        verbose_name = "Receipt Allocation"
        verbose_name_plural = "Receipt Allocations"
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def clean(self):
        if self.default_amount < 0:
            raise ValidationError({"default_amount": "Default amount cannot be negative."})


class PaymentAllocation(BaseFinancialModel):
    """What the payment is for (e.g., Salary, Supplies, etc.)"""
    name = models.CharField(max_length=255)
    abbr = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # School expenditure categories
    category = models.CharField(
        max_length=50,
        choices=[
            ('salary', 'Salaries & Wages'),
            ('supplies', 'Teaching Supplies'),
            ('maintenance', 'Maintenance'),
            ('utilities', 'Utilities'),
            ('transport', 'Transport'),
            ('development', 'Development'),
            ('security', 'Security Services'),
            ('insurance', 'Insurance'),
            ('taxes', 'Taxes & Levies'),
            ('other', 'Other Expenses'),
        ],
        default='other'
    )
    
    # Budget tracking
    has_budget_limit = models.BooleanField(default=False)
    annual_budget = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Annual budget limit for this allocation"
    )

    class Meta:
        ordering = ['category', 'name']
        verbose_name = "Payment Allocation"
        verbose_name_plural = "Payment Allocations"
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return self.name

    @property
    def spent_this_year(self):
        """Calculate total spent this academic year"""
        current_year = AcademicYear.get_current_year()
        if current_year:
            payments = Payment.objects.filter(
                paid_for=self,
                status=PaymentStatus.COMPLETED,
                date__range=[current_year.start_date, current_year.end_date]
            )
            return payments.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        return Decimal('0.00')

    @property
    def budget_utilization(self):
        """Calculate budget utilization percentage"""
        if self.has_budget_limit and self.annual_budget:
            spent = self.spent_this_year
            return (spent / self.annual_budget * 100).quantize(Decimal('0.01'))
        return Decimal('0.00')


# ==================== FEE STRUCTURE ENHANCEMENTS ====================
class FeeStructure(BaseFinancialModel):
    """Enhanced Kenya school fee structure with CBC and 8-4-4 support"""
    name = models.CharField(max_length=255, help_text="e.g., AcademicTerm 1 Fees 2024")
    curriculum = models.CharField(
        max_length=20,
        choices=[
            ('cbc', 'CBC'),
            ('8-4-4', '8-4-4'),
            ('igcse', 'IGCSE'),
            ('ib', 'International Baccalaureate'),
        ],
        default='cbc'
    )
    grade_level = models.CharField(
        max_length=20,
        choices=[
            # CBC Levels
            ('pre_primary_1', 'Pre-Primary 1 (PP1)'),
            ('pre_primary_2', 'Pre-Primary 2 (PP2)'),
            ('grade_1', 'Grade 1'),
            ('grade_2', 'Grade 2'),
            ('grade_3', 'Grade 3'),
            ('grade_4', 'Grade 4'),
            ('grade_5', 'Grade 5'),
            ('grade_6', 'Grade 6'),
            ('grade_7', 'Grade 7'),
            ('grade_8', 'Grade 8'),
            ('grade_9', 'Grade 9'),
            ('grade_10', 'Grade 10'),
            ('grade_11', 'Grade 11'),
            ('grade_12', 'Grade 12'),
            # 8-4-4 Levels
            ('class_1', 'Class 1'),
            ('class_2', 'Class 2'),
            ('class_3', 'Class 3'),
            ('class_4', 'Class 4'),
            ('class_5', 'Class 5'),
            ('class_6', 'Class 6'),
            ('class_7', 'Class 7'),
            ('class_8', 'Class 8'),
            ('form_1', 'Form 1'),
            ('form_2', 'Form 2'),
            ('form_3', 'Form 3'),
            ('form_4', 'Form 4'),
        ]
    )
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    
    # Enhanced fee components with categories
    fee_components = models.JSONField(
        default=dict,
        help_text="Structured fee components by category"
    )
    
    # Payment plans
    installment_allowed = models.BooleanField(default=False)
    max_installments = models.PositiveIntegerField(default=1)
    installment_due_dates = models.JSONField(
        default=list,
        blank=True,
        help_text="List of due dates for installments"
    )
    
    # Enhanced discount system
    early_payment_discount = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Discount percentage for early payment"
    )
    early_payment_deadline = models.DateField(null=True, blank=True)
    sibling_discount = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Discount percentage for siblings"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField(default=timezone.now)
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('curriculum', 'grade_level', 'term')
        ordering = ['curriculum', 'grade_level', 'term']
        verbose_name = "Fee Structure"
        verbose_name_plural = "Fee Structures"
        indexes = [
            models.Index(fields=['curriculum', 'grade_level', 'is_active']),
            models.Index(fields=['effective_from', 'effective_to']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_grade_level_display()} ({self.term})"

    def initialize_fee_components(self):
        """Initialize fee components with default structure"""
        if not self.fee_components:
            self.fee_components = {
                'tuition': {'amount': Decimal('0.00'), 'required': True},
                'activity': {'amount': Decimal('0.00'), 'required': True},
                'examination': {'amount': Decimal('0.00'), 'required': True},
                'boarding': {'amount': Decimal('0.00'), 'required': False},
                'transport': {'amount': Decimal('0.00'), 'required': False},
                'medical': {'amount': Decimal('0.00'), 'required': True},
                'development': {'amount': Decimal('0.00'), 'required': True},
                'caution': {'amount': Decimal('0.00'), 'required': False},
                'uniform': {'amount': Decimal('0.00'), 'required': False},
                'library': {'amount': Decimal('0.00'), 'required': False},
            }
    
    def save(self, *args, **kwargs):
        self.initialize_fee_components()
        super().save(*args, **kwargs)

    @property
    def total_fees(self):
        """Calculate total fees for this structure"""
        total = Decimal('0.00')
        for component, details in self.fee_components.items():
            total += Decimal(str(details.get('amount', 0)))
        return total.quantize(Decimal('0.01'))

    @property
    def mandatory_fees(self):
        """Calculate mandatory fees only"""
        total = Decimal('0.00')
        for component, details in self.fee_components.items():
            if details.get('required', False):
                total += Decimal(str(details.get('amount', 0)))
        return total.quantize(Decimal('0.01'))

    def get_component_amount(self, category):
        """Get amount for a specific fee component"""
        return Decimal(str(self.fee_components.get(category, {}).get('amount', 0)))

    def set_component_amount(self, category, amount, required=True):
        """Set amount for a specific fee component"""
        if category not in self.fee_components:
            self.fee_components[category] = {}
        self.fee_components[category]['amount'] = float(amount)
        self.fee_components[category]['required'] = required
        self.save()

    def clean(self):
        if self.effective_to and self.effective_from > self.effective_to:
            raise ValidationError("Effective to date must be after effective from date")
        
        if self.installment_allowed and self.max_installments < 2:
            raise ValidationError("Maximum installments must be at least 2 when installments are allowed")


# ==================== ENHANCED DEBT MANAGEMENT ====================
class DebtRecord(BaseFinancialModel):
    """Enhanced debt record with Kenya school system features"""
    student = models.ForeignKey(
        User, 
        related_name="debt_records", 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(
        FeeStructure, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Enhanced financial details
    original_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal("0.00")
    )
    amount_paid = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal("0.00")
    )
    discounts_applied = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal("0.00")
    )
    late_penalty_applied = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal("0.00")
    )
    
    # Installment tracking
    is_installment_plan = models.BooleanField(default=False)
    current_installment = models.PositiveIntegerField(default=1)
    total_installments = models.PositiveIntegerField(default=1)
    installment_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal("0.00")
    )
    
    # Payment tracking
    due_date = models.DateField(null=True, blank=True)
    is_overdue = models.BooleanField(default=False)
    overdue_days = models.IntegerField(default=0)
    next_installment_due = models.DateField(null=True, blank=True)
    
    # Enhanced notes and status
    payment_plan = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured payment plan details"
    )
    is_reversed = models.BooleanField(default=False)
    reversed_on = models.DateTimeField(null=True, blank=True)
    reversed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reversed_debts'
    )
    
    # Kenya-specific fields
    requires_parent_meeting = models.BooleanField(default=False)
    sent_reminder_sms = models.BooleanField(default=False)
    sent_reminder_email = models.BooleanField(default=False)
    last_reminder_sent = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "term")
        ordering = ["-created_at"]
        verbose_name = "Debt Record"
        verbose_name_plural = "Debt Records"
        indexes = [
            models.Index(fields=['student', 'term', 'is_overdue']),
            models.Index(fields=['due_date', 'is_overdue']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.term.name} - Balance: {self.balance}"

    @property
    def balance(self):
        """Calculate current balance including penalties and discounts"""
        total_debt = self.original_amount + self.late_penalty_applied - self.discounts_applied
        return max(Decimal("0.00"), total_debt - self.amount_paid)

    @property
    def amount_added(self):
        """Backward compatibility"""
        return self.original_amount

    @property
    def paid_percentage(self):
        """Calculate percentage of debt paid"""
        if self.original_amount > 0:
            return (self.amount_paid / self.original_amount * 100).quantize(Decimal('0.01'))
        return Decimal('0.00')

    def apply_payment(self, amount, payment_date=None):
        """
        Enhanced payment application with installment tracking
        """
        amount = Decimal(amount)
        if amount <= 0:
            raise ValidationError("Payment amount must be positive.")
        
        if self.balance < amount:
            raise ValidationError("Cannot pay more than the remaining balance.")
        
        self.amount_paid += amount
        
        # Update installment tracking
        if self.is_installment_plan:
            self.update_installment_progress()
        
        self.save()
        
        logger.info(f"Payment of {amount} applied to debt record {self.id}")

    def apply_discount(self, discount_type, amount, reason=""):
        """Apply discount to debt"""
        if discount_type == 'early_payment':
            if self.fee_structure and self.fee_structure.early_payment_discount > 0:
                discount = (self.original_amount * self.fee_structure.early_payment_discount / 100)
                self.discounts_applied += discount
        elif discount_type == 'sibling':
            if self.fee_structure and self.fee_structure.sibling_discount > 0:
                discount = (self.original_amount * self.fee_structure.sibling_discount / 100)
                self.discounts_applied += discount
        else:
            self.discounts_applied += amount
        
        self.save()
        logger.info(f"Discount of {amount} applied to debt record {self.id}")

    def setup_installment_plan(self, installments, due_dates):
        """Setup installment payment plan"""
        if not self.fee_structure or not self.fee_structure.installment_allowed:
            raise ValidationError("Installment plan not allowed for this fee structure")
        
        if installments < 2 or installments > self.fee_structure.max_installments:
            raise ValidationError(f"Installments must be between 2 and {self.fee_structure.max_installments}")
        
        self.is_installment_plan = True
        self.total_installments = installments
        self.current_installment = 1
        self.installment_amount = (self.original_amount / installments).quantize(Decimal('0.01'))
        
        # Setup payment plan
        self.payment_plan = {
            'total_installments': installments,
            'installment_amount': str(self.installment_amount),
            'due_dates': due_dates,
            'paid_installments': [],
            'remaining_installments': list(range(1, installments + 1))
        }
        
        if due_dates and len(due_dates) >= 1:
            self.next_installment_due = due_dates[0]
        
        self.save()

    def update_installment_progress(self):
        """Update installment progress based on payments"""
        if not self.is_installment_plan:
            return
        
        paid_installments = int(self.amount_paid / self.installment_amount)
        self.current_installment = min(paid_installments + 1, self.total_installments)
        
        # Update next due date
        if self.payment_plan.get('due_dates') and paid_installments < len(self.payment_plan['due_dates']):
            self.next_installment_due = self.payment_plan['due_dates'][paid_installments]

    # ... rest of the enhanced methods (apply_late_penalty, reverse, send_reminder, etc.)


# ==================== ENHANCED TRANSACTION MODELS ====================
class Receipt(BaseFinancialModel):
    """Enhanced receipt model with Kenya-specific features"""
    receipt_number = models.CharField(
        max_length=20, 
        unique=True, 
        db_index=True,
        help_text="Auto-generated receipt number"
    )
    date = models.DateField(default=timezone.now)
    payer_name = models.CharField(max_length=255, verbose_name="Payer's Name")
    payer_phone = models.CharField(
        max_length=13, 
        blank=True, 
        null=True,
        help_text="Payer's phone number for M-Pesa"
    )
    payer_email = models.EmailField(blank=True, null=True)
    
    # Enhanced student association
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='receipts',
        limit_choices_to={'role': 'student'}
    )
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(
        AcademicYear, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Enhanced payment details
    paid_for = models.ForeignKey(
        ReceiptAllocation, 
        on_delete=models.PROTECT,
        verbose_name="Payment Purpose"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_through = models.CharField(
        max_length=20, 
        choices=KenyaPaymentMethod.choices, 
        default=KenyaPaymentMethod.CASH
    )
    
    # Enhanced M-Pesa specific fields
    mpesa_transaction_id = models.CharField(max_length=50, blank=True, null=True)
    mpesa_confirmation_code = models.CharField(max_length=50, blank=True, null=True)
    mpesa_phone_number = models.CharField(max_length=13, blank=True, null=True)
    mpesa_transaction_time = models.DateTimeField(null=True, blank=True)
    
    # Enhanced bank transfer fields
    bank_reference = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Enhanced status and tracking
    status = models.CharField(
        max_length=20, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )
    received_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='issued_receipts'
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_receipts'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Enhanced additional information
    notes = models.TextField(blank=True, null=True)
    is_printed = models.BooleanField(default=False)
    printed_at = models.DateTimeField(null=True, blank=True)
    printed_count = models.PositiveIntegerField(default=0)
    
    # Reconciliation fields
    is_reconciled = models.BooleanField(default=False)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    reconciled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reconciled_receipts'
    )

    class Meta:
        ordering = ['-date', '-receipt_number']
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"
        indexes = [
            models.Index(fields=['receipt_number', 'status']),
            models.Index(fields=['student', 'term']),
            models.Index(fields=['paid_through', 'status']),
            models.Index(fields=['date', 'status']),
        ]

    def __str__(self):
        return f"Receipt #{self.receipt_number} - {self.payer_name} - {self.amount}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError({"amount": "Amount must be a positive value."})
        
        if self.paid_through == KenyaPaymentMethod.MPESA and not self.mpesa_transaction_id:
            raise ValidationError({
                "mpesa_transaction_id": "M-Pesa transaction ID is required for M-Pesa payments."
            })
        
        # Validate academic year consistency
        if self.academic_year and self.term:
            if self.term.academic_year != self.academic_year:
                raise ValidationError({
                    "academic_year": "Academic year must match the term's academic year."
                })

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        
        # Set academic year from term if not provided
        if not self.academic_year and self.term:
            self.academic_year = self.term.academic_year
        
        is_new = self._state.adding
        
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            # Auto-create payment record if status is completed
            if is_new and self.status == PaymentStatus.COMPLETED:
                self.create_payment_record()

    def generate_receipt_number(self):
        """Generate unique receipt number with school prefix"""
        prefix = "DELVOK"
        year = timezone.now().strftime('%Y')
        
        with transaction.atomic():
            last_receipt = Receipt.objects.select_for_update().filter(
                receipt_number__startswith=f"{prefix}{year}"
            ).order_by('-receipt_number').first()
            
            if last_receipt:
                try:
                    last_number = int(last_receipt.receipt_number.replace(f"{prefix}{year}", ""))
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
                
            return f"{prefix}{year}{new_number:06d}"

    def mark_printed(self):
        """Mark receipt as printed and increment print count"""
        self.is_printed = True
        self.printed_at = timezone.now()
        self.printed_count += 1
        self.save()

# ==================== PAYMENT MODELS ====================
class Payment(BaseFinancialModel):
    """Enhanced payment/expense model for school expenditures"""
    payment_number = models.CharField(
        max_length=20, 
        unique=True, 
        db_index=True,
        help_text="Auto-generated payment number"
    )
    date = models.DateField(default=timezone.now)
    description = models.TextField()
    
    # Enhanced payment details
    paid_to = models.CharField(max_length=255, verbose_name="Paid To")
    paid_to_phone = models.CharField(max_length=13, blank=True, null=True)
    paid_to_email = models.EmailField(blank=True, null=True)
    
    # Allocation and category
    allocation = models.ForeignKey(
        PaymentAllocation, 
        on_delete=models.PROTECT,
        related_name='payments'
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ('salary', 'Salaries & Wages'),
            ('supplies', 'Teaching Supplies'),
            ('maintenance', 'Maintenance'),
            ('utilities', 'Utilities'),
            ('transport', 'Transport'),
            ('development', 'Development'),
            ('security', 'Security Services'),
            ('insurance', 'Insurance'),
            ('taxes', 'Taxes & Levies'),
            ('other', 'Other Expenses'),
        ]
    )
    
    # Enhanced financial details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Tax/VAT amount"
    )
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Amount including tax"
    )
    
    # Payment method details
    payment_method = models.CharField(
        max_length=20, 
        choices=KenyaPaymentMethod.choices, 
        default=KenyaPaymentMethod.BANK_TRANSFER
    )
    
    # Bank transfer details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # M-Pesa details
    mpesa_transaction_id = models.CharField(max_length=50, blank=True, null=True)
    mpesa_confirmation_code = models.CharField(max_length=50, blank=True, null=True)
    
    # Cheque details
    cheque_number = models.CharField(max_length=50, blank=True, null=True)
    cheque_date = models.DateField(blank=True, null=True)
    
    # Enhanced status and approval workflow
    status = models.CharField(
        max_length=20, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_payments'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Authorization and verification
    authorized_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authorized_payments'
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Enhanced tracking
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='submitted_payments'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Supporting documents
    supporting_documents = models.JSONField(
        default=list,
        blank=True,
        help_text="List of document URLs or references"
    )
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Reconciliation
    is_reconciled = models.BooleanField(default=False)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    
    # Enhanced notes
    notes = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date', '-payment_number']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        indexes = [
            models.Index(fields=['payment_number', 'status']),
            models.Index(fields=['allocation', 'category']),
            models.Index(fields=['date', 'status']),
            models.Index(fields=['paid_to']),
        ]

    def __str__(self):
        return f"Payment #{self.payment_number} - {self.paid_to} - {self.total_amount}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError({"amount": "Amount must be a positive value."})
        
        if self.tax_amount < 0:
            raise ValidationError({"tax_amount": "Tax amount cannot be negative."})
        
        # Calculate total amount
        self.total_amount = self.amount + self.tax_amount
        
        # Validate payment method specific fields
        if self.payment_method == KenyaPaymentMethod.MPESA:
            if not self.mpesa_transaction_id:
                raise ValidationError({
                    "mpesa_transaction_id": "M-Pesa transaction ID is required."
                })
        elif self.payment_method == KenyaPaymentMethod.CHEQUE:
            if not self.cheque_number:
                raise ValidationError({
                    "cheque_number": "Cheque number is required for cheque payments."
                })

    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = self.generate_payment_number()
        
        is_new = self._state.adding
        
        with transaction.atomic():
            self.clean()
            super().save(*args, **kwargs)

    def generate_payment_number(self):
        """Generate unique payment number"""
        prefix = "PAY"
        year = timezone.now().strftime('%Y')
        
        with transaction.atomic():
            last_payment = Payment.objects.select_for_update().filter(
                payment_number__startswith=f"{prefix}{year}"
            ).order_by('-payment_number').first()
            
            if last_payment:
                try:
                    last_number = int(last_payment.payment_number.replace(f"{prefix}{year}", ""))
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
                
            return f"{prefix}{year}{new_number:06d}"

    def approve(self, approver, notes=""):
        """Approve payment"""
        if self.status != PaymentStatus.PENDING:
            raise ValidationError("Only pending payments can be approved.")
        
        self.status = PaymentStatus.COMPLETED
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.notes = f"{self.notes}\nApproved by {approver.get_full_name()}: {notes}"
        self.save()
        
        logger.info(f"Payment {self.payment_number} approved by {approver.get_full_name()}")

    def mark_as_paid(self, verified_by=None):
        """Mark payment as paid/complete"""
        self.status = PaymentStatus.COMPLETED
        if verified_by:
            self.verified_by = verified_by
            self.verified_at = timezone.now()
        self.save()


class PaymentRecord(BaseFinancialModel):
    """Enhanced payment record linking payments to debts/receipts"""
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='payment_record'
    )
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_records'
    )
    debt_record = models.ForeignKey(
        DebtRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_records'
    )
    
    # Enhanced allocation details
    allocated_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Amount allocated to this specific allocation"
    )
    allocation_category = models.ForeignKey(
        ReceiptAllocation,
        on_delete=models.PROTECT,
        related_name='payment_records'
    )
    
    # Enhanced tracking
    allocation_date = models.DateField(default=timezone.now)
    allocated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='allocated_payments'
    )
    
    # Status
    is_reversed = models.BooleanField(default=False)
    reversed_on = models.DateTimeField(null=True, blank=True)
    reversed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reversed_payment_records'
    )
    
    # Reconciliation
    is_reconciled = models.BooleanField(default=False)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-allocation_date']
        verbose_name = "Payment Record"
        verbose_name_plural = "Payment Records"
        indexes = [
            models.Index(fields=['receipt', 'debt_record']),
            models.Index(fields=['allocation_category', 'allocation_date']),
        ]

    def __str__(self):
        return f"Payment Record - {self.payment.payment_number} - {self.allocated_amount}"


# ==================== ENHANCED FINANCIAL REPORTS ====================
class FinancialReport(BaseFinancialModel):
    """Enhanced financial reports with multiple report types"""
    REPORT_TYPES = (
        ('daily', 'Daily Collection'),
        ('weekly', 'Weekly Collection'),
        ('monthly', 'Monthly Financial'),
        ('termly', 'AcademicTerm Financial'),
        ('annual', 'Annual Financial'),
        ('fee_collection', 'Fee Collection'),
        ('expenditure', 'Expenditure'),
        ('profit_loss', 'Profit & Loss'),
        ('balance_sheet', 'Balance Sheet'),
        ('cash_flow', 'Cash Flow'),
    )
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Period covered
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Report data (store computed data for quick access)
    report_data = models.JSONField(
        default=dict,
        help_text="Computed report data in structured format"
    )
    
    # Summary statistics
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    net_profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Generated by
    generated_by = models.ForeignKey(User, on_delete=models.PROTECT)
    generated_at = models.DateTimeField(default=timezone.now)
    
    # Approval
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_reports'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Export details
    exported_formats = models.JSONField(
        default=list,
        blank=True,
        help_text="List of exported formats (PDF, Excel, etc.)"
    )
    last_exported = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-period_end', '-generated_at']
        verbose_name = "Financial Report"
        verbose_name_plural = "Financial Reports"
        indexes = [
            models.Index(fields=['report_type', 'period_start']),
            models.Index(fields=['generated_at', 'is_approved']),
        ]

    def __str__(self):
        return f"{self.title} - {self.period_start} to {self.period_end}"

    def generate_report_data(self):
        """Generate comprehensive report data"""
        # This method would compute and populate report_data
        # Implementation depends on report type
        pass

    def calculate_summary(self):
        """Calculate summary statistics"""
        # This would calculate based on report_data
        pass


class Budget(BaseFinancialModel):
    """Enhanced budget model for school financial planning"""
    name = models.CharField(max_length=255)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE, null=True, blank=True)
    
    # Budget categories
    budget_items = models.JSONField(
        default=list,
        help_text="Structured budget items with categories and amounts"
    )
    
    # Enhanced budget details
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    actual_spent = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Status
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_budgets'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Monitoring
    variance_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Percentage variance between budget and actual"
    )
    is_on_track = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['academic_year', 'term']
        verbose_name = "Budget"
        verbose_name_plural = "Budgets"
        indexes = [
            models.Index(fields=['academic_year', 'is_approved']),
        ]

    def __str__(self):
        term_str = f" - {self.term.name}" if self.term else ""
        return f"{self.name} - {self.academic_year.name}{term_str}"

    def calculate_totals(self):
        """Calculate budget totals"""
        total = Decimal('0.00')
        for item in self.budget_items:
            total += Decimal(str(item.get('amount', 0)))
        self.total_budget = total
        self.save()

    def update_actual_spent(self):
        """Update actual spent amount based on payments"""
        if self.term:
            payments = Payment.objects.filter(
                date__gte=self.term.start_date,
                date__lte=self.term.end_date,
                status=PaymentStatus.COMPLETED
            )
        else:
            payments = Payment.objects.filter(
                date__gte=self.academic_year.start_date,
                date__lte=self.academic_year.end_date,
                status=PaymentStatus.COMPLETED
            )
        
        self.actual_spent = payments.aggregate(total=models.Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Calculate variance
        if self.total_budget > 0:
            self.variance_percentage = ((self.actual_spent - self.allocated_amount) / self.total_budget * 100).quantize(Decimal('0.01'))
        
        self.is_on_track = self.actual_spent <= self.allocated_amount
        self.save()


# ==================== TAX AND COMPLIANCE MODELS ====================
class TaxConfiguration(BaseFinancialModel):
    """Enhanced tax configuration for Kenya"""
    tax_name = models.CharField(max_length=100, help_text="e.g., VAT, Withholding Tax")
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Tax rate in percentage"
    )
    applies_to = models.CharField(
        max_length=20,
        choices=[
            ('all', 'All Payments'),
            ('receipts', 'Receipts Only'),
            ('payments', 'Payments Only'),
            ('specific', 'Specific Categories'),
        ],
        default='all'
    )
    
    # Kenya-specific tax details
    kra_pin_required = models.BooleanField(default=False)
    tax_code = models.CharField(max_length=50, blank=True, null=True)
    effective_from = models.DateField(default=timezone.now)
    effective_to = models.DateField(null=True, blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    auto_calculate = models.BooleanField(
        default=True,
        help_text="Automatically calculate tax on applicable transactions"
    )
    
    class Meta:
        verbose_name = "Tax Configuration"
        verbose_name_plural = "Tax Configurations"
        ordering = ['tax_name', 'effective_from']

    def __str__(self):
        return f"{self.tax_name} - {self.tax_rate}%"

    def calculate_tax(self, amount):
        """Calculate tax amount for given amount"""
        return (amount * self.tax_rate / 100).quantize(Decimal('0.01'))


class ComplianceRecord(BaseFinancialModel):
    """Enhanced compliance and audit records"""
    record_type = models.CharField(
        max_length=50,
        choices=[
            ('audit', 'Internal Audit'),
            ('tax', 'Tax Filing'),
            ('license', 'License Renewal'),
            ('inspection', 'Regulatory Inspection'),
            ('other', 'Other Compliance'),
        ]
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Compliance period
    due_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('overdue', 'Overdue'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    
    # Responsible parties
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='compliance_responsibilities'
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_compliance'
    )
    
    # Documents and evidence
    supporting_documents = models.JSONField(
        default=list,
        blank=True,
        help_text="List of compliance documents"
    )
    evidence_of_compliance = models.TextField(blank=True)
    
    # Notes and follow-up
    notes = models.TextField(blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    
    # Kenya-specific
    kra_filing = models.BooleanField(default=False)
    kra_reference = models.CharField(max_length=100, blank=True, null=True)
    ministry_registration = models.BooleanField(default=False)
    ministry_reference = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['due_date', 'status']
        verbose_name = "Compliance Record"
        verbose_name_plural = "Compliance Records"

    def __str__(self):
        return f"{self.title} - Due: {self.due_date}"


# ==================== ANALYTICS AND DASHBOARD MODELS ====================
class FinancialDashboard(BaseFinancialModel):
    """Enhanced financial dashboard with real-time metrics"""
    dashboard_date = models.DateField(default=timezone.now)
    
    # Key metrics
    total_receipts_today = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_payments_today = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cash_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Enhanced metrics
    fee_collection_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Percentage of fees collected for current term"
    )
    outstanding_debt = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    pending_approvals = models.IntegerField(default=0)
    
    # AcademicTerm-wise metrics (stored as JSON for flexibility)
    term_metrics = models.JSONField(
        default=dict,
        blank=True,
        help_text="AcademicTerm-wise financial metrics"
    )
    
    # Daily trends
    daily_trends = models.JSONField(
        default=dict,
        blank=True,
        help_text="Last 30 days trend data"
    )
    
    # Generated and refreshed
    generated_at = models.DateTimeField(default=timezone.now)
    last_refreshed = models.DateTimeField(auto_now=True)
    is_current = models.BooleanField(default=True)

    class Meta:
        ordering = ['-dashboard_date']
        verbose_name = "Financial Dashboard"
        verbose_name_plural = "Financial Dashboards"
        indexes = [
            models.Index(fields=['dashboard_date', 'is_current']),
        ]

    def __str__(self):
        return f"Financial Dashboard - {self.dashboard_date}"

    def refresh_metrics(self):
        """Refresh all dashboard metrics"""
        today = timezone.now().date()
        
        # Today's receipts
        today_receipts = Receipt.objects.filter(
            date=today,
            status=PaymentStatus.COMPLETED
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        # Today's payments
        today_payments = Payment.objects.filter(
            date=today,
            status=PaymentStatus.COMPLETED
        ).aggregate(total=models.Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Update metrics
        self.total_receipts_today = today_receipts
        self.total_payments_today = today_payments
        
        # Calculate cash balance (simplified)
        self.cash_balance = today_receipts - today_payments
        
        # Update outstanding debt
        current_term = AcademicTerm.get_current_term()
        if current_term:
            outstanding = DebtRecord.objects.filter(
                term=current_term,
                is_active=True
            ).aggregate(total=models.Sum('balance'))['total'] or Decimal('0.00')
            self.outstanding_debt = outstanding
        
        # Update pending approvals
        self.pending_approvals = Payment.objects.filter(
            requires_approval=True,
            status=PaymentStatus.PENDING
        ).count()
        
        self.save()


# ==================== UTILITY FUNCTIONS ====================
class FinancialUtils:
    """Utility class for financial calculations and operations"""
    
    @staticmethod
    def calculate_discount(original_amount, discount_percentage):
        """Calculate discount amount"""
        return (original_amount * discount_percentage / 100).quantize(Decimal('0.01'))
    
    @staticmethod
    def calculate_late_penalty(original_amount, overdue_days, penalty_rate=0.5):
        """Calculate late payment penalty (0.5% per day by default)"""
        penalty = original_amount * (penalty_rate / 100) * overdue_days
        return penalty.quantize(Decimal('0.01'))
    
    @staticmethod
    def format_currency(amount):
        """Format amount as Kenya Shillings"""
        return f"KSh {amount:,.2f}"
    
    @staticmethod
    def get_financial_year():
        """Get current financial year (July to June)"""
        today = timezone.now().date()
        if today.month >= 7:
            return today.year, today.year + 1
        else:
            return today.year - 1, today.year
    
    @staticmethod
    def generate_report_period(report_type):
        """Generate period dates based on report type"""
        today = timezone.now().date()
        
        if report_type == 'daily':
            start_date = today
            end_date = today
        elif report_type == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif report_type == 'monthly':
            start_date = today.replace(day=1)
            next_month = today.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
        elif report_type == 'termly':
            # Would need to get current term dates
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=3, day=31)
        elif report_type == 'annual':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:
            start_date = today
            end_date = today
        
        return start_date, end_date


class FinancialSettings(models.Model):
    """Financial system settings"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school_name = models.CharField(max_length=200, default='Delvok Academy')
    currency = models.CharField(max_length=3, default='KES')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=16.00)
    late_payment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    late_payment_days = models.IntegerField(default=30)
    installment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)
    
    # M-Pesa settings
    mpesa_shortcode = models.CharField(max_length=10, blank=True)
    mpesa_passkey = models.CharField(max_length=200, blank=True)
    mpesa_callback_url = models.URLField(blank=True)
    
    # Bank details
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_account_name = models.CharField(max_length=200, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    
    # Notification settings
    enable_auto_reminders = models.BooleanField(default=True)
    reminder_days_before = models.IntegerField(default=7)
    enable_late_fees = models.BooleanField(default=True)
    enable_sms_notifications = models.BooleanField(default=True)
    enable_email_notifications = models.BooleanField(default=True)
    
    # Document settings
    receipt_prefix = models.CharField(max_length=10, default='RC')
    payment_prefix = models.CharField(max_length=10, default='PM')
    invoice_prefix = models.CharField(max_length=10, default='INV')
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Financial Settings'
        verbose_name_plural = 'Financial Settings'
    
    def __str__(self):
        return f"Financial Settings - {self.school_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and FinancialSettings.objects.exists():
            # Update existing instance instead of creating new one
            existing = FinancialSettings.objects.first()
            existing.school_name = self.school_name
            existing.currency = self.currency
            existing.tax_rate = self.tax_rate
            existing.late_payment_fee = self.late_payment_fee
            existing.late_payment_days = self.late_payment_days
            existing.installment_fee = self.installment_fee
            existing.mpesa_shortcode = self.mpesa_shortcode
            existing.mpesa_passkey = self.mpesa_passkey
            existing.mpesa_callback_url = self.mpesa_callback_url
            existing.bank_name = self.bank_name
            existing.bank_account_number = self.bank_account_number
            existing.bank_account_name = self.bank_account_name
            existing.bank_branch = self.bank_branch
            existing.enable_auto_reminders = self.enable_auto_reminders
            existing.reminder_days_before = self.reminder_days_before
            existing.enable_late_fees = self.enable_late_fees
            existing.enable_sms_notifications = self.enable_sms_notifications
            existing.enable_email_notifications = self.enable_email_notifications
            existing.receipt_prefix = self.receipt_prefix
            existing.payment_prefix = self.payment_prefix
            existing.invoice_prefix = self.invoice_prefix
            existing.save()
            return existing
        return super().save(*args, **kwargs)

# Add these missing models to your finance/models.py file

# ==================== INSTALLMENT PLAN MODELS ====================
class InstallmentPlan(BaseFinancialModel):
    """Installment payment plans for students"""
    installment_number = models.PositiveIntegerField()
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='installment_plans',
        limit_choices_to={'role': 'student'}
    )
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    debt_record = models.ForeignKey(
        DebtRecord,
        on_delete=models.CASCADE,
        related_name='installment_plans',
        null=True,
        blank=True
    )
    
    # Payment details
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=20,
        choices=KenyaPaymentMethod.choices,
        default=KenyaPaymentMethod.CASH
    )
    reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('overdue', 'Overdue'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['due_date', 'installment_number']
        verbose_name = "Installment Plan"
        verbose_name_plural = "Installment Plans"
        unique_together = ['student', 'term', 'installment_number']
        indexes = [
            models.Index(fields=['student', 'term', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]

    def __str__(self):
        return f"Installment #{self.installment_number} - {self.student.get_full_name()}"

    @property
    def is_overdue(self):
        """Check if installment is overdue"""
        return self.status == 'pending' and self.due_date < timezone.now().date()

    @property
    def balance(self):
        """Calculate remaining balance"""
        return max(Decimal('0.00'), self.amount_due - self.amount_paid)

    def mark_as_paid(self, amount, payment_date=None, payment_method=None, reference=None):
        """Mark installment as paid"""
        if amount > self.balance:
            raise ValidationError("Payment amount exceeds remaining balance.")
        
        self.amount_paid = amount
        self.payment_date = payment_date or timezone.now().date()
        
        if payment_method:
            self.payment_method = payment_method
        
        if reference:
            self.reference = reference
        
        self.status = 'paid' if self.balance == Decimal('0.00') else 'partially_paid'
        self.save()


# ==================== DISCOUNT MODELS ====================
class Discount(BaseFinancialModel):
    """Discounts applied to student fees"""
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='discounts',
        limit_choices_to={'role': 'student'}
    )
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    debt_record = models.ForeignKey(
        DebtRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discounts'
    )
    
    # Discount details
    discount_type = models.CharField(
        max_length=30,
        choices=[
            ('sibling', 'Sibling Discount'),
            ('early_payment', 'Early Payment Discount'),
            ('academic', 'Academic Excellence'),
            ('sports', 'Sports Scholarship'),
            ('need_based', 'Need-based Financial Aid'),
            ('staff', 'Staff Discount'),
            ('promotional', 'Promotional Discount'),
            ('other', 'Other'),
        ],
        default='other'
    )
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    reason = models.TextField()
    
    # Status and approval
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_discounts'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"
        indexes = [
            models.Index(fields=['student', 'term', 'status']),
            models.Index(fields=['discount_type', 'status']),
        ]

    def __str__(self):
        return f"{self.get_discount_type_display()} - {self.student.get_full_name()}"


# ==================== WAIVER MODELS ====================
class Waiver(BaseFinancialModel):
    """Fee waivers for students"""
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='waivers',
        limit_choices_to={'role': 'student'}
    )
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    debt_record = models.ForeignKey(
        DebtRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='waivers'
    )
    
    # Waiver details
    waiver_type = models.CharField(
        max_length=30,
        choices=[
            ('full', 'Full Waiver'),
            ('partial', 'Partial Waiver'),
            ('temporary', 'Temporary Waiver'),
            ('scholarship', 'Scholarship'),
            ('bursary', 'Bursary'),
            ('other', 'Other'),
        ],
        default='partial'
    )
    waiver_amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    supporting_documents = models.JSONField(
        default=list,
        blank=True,
        help_text="List of supporting document references"
    )
    
    # Status and approval
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_waivers'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Waiver"
        verbose_name_plural = "Waivers"
        indexes = [
            models.Index(fields=['student', 'term', 'status']),
            models.Index(fields=['waiver_type', 'status']),
        ]

    def __str__(self):
        return f"{self.get_waiver_type_display()} - {self.student.get_full_name()}"


# ==================== AUDIT LOG MODELS ====================
class FinancialAuditLog(models.Model):
    """Audit log for financial transactions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='financial_audit_logs'
    )
    action = models.CharField(
        max_length=50,
        choices=[
            ('create', 'Create'),
            ('update', 'Update'),
            ('delete', 'Delete'),
            ('approve', 'Approve'),
            ('reject', 'Reject'),
            ('verify', 'Verify'),
            ('reconcile', 'Reconcile'),
            ('reverse', 'Reverse'),
        ]
    )
    entity_type = models.CharField(
        max_length=50,
        choices=[
            ('receipt', 'Receipt'),
            ('payment', 'Payment'),
            ('debt', 'Debt Record'),
            ('fee_structure', 'Fee Structure'),
            ('budget', 'Budget'),
            ('discount', 'Discount'),
            ('waiver', 'Waiver'),
            ('installment', 'Installment Plan'),
        ]
    )
    entity_id = models.UUIDField()
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Financial Audit Log"
        verbose_name_plural = "Financial Audit Logs"
        indexes = [
            models.Index(fields=['timestamp', 'action']),
            models.Index(fields=['user', 'entity_type']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} {self.get_entity_type_display()} - {self.timestamp}"

    @classmethod
    def log_action(cls, user, action, entity_type, entity_id, old_value=None, new_value=None, request=None):
        """Helper method to create audit log entries"""
        import json
        
        if old_value is not None and not isinstance(old_value, str):
            try:
                old_value = json.dumps(old_value, default=str)
            except (TypeError, ValueError):
                old_value = str(old_value)
        
        if new_value is not None and not isinstance(new_value, str):
            try:
                new_value = json.dumps(new_value, default=str)
            except (TypeError, ValueError):
                new_value = str(new_value)
        
        log_entry = cls.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT') if request else None
        )
        
        return log_entry


# ==================== BUDGET MODELS (enhanced) ====================

class BudgetItem(models.Model):
    """Individual budget items for detailed tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    budget = models.ForeignKey(
        'Budget',
        on_delete=models.CASCADE,
        related_name='items'
    )
    category = models.CharField(max_length=100)
    description = models.TextField()
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2)
    actual_spent = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    variance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category']
        verbose_name = "Budget Item"
        verbose_name_plural = "Budget Items"

    def __str__(self):
        return f"{self.category} - {self.description}"

    def calculate_variance(self):
        """Calculate variance between allocated and actual"""
        self.variance = self.actual_spent - self.allocated_amount
        self.save()


# ==================== NOTIFICATION MODELS ====================
class FinancialNotification(BaseFinancialModel):
    """Financial notifications and reminders"""
    NOTIFICATION_TYPES = [
        ('fee_reminder', 'Fee Payment Reminder'),
        ('overdue_alert', 'Overdue Fee Alert'),
        ('receipt_confirmation', 'Receipt Confirmation'),
        ('payment_confirmation', 'Payment Confirmation'),
        ('budget_alert', 'Budget Alert'),
        ('compliance_reminder', 'Compliance Reminder'),
        ('installment_due', 'Installment Due Reminder'),
        ('other', 'Other'),
    ]
    
    CHANNELS = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    ]
    
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='financial_notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNELS)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    sent_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
            ('delivered', 'Delivered'),
            ('read', 'Read'),
        ],
        default='pending'
    )
    entity_type = models.CharField(max_length=50, blank=True, null=True)
    entity_id = models.UUIDField(blank=True, null=True)
    priority = models.PositiveIntegerField(default=1, help_text="1=Low, 2=Medium, 3=High, 4=Urgent")
    retry_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-scheduled_time', 'priority']
        verbose_name = "Financial Notification"
        verbose_name_plural = "Financial Notifications"
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['notification_type', 'scheduled_time']),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.recipient.get_full_name()}"

    def mark_as_sent(self):
        """Mark notification as sent"""
        self.status = 'sent'
        self.sent_time = timezone.now()
        self.save()

    def mark_as_failed(self, error_message):
        """Mark notification as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save()


# ==================== RECONCILIATION MODELS ====================
class BankReconciliation(BaseFinancialModel):
    """Bank account reconciliation records"""
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    statement_date = models.DateField()
    statement_balance = models.DecimalField(max_digits=12, decimal_places=2)
    system_balance = models.DecimalField(max_digits=12, decimal_places=2)
    reconciled_balance = models.DecimalField(max_digits=12, decimal_places=2)
    variance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Reconciliation status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('discrepancy', 'Discrepancy Found'),
        ],
        default='pending'
    )
    
    # Transactions
    matched_transactions = models.JSONField(
        default=list,
        blank=True,
        help_text="List of matched transactions"
    )
    unmatched_transactions = models.JSONField(
        default=list,
        blank=True,
        help_text="List of unmatched transactions"
    )
    
    reconciled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reconciled_bank_statements'
    )
    reconciled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-statement_date']
        verbose_name = "Bank Reconciliation"
        verbose_name_plural = "Bank Reconciliations"
        indexes = [
            models.Index(fields=['bank_name', 'statement_date']),
        ]

    def __str__(self):
        return f"{self.bank_name} - {self.account_number} - {self.statement_date}"

    def calculate_variance(self):
        """Calculate variance between statement and system"""
        self.variance = self.statement_balance - self.reconciled_balance
        self.save()


class MPesaReconciliation(BaseFinancialModel):
    """M-Pesa reconciliation records"""
    business_shortcode = models.CharField(max_length=20)
    transaction_date = models.DateField()
    mpesa_total = models.DecimalField(max_digits=12, decimal_places=2)
    system_total = models.DecimalField(max_digits=12, decimal_places=2)
    reconciled_total = models.DecimalField(max_digits=12, decimal_places=2)
    variance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Transaction details
    mpesa_transactions = models.JSONField(
        default=list,
        blank=True,
        help_text="List of M-Pesa transactions"
    )
    system_transactions = models.JSONField(
        default=list,
        blank=True,
        help_text="List of system transactions"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('matched', 'Matched'),
            ('discrepancy', 'Discrepancy'),
            ('resolved', 'Resolved'),
        ],
        default='pending'
    )
    
    reconciled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reconciled_mpesa_statements'
    )
    reconciled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = "M-Pesa Reconciliation"
        verbose_name_plural = "M-Pesa Reconciliations"
        indexes = [
            models.Index(fields=['business_shortcode', 'transaction_date']),
        ]

    def __str__(self):
        return f"M-Pesa - {self.business_shortcode} - {self.transaction_date}"