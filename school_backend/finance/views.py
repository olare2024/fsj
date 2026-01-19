from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, DjangoModelPermissions
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Max, Min, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse
import csv
import json
from decimal import Decimal

from .models import (
    FinancialSettings, ReceiptAllocation, PaymentAllocation,
    FeeStructure, DebtRecord, Receipt, Payment, PaymentRecord,
    InstallmentPlan, Discount, Waiver, Budget, FinancialReport,
    FinancialAuditLog
)
from .serializers import *
from accounts.models import User
from academics.models import AcademicYear, AcademicTerm, GradeLevel
from academics.serializers import AcademicYearSerializer, AcademicTermSerializer


# ==================== CUSTOM PAGINATION ====================
class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ==================== BASE VIEWSET ====================
class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    def get_queryset(self):
        return self.model.objects.filter(is_active=True)


# ==================== MODEL VIEWSETS ====================
class FinancialSettingsViewSet(BaseViewSet):
    queryset = FinancialSettings.objects.all()
    serializer_class = FinancialSettingsSerializer
    model = FinancialSettings
    
    def get_queryset(self):
        # Only return the first (and only) settings instance
        return FinancialSettings.objects.all()[:1]
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current financial settings"""
        settings = FinancialSettings.objects.first()
        if not settings:
            # Create default settings if none exist
            settings = FinancialSettings.objects.create(
                school_name='Delvok Academy',
                updated_by=request.user
            )
        
        serializer = self.get_serializer(settings)
        return Response(serializer.data)


class ReceiptAllocationViewSet(BaseViewSet):
    queryset = ReceiptAllocation.objects.filter(is_active=True)
    serializer_class = ReceiptAllocationSerializer
    model = ReceiptAllocation
    search_fields = ['name', 'description']
    filterset_fields = ['category', 'is_optional', 'is_active']
    ordering_fields = ['category', 'name']


class PaymentAllocationViewSet(BaseViewSet):
    queryset = PaymentAllocation.objects.filter(is_active=True)
    serializer_class = PaymentAllocationSerializer
    model = PaymentAllocation
    search_fields = ['name', 'description']
    filterset_fields = ['category', 'has_budget_limit', 'is_active']
    ordering_fields = ['category', 'name']


class FeeStructureViewSet(BaseViewSet):
    queryset = FeeStructure.objects.filter(is_active=True)
    serializer_class = FeeStructureSerializer
    model = FeeStructure
    search_fields = ['name', 'grade_level__name']
    filterset_fields = ['curriculum', 'grade_level', 'term', 'is_active']
    ordering_fields = ['grade_level__level', 'term', 'name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        grade_level_id = self.request.query_params.get('grade_level')
        term_id = self.request.query_params.get('term')
        
        if grade_level_id:
            queryset = queryset.filter(grade_level_id=grade_level_id)
        if term_id:
            queryset = queryset.filter(term_id=term_id)
        
        return queryset.select_related('grade_level', 'term')
    
    @action(detail=False, methods=['get'])
    def by_grade_and_term(self, request):
        """Get fee structure for specific grade and term"""
        grade_level_id = request.query_params.get('grade_level')
        term_id = request.query_params.get('term')
        
        if not grade_level_id or not term_id:
            return Response(
                {'error': 'grade_level and term parameters are required'},
                status=400
            )
        
        fee_structure = FeeStructure.objects.filter(
            grade_level_id=grade_level_id,
            term_id=term_id,
            is_active=True
        ).first()
        
        if fee_structure:
            serializer = self.get_serializer(fee_structure)
            return Response(serializer.data)
        
        return Response(
            {'error': 'No fee structure found for the specified grade and term'},
            status=404
        )


class DebtRecordViewSet(BaseViewSet):
    queryset = DebtRecord.objects.filter(is_active=True)
    serializer_class = DebtRecordSerializer
    model = DebtRecord
    search_fields = ['student__first_name', 'student__last_name', 'student__username']
    filterset_fields = ['student', 'term', 'is_overdue', 'is_installment_plan']
    ordering_fields = ['due_date', 'original_amount', 'balance']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student')
        term_id = self.request.query_params.get('term')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if term_id:
            queryset = queryset.filter(term_id=term_id)
        
        return queryset.select_related('student', 'term', 'fee_structure')
    
    @action(detail=True, methods=['post'])
    def apply_payment(self, request, pk=None):
        """Apply payment to debt record"""
        debt = self.get_object()
        amount = request.data.get('amount')
        
        if not amount:
            return Response({'error': 'Amount is required'}, status=400)
        
        try:
            debt.apply_payment(Decimal(amount))
            serializer = self.get_serializer(debt)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=True, methods=['post'])
    def apply_discount(self, request, pk=None):
        """Apply discount to debt record"""
        debt = self.get_object()
        discount_type = request.data.get('discount_type')
        amount = request.data.get('amount')
        reason = request.data.get('reason', '')
        
        if not discount_type or not amount:
            return Response(
                {'error': 'Discount type and amount are required'},
                status=400
            )
        
        try:
            debt.apply_discount(discount_type, Decimal(amount), reason)
            serializer = self.get_serializer(debt)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=True, methods=['post'])
    def setup_installment_plan(self, request, pk=None):
        """Setup installment plan for debt"""
        debt = self.get_object()
        installments = request.data.get('installments')
        due_dates = request.data.get('due_dates')
        
        if not installments or not due_dates:
            return Response(
                {'error': 'Installments and due dates are required'},
                status=400
            )
        
        try:
            debt.setup_installment_plan(installments, due_dates)
            serializer = self.get_serializer(debt)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=True, methods=['post'])
    def send_reminder(self, request, pk=None):
        """Send payment reminder"""
        debt = self.get_object()
        sms = request.data.get('sms', True)
        email = request.data.get('email', True)
        
        try:
            debt.send_reminder(sms=sms, email=email)
            return Response({'message': 'Reminder sent successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class ReceiptViewSet(BaseViewSet):
    queryset = Receipt.objects.filter(is_active=True)
    serializer_class = ReceiptSerializer
    model = Receipt
    search_fields = ['receipt_number', 'payer_name', 'student__first_name', 
                    'student__last_name']
    filterset_fields = ['status', 'paid_through', 'term', 'paid_for']
    ordering_fields = ['date', 'receipt_number', 'amount']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.select_related('student', 'term', 'paid_for', 'received_by')
    
    @action(detail=True, methods=['post'])
    def mark_printed(self, request, pk=None):
        """Mark receipt as printed"""
        receipt = self.get_object()
        receipt.mark_printed()
        serializer = self.get_serializer(receipt)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """Get daily receipts summary"""
        date = request.query_params.get('date', timezone.now().date())
        
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        receipts = Receipt.objects.filter(date=date, is_active=True)
        
        summary = receipts.aggregate(
            total_count=Count('id'),
            total_amount=Sum('amount'),
            cash_amount=Sum('amount', filter=Q(paid_through='Cash')),
            mpesa_amount=Sum('amount', filter=Q(paid_through='M-Pesa')),
            bank_amount=Sum('amount', filter=Q(paid_through='Bank Transfer'))
        )
        
        return Response({
            'date': date,
            'summary': summary,
            'receipts': ReceiptSerializer(receipts, many=True).data[:50]
        })
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create receipts"""
        receipts_data = request.data.get('receipts', [])
        
        created_receipts = []
        errors = []
        
        for receipt_data in receipt_data:
            serializer = ReceiptSerializer(data=receipt_data)
            if serializer.is_valid():
                serializer.save()
                created_receipts.append(serializer.data)
            else:
                errors.append({
                    'data': receipt_data,
                    'errors': serializer.errors
                })
        
        return Response({
            'created': len(created_receipts),
            'errors': errors,
            'receipts': created_receipts
        }, status=201 if created_receipts else 400)


class PaymentViewSet(BaseViewSet):
    queryset = Payment.objects.filter(is_active=True)
    serializer_class = PaymentSerializer
    model = Payment
    search_fields = ['payment_number', 'paid_to', 'description', 'invoice_number']
    filterset_fields = ['status', 'payment_method', 'category', 'requires_approval']
    ordering_fields = ['date', 'payment_number', 'total_amount']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        allocation_id = self.request.query_params.get('allocation')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if allocation_id:
            queryset = queryset.filter(allocation_id=allocation_id)
        
        return queryset.select_related('allocation', 'submitted_by')
    
    def perform_create(self, serializer):
        # Set submitted_by to current user
        serializer.save(submitted_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve payment"""
        payment = self.get_object()
        notes = request.data.get('notes', '')
        
        try:
            payment.approve(request.user, notes)
            serializer = self.get_serializer(payment)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Mark payment as paid"""
        payment = self.get_object()
        
        try:
            payment.mark_as_paid(request.user)
            serializer = self.get_serializer(payment)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Get payments pending approval"""
        payments = Payment.objects.filter(
            requires_approval=True,
            status=PaymentStatus.PENDING,
            is_active=True
        )
        
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)


class PaymentRecordViewSet(BaseViewSet):
    queryset = PaymentRecord.objects.filter(is_active=True)
    serializer_class = PaymentRecordSerializer
    model = PaymentRecord
    search_fields = ['payment__payment_number', 'receipt__receipt_number']
    filterset_fields = ['allocation_category', 'is_reconciled']
    ordering_fields = ['allocation_date', 'allocated_amount']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        payment_id = self.request.query_params.get('payment')
        receipt_id = self.request.query_params.get('receipt')
        
        if payment_id:
            queryset = queryset.filter(payment_id=payment_id)
        if receipt_id:
            queryset = queryset.filter(receipt_id=receipt_id)
        
        return queryset.select_related('payment', 'receipt', 'debt_record', 'allocation_category')


class InstallmentPlanViewSet(BaseViewSet):
    queryset = InstallmentPlan.objects.filter(is_active=True)
    serializer_class = InstallmentPlanSerializer
    model = InstallmentPlan
    search_fields = ['student__first_name', 'student__last_name', 'reference']
    filterset_fields = ['student', 'term', 'status', 'payment_method']
    ordering_fields = ['due_date', 'installment_number', 'amount_due']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student')
        term_id = self.request.query_params.get('term')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if term_id:
            queryset = queryset.filter(term_id=term_id)
        
        return queryset.select_related('student', 'term', 'debt_record')
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Mark installment as paid"""
        installment = self.get_object()
        amount = request.data.get('amount', installment.amount_due)
        payment_method = request.data.get('payment_method')
        reference = request.data.get('reference')
        
        try:
            installment.mark_as_paid(
                amount=Decimal(amount),
                payment_method=payment_method,
                reference=reference
            )
            serializer = self.get_serializer(installment)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue installments"""
        overdue_installments = InstallmentPlan.objects.filter(
            status='pending',
            due_date__lt=timezone.now().date(),
            is_active=True
        )
        
        serializer = self.get_serializer(overdue_installments, many=True)
        return Response(serializer.data)


class DiscountViewSet(BaseViewSet):
    queryset = Discount.objects.filter(is_active=True)
    serializer_class = DiscountSerializer
    model = Discount
    search_fields = ['student__first_name', 'student__last_name', 'reason']
    filterset_fields = ['discount_type', 'status', 'term']
    ordering_fields = ['created_at', 'discount_amount']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student')
        status = self.request.query_params.get('status')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.select_related('student', 'term', 'approved_by')
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve discount"""
        discount = self.get_object()
        notes = request.data.get('notes', '')
        
        if discount.status != 'pending':
            return Response(
                {'error': 'Only pending discounts can be approved'},
                status=400
            )
        
        discount.status = 'approved'
        discount.approved_by = request.user
        discount.approved_at = timezone.now()
        discount.approval_notes = notes
        discount.save()
        
        serializer = self.get_serializer(discount)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject discount"""
        discount = self.get_object()
        notes = request.data.get('notes', '')
        
        if discount.status != 'pending':
            return Response(
                {'error': 'Only pending discounts can be rejected'},
                status=400
            )
        
        discount.status = 'rejected'
        discount.approved_by = request.user
        discount.approved_at = timezone.now()
        discount.approval_notes = notes
        discount.save()
        
        serializer = self.get_serializer(discount)
        return Response(serializer.data)


class WaiverViewSet(BaseViewSet):
    queryset = Waiver.objects.filter(is_active=True)
    serializer_class = WaiverSerializer
    model = Waiver
    search_fields = ['student__first_name', 'student__last_name', 'reason']
    filterset_fields = ['waiver_type', 'status', 'term']
    ordering_fields = ['created_at', 'waiver_amount']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student')
        status = self.request.query_params.get('status')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.select_related('student', 'term', 'approved_by')
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve waiver"""
        waiver = self.get_object()
        notes = request.data.get('notes', '')
        
        if waiver.status != 'pending':
            return Response(
                {'error': 'Only pending waivers can be approved'},
                status=400
            )
        
        waiver.status = 'approved'
        waiver.approved_by = request.user
        waiver.approved_at = timezone.now()
        waiver.approval_notes = notes
        waiver.save()
        
        serializer = self.get_serializer(waiver)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject waiver"""
        waiver = self.get_object()
        notes = request.data.get('notes', '')
        
        if waiver.status != 'pending':
            return Response(
                {'error': 'Only pending waivers can be rejected'},
                status=400
            )
        
        waiver.status = 'rejected'
        waiver.approved_by = request.user
        waiver.approved_at = timezone.now()
        waiver.approval_notes = notes
        waiver.save()
        
        serializer = self.get_serializer(waiver)
        return Response(serializer.data)


class BudgetViewSet(BaseViewSet):
    queryset = Budget.objects.filter(is_active=True)
    serializer_class = BudgetSerializer
    model = Budget
    search_fields = ['name', 'academic_year__name']
    filterset_fields = ['academic_year', 'is_approved']
    ordering_fields = ['academic_year__name', 'term__name', 'name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        academic_year_id = self.request.query_params.get('academic_year')
        term_id = self.request.query_params.get('term')
        
        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)
        if term_id:
            queryset = queryset.filter(term_id=term_id)
        
        return queryset.select_related('academic_year', 'term', 'approved_by')
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve budget"""
        budget = self.get_object()
        
        if budget.is_approved:
            return Response({'error': 'Budget is already approved'}, status=400)
        
        budget.is_approved = True
        budget.approved_by = request.user
        budget.approved_at = timezone.now()
        budget.save()
        
        serializer = self.get_serializer(budget)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_spending(self, request, pk=None):
        """Update actual spending for budget"""
        budget = self.get_object()
        budget.update_actual_spent()
        
        serializer = self.get_serializer(budget)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current budget"""
        current_year = AcademicYear.objects.filter(is_current=True, is_active=True).first()
        current_term = AcademicTerm.objects.filter(is_current=True, is_active=True).first()
        
        if current_term:
            budget = Budget.objects.filter(
                term=current_term,
                is_active=True
            ).first()
        elif current_year:
            budget = Budget.objects.filter(
                academic_year=current_year,
                term__isnull=True,
                is_active=True
            ).first()
        else:
            budget = None
        
        if budget:
            serializer = self.get_serializer(budget)
            return Response(serializer.data)
        
        return Response({'error': 'No current budget found'}, status=404)


class FinancialReportViewSet(BaseViewSet):
    queryset = FinancialReport.objects.filter(is_active=True)
    serializer_class = FinancialReportSerializer
    model = FinancialReport
    search_fields = ['title', 'description']
    filterset_fields = ['report_type', 'is_approved']
    ordering_fields = ['period_end', 'generated_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        report_type = self.request.query_params.get('report_type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        if start_date:
            queryset = queryset.filter(period_start__gte=start_date)
        if end_date:
            queryset = queryset.filter(period_end__lte=end_date)
        
        return queryset.select_related('generated_by', 'approved_by')
    
    def perform_create(self, serializer):
        # Set generated_by to current user
        serializer.save(generated_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve financial report"""
        report = self.get_object()
        
        if report.is_approved:
            return Response({'error': 'Report is already approved'}, status=400)
        
        report.is_approved = True
        report.approved_by = request.user
        report.approved_at = timezone.now()
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generate_data(self, request, pk=None):
        """Generate report data"""
        report = self.get_object()
        report.generate_report_data()
        report.calculate_summary()
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)


# ==================== CUSTOM API VIEWS ====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financial_dashboard(request):
    """Get financial dashboard data"""
    today = timezone.now().date()
    
    # Today's receipts
    today_receipts = Receipt.objects.filter(
        date=today,
        status='completed',
        is_active=True
    )
    total_receipts_today = today_receipts.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Today's payments
    today_payments = Payment.objects.filter(
        date=today,
        status='completed',
        is_active=True
    )
    total_payments_today = today_payments.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')
    
    # Cash balance (simplified)
    cash_balance = total_receipts_today - total_payments_today
    
    # Fee collection rate for current term
    current_term = AcademicTerm.objects.filter(is_current=True, is_active=True).first()
    fee_collection_rate = Decimal('0.00')
    if current_term:
        total_fees = DebtRecord.objects.filter(
            term=current_term,
            is_active=True
        ).aggregate(total=Sum('original_amount'))['total'] or Decimal('0.00')
        
        paid_fees = DebtRecord.objects.filter(
            term=current_term,
            is_active=True
        ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
        
        if total_fees > 0:
            fee_collection_rate = (paid_fees / total_fees * 100).quantize(Decimal('0.01'))
    
    # Outstanding debt
    outstanding_debt = DebtRecord.objects.filter(
        is_active=True,
        is_reversed=False
    ).aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
    
    # Pending approvals
    pending_approvals = Payment.objects.filter(
        requires_approval=True,
        status='pending',
        is_active=True
    ).count()
    
    # Recent transactions
    recent_receipts = Receipt.objects.filter(
        is_active=True
    ).order_by('-date')[:10]
    
    recent_payments = Payment.objects.filter(
        is_active=True
    ).order_by('-date')[:10]
    
    # Overdue debts
    overdue_debts = DebtRecord.objects.filter(
        is_overdue=True,
        is_active=True,
        is_reversed=False
    ).order_by('-overdue_days')[:10]
    
    dashboard_data = {
        'total_receipts_today': total_receipts_today,
        'total_payments_today': total_payments_today,
        'cash_balance': cash_balance,
        'fee_collection_rate': fee_collection_rate,
        'outstanding_debt': outstanding_debt,
        'pending_approvals': pending_approvals,
        'recent_receipts': ReceiptSerializer(recent_receipts, many=True).data,
        'recent_payments': PaymentSerializer(recent_payments, many=True).data,
        'overdue_debts': DebtRecordSerializer(overdue_debts, many=True).data,
        'date': today
    }
    
    return Response(dashboard_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fee_collection_report(request):
    """Generate fee collection report"""
    period = request.query_params.get('period', 'term')  # term, month, year
    term_id = request.query_params.get('term')
    grade_level_id = request.query_params.get('grade_level')
    
    # Determine period
    today = timezone.now().date()
    
    if period == 'term':
        if term_id:
            term = AcademicTerm.objects.filter(id=term_id, is_active=True).first()
        else:
            term = AcademicTerm.objects.filter(is_current=True, is_active=True).first()
        
        if not term:
            return Response({'error': 'No term found'}, status=404)
        
        period_start = term.start_date
        period_end = term.end_date
        period_name = f"{term.name} - {term.academic_year.name}"
    elif period == 'month':
        period_start = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        period_end = next_month - timedelta(days=next_month.day)
        period_name = f"Month of {period_start.strftime('%B %Y')}"
    else:  # year
        current_year = AcademicYear.objects.filter(is_current=True, is_active=True).first()
        if current_year:
            period_start = current_year.start_date
            period_end = current_year.end_date
            period_name = current_year.name
        else:
            return Response({'error': 'No current academic year found'}, status=404)
    
    # Get debt records for the period
    debt_records = DebtRecord.objects.filter(
        term__start_date__gte=period_start,
        term__end_date__lte=period_end,
        is_active=True,
        is_reversed=False
    )
    
    if grade_level_id:
        # Filter by grade level through fee structure
        debt_records = debt_records.filter(
            fee_structure__grade_level_id=grade_level_id
        )
    
    # Calculate totals
    total_fees = debt_records.aggregate(total=Sum('original_amount'))['total'] or Decimal('0.00')
    collected_fees = debt_records.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
    pending_fees = total_fees - collected_fees
    collection_rate = (collected_fees / total_fees * 100).quantize(Decimal('0.01')) if total_fees > 0 else Decimal('0.00')
    
    # Grade level breakdown
    grade_level_breakdown = {}
    if not grade_level_id:
        grade_levels = GradeLevel.objects.filter(is_active=True)
        for grade in grade_levels:
            grade_debts = debt_records.filter(
                fee_structure__grade_level=grade
            )
            grade_total = grade_debts.aggregate(total=Sum('original_amount'))['total'] or Decimal('0.00')
            grade_collected = grade_debts.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
            
            if grade_total > 0:
                grade_level_breakdown[grade.name] = {
                    'total_fees': grade_total,
                    'collected_fees': grade_collected,
                    'collection_rate': (grade_collected / grade_total * 100).quantize(Decimal('0.01'))
                }
    
    # Payment method breakdown
    receipts = Receipt.objects.filter(
        date__range=[period_start, period_end],
        status='completed',
        is_active=True
    )
    
    payment_method_breakdown = {}
    for method in Receipt.KenyaPaymentMethod:
        method_receipts = receipts.filter(paid_through=method.value)
        method_total = method_receipts.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        if method_total > 0:
            payment_method_breakdown[method.label] = {
                'amount': method_total,
                'count': method_receipts.count()
            }
    
    report = {
        'period': period_name,
        'total_fees': total_fees,
        'collected_fees': collected_fees,
        'pending_fees': pending_fees,
        'collection_rate': collection_rate,
        'grade_level_breakdown': grade_level_breakdown,
        'payment_method_breakdown': payment_method_breakdown,
        'date_range': {
            'start': period_start,
            'end': period_end
        }
    }
    
    return Response(report)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_report(request):
    """Generate expense report"""
    period = request.query_params.get('period', 'month')  # month, term, year
    category = request.query_params.get('category')
    
    # Determine period
    today = timezone.now().date()
    
    if period == 'term':
        current_term = AcademicTerm.objects.filter(is_current=True, is_active=True).first()
        if not current_term:
            return Response({'error': 'No current term found'}, status=404)
        
        period_start = current_term.start_date
        period_end = current_term.end_date
        period_name = f"{current_term.name} - {current_term.academic_year.name}"
    elif period == 'year':
        current_year = AcademicYear.objects.filter(is_current=True, is_active=True).first()
        if not current_year:
            return Response({'error': 'No current academic year found'}, status=404)
        
        period_start = current_year.start_date
        period_end = current_year.end_date
        period_name = current_year.name
    else:  # month
        period_start = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        period_end = next_month - timedelta(days=next_month.day)
        period_name = f"Month of {period_start.strftime('%B %Y')}"
    
    # Get payments for the period
    payments = Payment.objects.filter(
        date__range=[period_start, period_end],
        status='completed',
        is_active=True
    )
    
    if category:
        payments = payments.filter(category=category)
    
    # Calculate totals
    total_expenses = payments.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Category breakdown
    category_breakdown = {}
    categories = Payment._meta.get_field('category').choices
    for cat_value, cat_label in categories:
        cat_payments = payments.filter(category=cat_value)
        cat_total = cat_payments.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        if cat_total > 0:
            category_breakdown[cat_label] = {
                'amount': cat_total,
                'percentage': (cat_total / total_expenses * 100).quantize(Decimal('0.01')) if total_expenses > 0 else Decimal('0.00'),
                'count': cat_payments.count()
            }
    
    # Allocation breakdown
    allocation_breakdown = {}
    allocations = PaymentAllocation.objects.filter(is_active=True)
    for allocation in allocations:
        alloc_payments = payments.filter(allocation=allocation)
        alloc_total = alloc_payments.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        if alloc_total > 0:
            allocation_breakdown[allocation.name] = {
                'amount': alloc_total,
                'percentage': (alloc_total / total_expenses * 100).quantize(Decimal('0.01')) if total_expenses > 0 else Decimal('0.00'),
                'count': alloc_payments.count()
            }
    
    # Top expenses
    top_expenses = payments.order_by('-total_amount')[:10]
    
    report = {
        'period': period_name,
        'total_expenses': total_expenses,
        'category_breakdown': category_breakdown,
        'allocation_breakdown': allocation_breakdown,
        'top_expenses': PaymentSerializer(top_expenses, many=True).data,
        'date_range': {
            'start': period_start,
            'end': period_end
        }
    }
    
    return Response(report)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_financial_summary(request, student_id):
    """Get financial summary for a specific student"""
    try:
        student = User.objects.get(id=student_id, role='student', is_active=True)
    except User.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)
    
    # Get current term
    current_term = AcademicTerm.objects.filter(is_current=True, is_active=True).first()
    
    # Get debt records
    debt_records = DebtRecord.objects.filter(
        student=student,
        is_active=True,
        is_reversed=False
    )
    
    # Current term debt
    current_term_debt = None
    if current_term:
        current_term_debt = debt_records.filter(term=current_term).first()
    
    # Calculate totals
    total_debt = debt_records.aggregate(total=Sum('original_amount'))['total'] or Decimal('0.00')
    total_paid = debt_records.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
    total_balance = debt_records.aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
    
    # Get receipts
    receipts = Receipt.objects.filter(
        student=student,
        is_active=True
    ).order_by('-date')[:10]
    
    # Get discounts
    discounts = Discount.objects.filter(
        student=student,
        is_active=True,
        status='approved'
    )
    
    total_discounts = discounts.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0.00')
    
    # Get waivers
    waivers = Waiver.objects.filter(
        student=student,
        is_active=True,
        status='approved'
    )
    
    total_waivers = waivers.aggregate(total=Sum('waiver_amount'))['total'] or Decimal('0.00')
    
    summary = {
        'student': {
            'id': student.id,
            'name': student.get_full_name(),
            'username': student.username,
            'email': student.email
        },
        'current_term': AcademicTermSerializer(current_term).data if current_term else None,
        'current_term_debt': DebtRecordSerializer(current_term_debt).data if current_term_debt else None,
        'financial_summary': {
            'total_debt': total_debt,
            'total_paid': total_paid,
            'total_balance': total_balance,
            'total_discounts': total_discounts,
            'total_waivers': total_waivers,
            'net_amount_payable': max(Decimal('0.00'), total_balance - total_discounts - total_waivers)
        },
        'recent_receipts': ReceiptSerializer(receipts, many=True).data,
        'discounts': DiscountSerializer(discounts, many=True).data,
        'waivers': WaiverSerializer(waivers, many=True).data,
        'debt_history': DebtRecordSerializer(debt_records, many=True).data
    }
    
    return Response(summary)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_receipts_csv(request):
    """Export receipts as CSV"""
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    student_id = request.query_params.get('student')
    
    if not start_date or not end_date:
        return Response(
            {'error': 'start_date and end_date parameters are required'},
            status=400
        )
    
    receipts = Receipt.objects.filter(
        date__range=[start_date, end_date],
        is_active=True
    ).select_related('student', 'term', 'paid_for')
    
    if student_id:
        receipts = receipts.filter(student_id=student_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="receipts_{start_date}_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Receipt Number', 'Date', 'Student Name', 'Student ID',
        'Term', 'Payer Name', 'Amount', 'Payment Method', 'Status',
        'Purpose', 'Received By', 'Notes'
    ])
    
    for receipt in receipts:
        writer.writerow([
            receipt.receipt_number,
            receipt.date,
            receipt.student.get_full_name(),
            receipt.student.username,
            receipt.term.name if receipt.term else '',
            receipt.payer_name,
            receipt.amount,
            receipt.get_paid_through_display(),
            receipt.get_status_display(),
            receipt.paid_for.name if receipt.paid_for else '',
            receipt.received_by.get_full_name() if receipt.received_by else '',
            receipt.notes or ''
        ])
    
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_payments_csv(request):
    """Export payments as CSV"""
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    allocation_id = request.query_params.get('allocation')
    
    if not start_date or not end_date:
        return Response(
            {'error': 'start_date and end_date parameters are required'},
            status=400
        )
    
    payments = Payment.objects.filter(
        date__range=[start_date, end_date],
        is_active=True
    ).select_related('allocation', 'submitted_by')
    
    if allocation_id:
        payments = payments.filter(allocation_id=allocation_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="payments_{start_date}_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Payment Number', 'Date', 'Paid To', 'Description',
        'Amount', 'Tax', 'Total Amount', 'Payment Method',
        'Status', 'Category', 'Allocation', 'Submitted By', 'Notes'
    ])
    
    for payment in payments:
        writer.writerow([
            payment.payment_number,
            payment.date,
            payment.paid_to,
            payment.description[:100],
            payment.amount,
            payment.tax_amount,
            payment.total_amount,
            payment.get_payment_method_display(),
            payment.get_status_display(),
            payment.get_category_display(),
            payment.allocation.name if payment.allocation else '',
            payment.submitted_by.get_full_name() if payment.submitted_by else '',
            payment.notes or ''
        ])
    
    return response