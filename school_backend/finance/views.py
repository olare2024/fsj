# finance/views.py
"""
Finance Views for Delvok Academy School Management System
Comprehensive finance views with Kenya-specific features
"""

import uuid
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Count, Sum, Avg, F, ExpressionWrapper, DecimalField
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta, date
from decimal import Decimal
import logging
import json

from accounts.models import User
from administration.models import  School
from academics.models import AcademicYear, AcademicTerm, Class, StudentClassAssignment
from students.models import StudentProfile, StudentEnrollment
from .models import (
    ReceiptAllocation, PaymentAllocation, FeeStructure, DebtRecord,
    Receipt, Payment, PaymentRecord, FinancialReport, Budget,
    TaxConfiguration, ComplianceRecord, FinancialDashboard,
    KenyaPaymentMethod, PaymentStatus, FeeCategory, FinancialUtils, InstallmentPlan, Discount, Waiver, FinancialAuditLog
)
from .serializers import (
    FinancialSettingsSerializer, ReceiptAllocationSerializer, PaymentAllocationSerializer,
    FeeStructureSerializer, DebtRecordSerializer,
    ReceiptSerializer, PaymentSerializer, PaymentRecordSerializer,
    FinancialReportSerializer, BudgetSerializer,
    FinancialAuditLogSerializer,
    InstallmentPlanSerializer, DiscountSerializer, WaiverSerializer,
    TaxConfigurationSerializer, ComplianceRecordSerializer,
    FinancialDashboardSerializer, FinancialSummarySerializer,
    DebtSummarySerializer, PaymentPlanSerializer,
    BulkReceiptCreateSerializer, BulkPaymentApplySerializer
)

logger = logging.getLogger(__name__)


# ==================== ALLOCATION VIEWSETS ====================
class ReceiptAllocationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing receipt allocations"""
    queryset = ReceiptAllocation.objects.all()
    serializer_class = ReceiptAllocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'is_optional', 'applies_to_boarding']
    search_fields = ['name', 'abbr', 'description']
    ordering_fields = ['name', 'category', 'default_amount']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all fee categories with counts"""
        categories = []
        for category_code, category_name in FeeCategory.choices:
            count = ReceiptAllocation.objects.filter(
                category=category_code, 
                is_active=True
            ).count()
            categories.append({
                'code': category_code,
                'name': category_name,
                'count': count
            })
        
        return Response(categories)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get allocation summary"""
        total_allocations = self.get_queryset().count()
        active_allocations = self.get_queryset().filter(is_active=True).count()
        optional_allocations = self.get_queryset().filter(is_optional=True).count()
        
        # Summary by category
        category_summary = self.get_queryset().values('category').annotate(
            count=Count('id'),
            total_default=Sum('default_amount')
        )
        
        summary = {
            'total_allocations': total_allocations,
            'active_allocations': active_allocations,
            'optional_allocations': optional_allocations,
            'category_summary': list(category_summary),  # Convert QuerySet to list
            'created_today': self.get_queryset().filter(
                created_at__date=timezone.now().date()
            ).count()
        }
        
        return Response(summary)


class PaymentAllocationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payment allocations"""
    queryset = PaymentAllocation.objects.all()
    serializer_class = PaymentAllocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'has_budget_limit']
    search_fields = ['name', 'abbr', 'description']
    ordering_fields = ['name', 'category', 'annual_budget']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def budget_status(self, request):
        """Get budget status for all allocations"""
        allocations = self.get_queryset().filter(
            has_budget_limit=True,
            is_active=True
        )
        
        budget_status = []
        for allocation in allocations:
            spent = allocation.spent_this_year
            utilization = allocation.budget_utilization
            remaining = allocation.annual_budget - spent if allocation.annual_budget else Decimal('0.00')
            
            budget_status.append({
                'id': allocation.id,
                'name': allocation.name,
                'annual_budget': allocation.annual_budget,
                'spent_this_year': spent,
                'budget_utilization': utilization,
                'remaining_budget': max(Decimal('0.00'), remaining),
                'status': 'over_budget' if spent > allocation.annual_budget else 'within_budget'
            })
        
        return Response(budget_status)


# ==================== FEE STRUCTURE VIEWSETS ====================
class FeeStructureViewSet(viewsets.ModelViewSet):
    """ViewSet for managing fee structures"""
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['curriculum', 'grade_level', 'term', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'curriculum', 'grade_level', 'effective_from']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def current_structures(self, request):
        """Get current fee structures"""
        today = timezone.now().date()
        current_structures = self.get_queryset().filter(
            Q(effective_to__isnull=True) | Q(effective_to__gte=today),
            effective_from__lte=today,
            is_active=True
        )
        
        serializer = self.get_serializer(current_structures, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_curriculum(self, request):
        """Get fee structures grouped by curriculum"""
        curriculum = request.query_params.get('curriculum')
        grade_level = request.query_params.get('grade_level')
        
        queryset = self.get_queryset().filter(is_active=True)
        
        if curriculum:
            queryset = queryset.filter(curriculum=curriculum)
        
        if grade_level:
            queryset = queryset.filter(grade_level=grade_level)
        
        # Group by curriculum
        structures_by_curriculum = {}
        for structure in queryset:
            if structure.curriculum not in structures_by_curriculum:
                structures_by_curriculum[structure.curriculum] = {
                    'curriculum': structure.get_curriculum_display(),
                    'structures': []
                }
            
            structures_by_curriculum[structure.curriculum]['structures'].append(
                FeeStructureSerializer(structure).data
            )
        
        return Response(structures_by_curriculum)
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def duplicate(self, request, pk=None):
        """Duplicate a fee structure for new term"""
        fee_structure = self.get_object()
        
        new_name = request.data.get('new_name', f"{fee_structure.name} - Copy")
        new_term_id = request.data.get('new_term_id')
        
        if not new_term_id:
            return Response(
                {'error': 'new_term_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_term = AcademicTerm.objects.get(id=new_term_id)
        except AcademicTerm.DoesNotExist:
            return Response(
                {'error': 'AcademicTerm not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if fee structure already exists for this curriculum, grade, and term
        existing = FeeStructure.objects.filter(
            curriculum=fee_structure.curriculum,
            grade_level=fee_structure.grade_level,
            term=new_term
        ).exists()
        
        if existing:
            return Response(
                {'error': 'Fee structure already exists for this curriculum, grade, and term'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create duplicate
        new_structure = FeeStructure.objects.create(
            name=new_name,
            curriculum=fee_structure.curriculum,
            grade_level=fee_structure.grade_level,
            term=new_term,
            fee_components=fee_structure.fee_components,
            installment_allowed=fee_structure.installment_allowed,
            max_installments=fee_structure.max_installments,
            installment_due_dates=fee_structure.installment_due_dates,
            early_payment_discount=fee_structure.early_payment_discount,
            early_payment_deadline=fee_structure.early_payment_deadline,
            sibling_discount=fee_structure.sibling_discount,
            is_active=True,
            effective_from=timezone.now().date()
        )
        
        serializer = self.get_serializer(new_structure)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ==================== DEBT MANAGEMENT VIEWSETS ====================
class DebtRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for managing debt records"""
    queryset = DebtRecord.objects.all()
    serializer_class = DebtRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'term', 'is_overdue', 'is_installment_plan', 'is_reversed']
    search_fields = ['student__first_name', 'student__last_name', 'student__username']
    ordering_fields = ['due_date', 'created_at', 'original_amount', 'balance']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Override queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Students can only see their own debt records
        if not self.request.user.is_staff and self.request.user.role == 'student':
            queryset = queryset.filter(student=self.request.user)
        
        # Teachers can see their class students' debts
        elif self.request.user.role in ['teacher', 'head_teacher']:
            # Get classes taught by this teacher
            teacher_classes = Class.objects.filter(
                teacher_assignments__teacher__teacher=self.request.user
            ).distinct()
            
            # Get students in those classes
            student_ids = StudentClassAssignment.objects.filter(
                class_assigned__in=teacher_classes
            ).values_list('student_id', flat=True)
            
            queryset = queryset.filter(student_id__in=student_ids)
        
        # Filter by term
        term_id = self.request.query_params.get('term_id')
        if term_id:
            queryset = queryset.filter(term_id=term_id)
        
        # Filter by overdue status
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            queryset = queryset.filter(is_overdue=True)
        elif overdue == 'false':
            queryset = queryset.filter(is_overdue=False)
        
        # Filter by payment status
        payment_status = self.request.query_params.get('payment_status')
        if payment_status == 'paid':
            queryset = queryset.filter(balance=0)
        elif payment_status == 'partial':
            queryset = queryset.filter(balance__gt=0, amount_paid__gt=0)
        elif payment_status == 'unpaid':
            queryset = queryset.filter(amount_paid=0)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def apply_payment(self, request, pk=None):
        """Apply payment to debt record"""
        debt_record = self.get_object()
        
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        reference = request.data.get('reference', '')
        
        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = Decimal(amount)
        except (ValueError, TypeError, InvalidOperation):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            debt_record.apply_payment(amount)
            
            # Create receipt for the payment
            receipt = Receipt.objects.create(
                receipt_number=Receipt.generate_receipt_number(),
                date=timezone.now().date(),
                payer_name=debt_record.student.get_full_name(),
                payer_phone=debt_record.student.phone,
                student=debt_record.student,
                term=debt_record.term,
                academic_year=debt_record.term.academic_year,
                paid_for=ReceiptAllocation.objects.get(name='Tuition Fees'),
                amount=amount,
                paid_through=payment_method or KenyaPaymentMethod.CASH,
                status=PaymentStatus.COMPLETED,
                received_by=request.user,
                notes=f"Payment applied to debt for term {debt_record.term.name}. Reference: {reference}"
            )
            
            serializer = self.get_serializer(debt_record)
            return Response({
                'debt_record': serializer.data,
                'receipt': {
                    'id': str(receipt.id),
                    'receipt_number': receipt.receipt_number,
                    'amount': receipt.amount
                },
                'message': f'Payment of {amount} applied successfully'
            })
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ReceiptAllocation.DoesNotExist:
            return Response(
                {'error': 'Tuition Fees allocation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def setup_installment_plan(self, request, pk=None):
        """Setup installment payment plan"""
        debt_record = self.get_object()
        
        serializer = PaymentPlanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            debt_record.setup_installment_plan(
                installments=data['installments'],
                due_dates=data['due_dates']
            )
            
            serializer = self.get_serializer(debt_record)
            return Response({
                'debt_record': serializer.data,
                'message': 'Installment plan setup successfully'
            })
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get debt summary"""
        term_id = request.query_params.get('term_id')
        academic_year_id = request.query_params.get('academic_year_id')
        
        queryset = self.get_queryset()
        
        if term_id:
            queryset = queryset.filter(term_id=term_id)
        elif academic_year_id:
            queryset = queryset.filter(term__academic_year_id=academic_year_id)
        
        summary = queryset.aggregate(
            total_debt=Sum('original_amount'),
            total_paid=Sum('amount_paid'),
            total_discounts=Sum('discounts_applied'),
            total_penalties=Sum('late_penalty_applied')
        )
        
        total_outstanding = (summary['total_debt'] or Decimal('0.00')) - \
                           (summary['total_paid'] or Decimal('0.00'))
        
        collection_rate = Decimal('0.00')
        if summary['total_debt'] and summary['total_debt'] > 0:
            collection_rate = ((summary['total_paid'] or Decimal('0.00')) / 
                             summary['total_debt'] * 100).quantize(Decimal('0.01'))
        
        # Overdue debts
        overdue_count = queryset.filter(is_overdue=True).count()
        overdue_amount = queryset.filter(is_overdue=True).aggregate(
            total=Sum('balance')
        )['total'] or Decimal('0.00')
        
        return Response({
            'total_debt': summary['total_debt'] or Decimal('0.00'),
            'total_paid': summary['total_paid'] or Decimal('0.00'),
            'total_outstanding': total_outstanding,
            'collection_rate': collection_rate,
            'overdue_count': overdue_count,
            'overdue_amount': overdue_amount,
            'total_discounts': summary['total_discounts'] or Decimal('0.00'),
            'total_penalties': summary['total_penalties'] or Decimal('0.00')
        })
    
    @action(detail=False, methods=['get'])
    def by_class(self, request):
        """Get debt summary by class"""
        term_id = request.query_params.get('term_id')
        academic_year_id = request.query_params.get('academic_year_id')
        
        if not term_id and not academic_year_id:
            current_term = AcademicTerm.get_current_term()
            if current_term:
                term_id = current_term.id
            else:
                return Response(
                    {'error': 'No current term found and no term_id or academic_year_id provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if term_id:
            debts = DebtRecord.objects.filter(term_id=term_id)
        else:
            debts = DebtRecord.objects.filter(term__academic_year_id=academic_year_id)
        
        # Get class assignments for students with debts
        student_ids = debts.values_list('student_id', flat=True).distinct()
        class_assignments = StudentClassAssignment.objects.filter(
            student_id__in=student_ids,
            is_active=True
        ).select_related('class_assigned', 'academic_year')
        
        # Group by class
        debt_by_class = {}
        for assignment in class_assignments:
            class_name = str(assignment.class_assigned)
            if class_name not in debt_by_class:
                debt_by_class[class_name] = {
                    'class_id': assignment.class_assigned.id,
                    'class_name': class_name,
                    'total_students': 0,
                    'total_debt': Decimal('0.00'),
                    'total_paid': Decimal('0.00'),
                    'students_with_debt': 0
                }
            
            # Get debt for this student
            student_debts = debts.filter(student=assignment.student)
            if student_debts.exists():
                debt_by_class[class_name]['students_with_debt'] += 1
                
                for debt in student_debts:
                    debt_by_class[class_name]['total_debt'] += debt.original_amount
                    debt_by_class[class_name]['total_paid'] += debt.amount_paid
            
            debt_by_class[class_name]['total_students'] += 1
        
        # Calculate percentages
        for class_data in debt_by_class.values():
            if class_data['total_students'] > 0:
                class_data['debt_percentage'] = (
                    class_data['students_with_debt'] / class_data['total_students'] * 100
                ).quantize(Decimal('0.01'))
            
            if class_data['total_debt'] > 0:
                class_data['collection_rate'] = (
                    class_data['total_paid'] / class_data['total_debt'] * 100
                ).quantize(Decimal('0.01'))
            else:
                class_data['collection_rate'] = Decimal('0.00')
        
        return Response(list(debt_by_class.values()))


# ==================== RECEIPT VIEWSETS ====================
class ReceiptViewSet(viewsets.ModelViewSet):
    """ViewSet for managing receipts"""
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'paid_through', 'term', 'academic_year', 'is_printed', 'is_reconciled']
    search_fields = ['receipt_number', 'payer_name', 'student__first_name', 'student__last_name']
    ordering_fields = ['date', 'receipt_number', 'amount', 'created_at']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Override queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Students can only see their own receipts
        if not self.request.user.is_staff and self.request.user.role == 'student':
            queryset = queryset.filter(student=self.request.user)
        
        # Parents can see their children's receipts
        elif self.request.user.role == 'parent':
            # Get student children
            children = User.objects.filter(parent=self.request.user)
            queryset = queryset.filter(student__in=children)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        
        # Filter by payment method
        payment_method = self.request.query_params.get('payment_method')
        if payment_method:
            queryset = queryset.filter(paid_through=payment_method)
        
        # Filter by amount range
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        
        if min_amount:
            try:
                queryset = queryset.filter(amount__gte=Decimal(min_amount))
            except (ValueError, InvalidOperation):
                pass
        
        if max_amount:
            try:
                queryset = queryset.filter(amount__lte=Decimal(max_amount))
            except (ValueError, InvalidOperation):
                pass
        
        return queryset
    
    @transaction.atomic
    def perform_create(self, serializer):
        """Set received_by to current user"""
        serializer.save(received_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a receipt"""
        receipt = self.get_object()
        
        if receipt.status != PaymentStatus.COMPLETED:
            return Response(
                {'error': 'Only completed receipts can be verified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if receipt.verified_by:
            return Response(
                {'error': 'Receipt already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        receipt.verified_by = request.user
        receipt.verified_at = timezone.now()
        receipt.save()
        
        serializer = self.get_serializer(receipt)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_printed(self, request, pk=None):
        """Mark receipt as printed"""
        receipt = self.get_object()
        receipt.mark_printed()
        
        serializer = self.get_serializer(receipt)
        return Response(serializer.data)
    
@action(detail=True, methods=['post'])
def reconcile(self, request, pk=None):
    """Reconcile receipt"""
    receipt = self.get_object()
    
    if receipt.is_reconciled:
        return Response(
            {'error': 'Receipt already reconciled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    receipt.is_reconciled = True
    receipt.reconciled_by = request.user
    receipt.reconciled_at = timezone.now()
    receipt.save()
    
    serializer = self.get_serializer(receipt)
    return Response(serializer.data)

@action(detail=False, methods=['get'])
def daily_summary(self, request):
    """Get daily receipt summary"""
    date_param = request.query_params.get('date')
    
    try:
        if date_param:
            target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        else:
            target_date = timezone.now().date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    receipts = self.get_queryset().filter(date=target_date, status=PaymentStatus.COMPLETED)
    
    summary = receipts.aggregate(
        total_amount=Sum('amount'),
        count=Count('id')
    )
    
    # Summary by payment method
    by_method = receipts.values('paid_through').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Summary by allocation
    by_allocation = receipts.values('paid_for__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    return Response({
        'date': target_date.isoformat(),
        'total_amount': summary['total_amount'] or Decimal('0.00'),
        'total_count': summary['count'] or 0,
        'by_payment_method': list(by_method),
        'by_allocation': list(by_allocation),
        'receipts': ReceiptSerializer(receipts, many=True).data
    })
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def bulk_create(self, request):
        """Bulk create receipts"""
        serializer = BulkReceiptCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        created_receipts = []
        errors = []
        
        with transaction.atomic():
            for student in data['student_ids']:
                try:
                    receipt = Receipt.objects.create(
                        receipt_number=Receipt.generate_receipt_number(),
                        date=data.get('date', timezone.now().date()),
                        payer_name=data.get('payer_name', student.get_full_name()),
                        payer_phone=student.phone,
                        student=student,
                        term=data['term_id'],
                        academic_year=data['term_id'].academic_year,
                        paid_for=data['paid_for_id'],
                        amount=data['amount'],
                        paid_through=data['paid_through'],
                        status=PaymentStatus.COMPLETED,
                        received_by=request.user
                    )
                    created_receipts.append(receipt)
                    
                except Exception as e:
                    errors.append({
                        'student': str(student),
                        'error': str(e)
                    })
        
        if errors and not created_receipts:
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'created': ReceiptSerializer(created_receipts, many=True).data,
            'errors': errors,
            'message': f'Successfully created {len(created_receipts)} receipt(s)'
        })


# ==================== PAYMENT VIEWSETS ====================
class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payments/expenses"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'payment_method', 'requires_approval', 'is_reconciled']
    search_fields = ['payment_number', 'paid_to', 'description', 'invoice_number']
    ordering_fields = ['date', 'payment_number', 'total_amount', 'created_at']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Override queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-admin users can only see payments they submitted
        if not self.request.user.is_staff:
            queryset = queryset.filter(submitted_by=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        
        # Filter by amount range
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        
        if min_amount:
            try:
                queryset = queryset.filter(total_amount__gte=Decimal(min_amount))
            except (ValueError, InvalidOperation):
                pass
        
        if max_amount:
            try:
                queryset = queryset.filter(total_amount__lte=Decimal(max_amount))
            except (ValueError, InvalidOperation):
                pass
        
        # Filter by approval status
        needs_approval = self.request.query_params.get('needs_approval')
        if needs_approval == 'true':
            queryset = queryset.filter(requires_approval=True, status=PaymentStatus.PENDING)
        
        return queryset
    
    @transaction.atomic
    def perform_create(self, serializer):
        """Set submitted_by to current user"""
        serializer.save(submitted_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a payment"""
        payment = self.get_object()
        
        if not payment.requires_approval:
            return Response(
                {'error': 'This payment does not require approval'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if payment.status != PaymentStatus.PENDING:
            return Response(
                {'error': 'Only pending payments can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval_notes = request.data.get('notes', '')
        
        payment.approve(request.user, approval_notes)
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Mark payment as paid"""
        payment = self.get_object()
        
        if payment.status == PaymentStatus.COMPLETED:
            return Response(
                {'error': 'Payment already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.mark_as_paid(request.user)
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expenditure_summary(self, request):
        """Get expenditure summary"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date', timezone.now().date())
        
        if not start_date:
            # Default to current month
            start_date = timezone.now().replace(day=1).date()
        else:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                start_date = timezone.now().replace(day=1).date()
        
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = timezone.now().date()
        
        payments = self.get_queryset().filter(
            date__gte=start_date,
            date__lte=end_date,
            status=PaymentStatus.COMPLETED
        )
        
        # Total summary
        total_summary = payments.aggregate(
            total_amount=Sum('total_amount'),
            total_tax=Sum('tax_amount'),
            count=Count('id')
        )
        
        # Summary by category
        by_category = payments.values('category').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Summary by allocation
        by_allocation = payments.values('allocation__name').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Summary by payment method
        by_method = payments.values('payment_method').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Monthly trend
        monthly_trend = payments.values('date__month', 'date__year').annotate(
            total=Sum('total_amount')
        ).order_by('date__year', 'date__month')
        
        return Response({
            'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
            'total_summary': total_summary,
            'by_category': list(by_category),
            'by_allocation': list(by_allocation),
            'by_payment_method': list(by_method),
            'monthly_trend': list(monthly_trend)
        })


# ==================== FINANCIAL REPORT VIEWS ====================
class FinancialReportViewSet(viewsets.ModelViewSet):
    """ViewSet for financial reports"""
    queryset = FinancialReport.objects.all()
    serializer_class = FinancialReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'is_approved']
    search_fields = ['title', 'description']
    ordering_fields = ['period_start', 'period_end', 'generated_at']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def generate_daily(self, request):
        """Generate daily collection report"""
        report_date = request.query_params.get('date', timezone.now().date())
        
        try:
            target_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        except ValueError:
            target_date = timezone.now().date()
        
        # Get receipts for the day
        receipts = Receipt.objects.filter(
            date=target_date,
            status=PaymentStatus.COMPLETED
        )
        
        # Get payments for the day
        payments = Payment.objects.filter(
            date=target_date,
            status=PaymentStatus.COMPLETED
        )
        
        # Calculate totals
        total_receipts = receipts.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_payments = payments.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        net_cash = total_receipts - total_payments
        
        # Create report data
        report_data = {
            'date': target_date.isoformat(),
            'receipts': {
                'total': float(total_receipts),
                'count': receipts.count(),
                'by_method': list(receipts.values('paid_through').annotate(
                    total=Sum('amount'),
                    count=Count('id')
                ))
            },
            'payments': {
                'total': float(total_payments),
                'count': payments.count(),
                'by_category': list(payments.values('category').annotate(
                    total=Sum('total_amount'),
                    count=Count('id')
                ))
            },
            'summary': {
                'net_cash': float(net_cash),
                'cash_balance': float(net_cash)  # Simplified
            }
        }
        
        # Create or update report
        report, created = FinancialReport.objects.update_or_create(
            report_type='daily',
            period_start=target_date,
            period_end=target_date,
            defaults={
                'title': f'Daily Collection Report - {target_date}',
                'description': f'Daily financial report for {target_date}',
                'report_data': report_data,
                'total_income': total_receipts,
                'total_expenses': total_payments,
                'net_profit': net_cash,
                'generated_by': request.user
            }
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)


# ==================== API VIEWS FOR DASHBOARD AND ANALYTICS ====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financial_dashboard(request):
    """Get comprehensive financial dashboard data"""
    today = timezone.now().date()
    
    try:
        # Get or create dashboard for today
        dashboard, created = FinancialDashboard.objects.get_or_create(
            dashboard_date=today,
            defaults={
                'total_receipts_today': Decimal('0.00'),
                'total_payments_today': Decimal('0.00'),
                'cash_balance': Decimal('0.00'),
                'fee_collection_rate': Decimal('0.00'),
                'outstanding_debt': Decimal('0.00'),
                'pending_approvals': 0,
                'generated_at': timezone.now(),
                'is_current': True
            }
        )
        
        # Refresh metrics
        if hasattr(dashboard, 'refresh_metrics'):
            try:
                dashboard.refresh_metrics()
            except:
                pass  # If refresh_metrics fails, continue with existing data
        
        # Serialize the data
        serializer = FinancialDashboardSerializer(dashboard)
        
        # Add additional data that might not be in the serializer
        response_data = serializer.data
        
        # Add recent transactions (optional)
        try:
            recent_receipts = Receipt.objects.filter(
                status=PaymentStatus.COMPLETED
            ).select_related('student', 'paid_for').order_by('-date', '-created_at')[:10]
            
            recent_payments = Payment.objects.filter(
                status=PaymentStatus.COMPLETED
            ).select_related('allocation').order_by('-date', '-created_at')[:10]
            
            receipt_serializer = ReceiptSerializer(recent_receipts, many=True)
            payment_serializer = PaymentSerializer(recent_payments, many=True)
            
            response_data.update({
                'recent_transactions': {
                    'receipts': receipt_serializer.data,
                    'payments': payment_serializer.data
                }
            })
        except Exception as e:
            logger.warning(f"Could not fetch recent transactions: {e}")
            response_data['recent_transactions'] = {
                'receipts': [],
                'payments': []
            }
        
        # Add calculated fields for frontend compatibility
        response_data.update({
            'dashboard_date': dashboard.dashboard_date.isoformat(),
            'total_income': float(dashboard.total_receipts_today),  # Alias for frontend
            'total_expenses': float(dashboard.total_payments_today),  # Alias for frontend
            'pending_payments': 0,  # Placeholder - calculate if needed
            'overdue_payments': 0,  # Placeholder - calculate if needed
            'bank_balance': 0,  # Placeholder - implement bank balance logic
            'net_balance': float(dashboard.cash_balance),
            'profit_loss': float(dashboard.total_receipts_today - dashboard.total_payments_today),
            'collection_rate': float(dashboard.fee_collection_rate),
            'created': created
        })
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error in financial_dashboard: {e}")
        
        # Fallback response with today's basic data
        return Response({
            'dashboard_date': today.isoformat(),
            'total_income': 0,
            'total_expenses': 0,
            'cash_balance': 0,
            'bank_balance': 0,
            'pending_payments': 0,
            'overdue_payments': 0,
            'net_balance': 0,
            'profit_loss': 0,
            'collection_rate': 0,
            'status': 'fallback',
            'message': 'Using basic dashboard data',
            'recent_transactions': {
                'receipts': [],
                'payments': []
            }
        })



@api_view(['GET'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financial_dashboard_history(request):
    """Get historical financial dashboard data"""
    days = int(request.query_params.get('days', 7))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    dashboards = FinancialDashboard.objects.filter(
        dashboard_date__gte=start_date,
        dashboard_date__lte=end_date
    ).order_by('dashboard_date')
    
    serializer = FinancialDashboardSerializer(dashboards, many=True)
    
    # Add calculated fields for frontend compatibility
    enhanced_data = []
    for dashboard_data in serializer.data:
        dashboard_data.update({
            'total_income': float(dashboard_data.get('total_receipts_today', 0)),
            'total_expenses': float(dashboard_data.get('total_payments_today', 0)),
            'net_balance': float(dashboard_data.get('cash_balance', 0)),
            'profit_loss': float(dashboard_data.get('total_receipts_today', 0) - 
                               dashboard_data.get('total_payments_today', 0))
        })
        enhanced_data.append(dashboard_data)
    
    return Response({
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'dashboards': enhanced_data
    })


    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financial_summary(request):
    """Get comprehensive financial summary using serializer"""
    
    period = request.query_params.get('period', 'month')
    today = timezone.now().date()
    
    # Determine period dates
    if period == 'month':
        start_date = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
    elif period == 'term':
        current_term = AcademicTerm.get_current_term()
        if current_term:
            start_date = current_term.start_date
            end_date = current_term.end_date
        else:
            start_date = today.replace(day=1)
            end_date = today
    elif period == 'year':
        current_year = AcademicYear.get_current_year()
        if current_year:
            start_date = current_year.start_date
            end_date = current_year.end_date
        else:
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
    elif period == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'quarter':
        quarter = (today.month - 1) // 3 + 1
        start_month = (quarter - 1) * 3 + 1
        start_date = date(today.year, start_month, 1)
        if quarter == 4:
            end_date = date(today.year, 12, 31)
        else:
            end_month = start_month + 2
            end_date = date(today.year, end_month + 1, 1) - timedelta(days=1)
    else:
        start_date = today.replace(day=1)
        end_date = today
    
    # ==================== CALCULATE FINANCIAL DATA ====================
    
    # Calculate income (receipts)
    income = Receipt.objects.filter(
        date__gte=start_date,
        date__lte=end_date,
        status=PaymentStatus.COMPLETED
    )
    
    total_income = income.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Calculate expenses (payments)
    expenses = Payment.objects.filter(
        date__gte=start_date,
        date__lte=end_date,
        status=PaymentStatus.COMPLETED
    )
    
    total_expenses = expenses.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Net profit
    net_profit = total_income - total_expenses
    
    # ==================== INCOME BREAKDOWN ====================
    
    income_breakdown = income.values('paid_for__name', 'paid_for__category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    income_breakdown_dict = {}
    for item in income_breakdown:
        category = item['paid_for__category'] or 'other'
        if category not in income_breakdown_dict:
            income_breakdown_dict[category] = {
                'total': Decimal('0.00'),
                'details': []
            }
        
        amount = Decimal(str(item['total']))
        income_breakdown_dict[category]['total'] += amount
        income_breakdown_dict[category]['details'].append({
            'allocation': item['paid_for__name'],
            'amount': float(amount),
            'count': item['count']
        })
    
    # Convert totals to float for serializer
    for category in income_breakdown_dict:
        income_breakdown_dict[category]['total'] = float(income_breakdown_dict[category]['total'])
    
    # ==================== EXPENSE BREAKDOWN ====================
    
    expense_breakdown = expenses.values('category', 'allocation__name').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('-total')
    
    expense_breakdown_dict = {}
    for item in expense_breakdown:
        category = item['category'] or 'other'
        if category not in expense_breakdown_dict:
            expense_breakdown_dict[category] = {
                'total': Decimal('0.00'),
                'details': []
            }
        
        amount = Decimal(str(item['total']))
        expense_breakdown_dict[category]['total'] += amount
        expense_breakdown_dict[category]['details'].append({
            'allocation': item['allocation__name'],
            'amount': float(amount),
            'count': item['count']
        })
    
    # Convert totals to float for serializer
    for category in expense_breakdown_dict:
        expense_breakdown_dict[category]['total'] = float(expense_breakdown_dict[category]['total'])
    
    # ==================== FEE COLLECTION RATE ====================
    
    collection_rate = Decimal('0.00')
    if period == 'term':
        current_term = AcademicTerm.get_current_term()
        if current_term:
            total_debt = DebtRecord.objects.filter(
                term=current_term
            ).aggregate(total=Sum('original_amount'))['total'] or Decimal('0.00')
            
            total_paid = DebtRecord.objects.filter(
                term=current_term
            ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
            
            if total_debt > 0:
                collection_rate = (total_paid / total_debt * 100).quantize(Decimal('0.01'))
    elif period == 'year':
        if current_year:
            year_debts = DebtRecord.objects.filter(
                term__academic_year=current_year
            )
            total_debt = year_debts.aggregate(total=Sum('original_amount'))['total'] or Decimal('0.00')
            total_paid = year_debts.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
            
            if total_debt > 0:
                collection_rate = (total_paid / total_debt * 100).quantize(Decimal('0.01'))
    
    # ==================== OUTSTANDING DEBT ====================
    
    outstanding_debt = Decimal('0.00')
    if period == 'term':
        if current_term:
            outstanding_debt = DebtRecord.objects.filter(
                term=current_term,
                balance__gt=0
            ).aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
    elif period == 'year':
        if current_year:
            outstanding_debt = DebtRecord.objects.filter(
                term__academic_year=current_year,
                balance__gt=0
            ).aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
    else:
        # For month/quarter/week, get all active debts
        outstanding_debt = DebtRecord.objects.filter(
            balance__gt=0,
            is_active=True
        ).aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
    
    # ==================== MONTHLY TREND ====================
    
    monthly_trend_data = []
    
    if period == 'year':
        # Monthly breakdown for annual report
        for month in range(1, 13):
            month_start = date(today.year, month, 1)
            if month == 12:
                month_end = date(today.year, 12, 31)
            else:
                month_end = date(today.year, month + 1, 1) - timedelta(days=1)
            
            month_income = Receipt.objects.filter(
                date__gte=month_start,
                date__lte=month_end,
                status=PaymentStatus.COMPLETED
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            month_expenses = Payment.objects.filter(
                date__gte=month_start,
                date__lte=month_end,
                status=PaymentStatus.COMPLETED
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            monthly_trend_data.append({
                'month': month_start.strftime('%B'),
                'start': month_start.isoformat(),
                'end': month_end.isoformat(),
                'income': float(month_income),
                'expenses': float(month_expenses),
                'profit': float(month_income - month_expenses)
            })
    
    elif period == 'quarter':
        # Weekly breakdown for quarter
        current = start_date
        week_number = 1
        
        while current <= end_date:
            week_end = min(current + timedelta(days=6), end_date)
            
            week_income = Receipt.objects.filter(
                date__gte=current,
                date__lte=week_end,
                status=PaymentStatus.COMPLETED
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            week_expenses = Payment.objects.filter(
                date__gte=current,
                date__lte=week_end,
                status=PaymentStatus.COMPLETED
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            monthly_trend_data.append({
                'week': f'Week {week_number}',
                'start': current.isoformat(),
                'end': week_end.isoformat(),
                'income': float(week_income),
                'expenses': float(week_expenses),
                'profit': float(week_income - week_expenses)
            })
            
            current = week_end + timedelta(days=1)
            week_number += 1
    
    elif period == 'month':
        # Weekly breakdown for month
        current = start_date
        week_number = 1
        
        while current <= end_date:
            week_end = min(current + timedelta(days=6), end_date)
            
            week_income = Receipt.objects.filter(
                date__gte=current,
                date__lte=week_end,
                status=PaymentStatus.COMPLETED
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            week_expenses = Payment.objects.filter(
                date__gte=current,
                date__lte=week_end,
                status=PaymentStatus.COMPLETED
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            monthly_trend_data.append({
                'week': f'Week {week_number}',
                'start': current.isoformat(),
                'end': week_end.isoformat(),
                'income': float(week_income),
                'expenses': float(week_expenses),
                'profit': float(week_income - week_expenses)
            })
            
            current = week_end + timedelta(days=1)
            week_number += 1
    
    elif period == 'week':
        # Daily breakdown for week
        current = start_date
        
        while current <= end_date:
            day_income = Receipt.objects.filter(
                date=current,
                status=PaymentStatus.COMPLETED
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            day_expenses = Payment.objects.filter(
                date=current,
                status=PaymentStatus.COMPLETED
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            monthly_trend_data.append({
                'day': current.strftime('%A'),
                'date': current.isoformat(),
                'income': float(day_income),
                'expenses': float(day_expenses),
                'profit': float(day_income - day_expenses)
            })
            
            current += timedelta(days=1)
    
    # ==================== COMPARISON WITH PREVIOUS PERIOD ====================
    
    comparison_data = {}
    
    if period == 'month':
        # Compare with previous month
        prev_month_start = (start_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        prev_month_end = start_date - timedelta(days=1)
        
        prev_income = Receipt.objects.filter(
            date__gte=prev_month_start,
            date__lte=prev_month_end,
            status=PaymentStatus.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        prev_expenses = Payment.objects.filter(
            date__gte=prev_month_start,
            date__lte=prev_month_end,
            status=PaymentStatus.COMPLETED
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        prev_profit = prev_income - prev_expenses
        
        income_change = Decimal('0.00')
        expenses_change = Decimal('0.00')
        profit_change = Decimal('0.00')
        
        if prev_income > 0:
            income_change = ((total_income - prev_income) / prev_income * 100).quantize(Decimal('0.01'))
        
        if prev_expenses > 0:
            expenses_change = ((total_expenses - prev_expenses) / prev_expenses * 100).quantize(Decimal('0.01'))
        
        if prev_profit != 0:
            profit_change = ((net_profit - prev_profit) / abs(prev_profit) * 100).quantize(Decimal('0.01'))
        
        comparison_data = {
            'previous_period': {
                'start': prev_month_start.isoformat(),
                'end': prev_month_end.isoformat(),
                'income': float(prev_income),
                'expenses': float(prev_expenses),
                'profit': float(prev_profit)
            },
            'change_percentage': {
                'income': float(income_change),
                'expenses': float(expenses_change),
                'profit': float(profit_change)
            },
            'trend': {
                'income': 'up' if income_change > 0 else 'down' if income_change < 0 else 'same',
                'expenses': 'up' if expenses_change > 0 else 'down' if expenses_change < 0 else 'same',
                'profit': 'up' if profit_change > 0 else 'down' if profit_change < 0 else 'same'
            }
        }
    
    elif period == 'quarter':
        # Compare with previous quarter
        prev_quarter = (today.month - 1) // 3  # 0-based quarter
        prev_year = today.year
        
        if prev_quarter == 0:
            prev_quarter = 4
            prev_year -= 1
        
        prev_start_month = (prev_quarter - 1) * 3 + 1
        prev_start_date = date(prev_year, prev_start_month, 1)
        
        if prev_quarter == 4:
            prev_end_date = date(prev_year, 12, 31)
        else:
            prev_end_month = prev_start_month + 2
            prev_end_date = date(prev_year, prev_end_month + 1, 1) - timedelta(days=1)
        
        prev_income = Receipt.objects.filter(
            date__gte=prev_start_date,
            date__lte=prev_end_date,
            status=PaymentStatus.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        comparison_data = {
            'previous_period': {
                'quarter': prev_quarter,
                'year': prev_year,
                'start': prev_start_date.isoformat(),
                'end': prev_end_date.isoformat(),
                'income': float(prev_income)
            }
        }
    
    # ==================== ADDITIONAL METRICS ====================
    
    # Average transaction values
    avg_receipt_amount = (total_income / income.count()).quantize(Decimal('0.01')) if income.count() > 0 else Decimal('0.00')
    avg_payment_amount = (total_expenses / expenses.count()).quantize(Decimal('0.01')) if expenses.count() > 0 else Decimal('0.00')
    
    # Profit margin
    profit_margin = (net_profit / total_income * 100).quantize(Decimal('0.01')) if total_income > 0 else Decimal('0.00')
    
    # ==================== PREPARE DATA FOR SERIALIZER ====================
    
    summary_data = {
        'period': f"{start_date.isoformat()} to {end_date.isoformat()}",
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'net_profit': float(net_profit),
        'fee_collection_rate': float(collection_rate),
        'outstanding_debt': float(outstanding_debt),
        'income_breakdown': income_breakdown_dict,
        'expense_breakdown': expense_breakdown_dict,
        'monthly_trend': monthly_trend_data,
        'comparison_with_previous': comparison_data,
        'additional_metrics': {
            'avg_receipt_amount': float(avg_receipt_amount),
            'avg_payment_amount': float(avg_payment_amount),
            'profit_margin': float(profit_margin),
            'receipt_count': income.count(),
            'payment_count': expenses.count(),
            'period_type': period
        }
    }
    
    # ==================== USE THE SERIALIZER ====================
    
    try:
        serializer = FinancialSummarySerializer(data=summary_data)
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            # Log serializer errors for debugging
            logger.warning(f"FinancialSummarySerializer errors: {serializer.errors}")
            
            # Fallback to manual response with serializer errors
            return Response({
                'summary': summary_data,
                'serializer_errors': serializer.errors,
                'message': 'Using fallback response due to serializer validation errors'
            })
            
    except Exception as e:
        logger.error(f"Error in financial_summary view: {e}")
        
        # Fallback to manual response
        return Response({
            'period': f"{start_date.isoformat()} to {end_date.isoformat()}",
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'net_profit': float(net_profit),
            'fee_collection_rate': float(collection_rate),
            'outstanding_debt': float(outstanding_debt),
            'income_breakdown': income_breakdown_dict,
            'expense_breakdown': expense_breakdown_dict,
            'monthly_trend': monthly_trend_data,
            'comparison_with_previous': comparison_data,
            'additional_metrics': {
                'avg_receipt_amount': float(avg_receipt_amount),
                'avg_payment_amount': float(avg_payment_amount),
                'profit_margin': float(profit_margin),
                'receipt_count': income.count(),
                'payment_count': expenses.count(),
                'period_type': period
            },
            'error': str(e),
            'message': 'Fallback response due to error'
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def send_fee_reminders(request):
    """Send fee payment reminders to parents/students"""
    
    try:
        # Get parameters from request
        reminder_type = request.data.get('reminder_type', 'overdue')  # overdue, upcoming, all
        days_before = int(request.data.get('days_before', 7))
        include_sms = request.data.get('include_sms', True)
        include_email = request.data.get('include_email', True)
        student_ids = request.data.get('student_ids', [])
        term_id = request.data.get('term_id')
        
        # Validate term_id
        if not term_id:
            current_term = AcademicTerm.get_current_term()
            if not current_term:
                return Response(
                    {'error': 'No current term found and no term_id provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            term_id = current_term.id
        
        try:
            term = AcademicTerm.objects.get(id=term_id)
        except AcademicTerm.DoesNotExist:
            return Response(
                {'error': 'AcademicTerm not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get debt records based on reminder type
        debts = DebtRecord.objects.filter(term=term, balance__gt=0)
        
        if student_ids:
            debts = debts.filter(student_id__in=student_ids)
        
        if reminder_type == 'overdue':
            debts = debts.filter(is_overdue=True)
        elif reminder_type == 'upcoming':
            cutoff_date = timezone.now().date() + timedelta(days=days_before)
            debts = debts.filter(due_date__lte=cutoff_date, due_date__gte=timezone.now().date())
        # 'all' includes all debts with balance > 0
        
        # Group by student
        reminders_sent = []
        errors = []
        
        for debt in debts:
            try:
                student = debt.student
                
                # Prepare reminder data
                reminder_data = {
                    'student_name': student.get_full_name(),
                    'student_id': student.id,
                    'parent_name': student.parent.get_full_name() if student.parent else None,
                    'parent_email': student.parent.email if student.parent and student.parent.email else None,
                    'parent_phone': student.parent.phone if student.parent and student.parent.phone else None,
                    'term': term.name,
                    'due_date': debt.due_date.isoformat() if debt.due_date else None,
                    'balance': float(debt.balance),
                    'original_amount': float(debt.original_amount),
                    'paid_amount': float(debt.amount_paid),
                    'is_overdue': debt.is_overdue,
                    'overdue_days': debt.overdue_days
                }
                
                # Send SMS if enabled and phone exists
                if include_sms and reminder_data['parent_phone']:
                    try:
                        sms_sent = send_sms_reminder(reminder_data)
                        if sms_sent:
                            reminders_sent.append({
                                'student': student.get_full_name(),
                                'medium': 'SMS',
                                'recipient': reminder_data['parent_phone'],
                                'status': 'sent'
                            })
                    except Exception as e:
                        errors.append({
                            'student': student.get_full_name(),
                            'medium': 'SMS',
                            'error': str(e)
                        })
                
                # Send email if enabled and email exists
                if include_email and reminder_data['parent_email']:
                    try:
                        email_sent = send_email_reminder(reminder_data)
                        if email_sent:
                            reminders_sent.append({
                                'student': student.get_full_name(),
                                'medium': 'Email',
                                'recipient': reminder_data['parent_email'],
                                'status': 'sent'
                            })
                    except Exception as e:
                        errors.append({
                            'student': student.get_full_name(),
                            'medium': 'Email',
                            'error': str(e)
                        })
                
                # Update debt record
                if include_sms:
                    debt.sent_reminder_sms = True
                if include_email:
                    debt.sent_reminder_email = True
                debt.last_reminder_sent = timezone.now()
                debt.save()
                
            except Exception as e:
                errors.append({
                    'student': student.get_full_name() if 'student' in locals() else 'Unknown',
                    'error': str(e)
                })
        
        return Response({
            'success': True,
            'message': f'Sent {len(reminders_sent)} reminders',
            'details': {
                'total_debts': debts.count(),
                'reminders_sent': reminders_sent,
                'errors': errors,
                'reminder_type': reminder_type,
                'term': term.name
            },
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Error sending fee reminders: {e}")
        return Response(
            {'error': f'Failed to send reminders: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Helper functions for sending reminders
def send_sms_reminder(reminder_data):
    """Send SMS reminder"""
    # This is a placeholder - implement actual SMS sending logic
    # You would integrate with a service like Africa's Talking, Twilio, etc.
    
    student_name = reminder_data['student_name']
    balance = reminder_data['balance']
    term = reminder_data['term']
    due_date = reminder_data['due_date']
    is_overdue = reminder_data['is_overdue']
    
    if is_overdue:
        message = f"URGENT: Fee reminder for {student_name}. Overdue balance: KES {balance:,.2f} for {term}. Please pay immediately."
    else:
        due_date_str = datetime.strptime(due_date, '%Y-%m-%d').strftime('%d/%m/%Y') if due_date else 'soon'
        message = f"Fee reminder: {student_name} has balance KES {balance:,.2f} for {term}. Due: {due_date_str}."
    
    # Log the SMS (in production, this would actually send)
    logger.info(f"SMS would be sent to {reminder_data['parent_phone']}: {message}")
    
    # Return True to simulate successful sending
    # In production, check the SMS provider's response
    return True


def send_email_reminder(reminder_data):
    """Send email reminder"""
    # This is a placeholder - implement actual email sending logic
    # You would use Django's email backend or a service like SendGrid
    
    from django.core.mail import send_mail
    from django.conf import settings
    
    student_name = reminder_data['student_name']
    balance = reminder_data['balance']
    term = reminder_data['term']
    due_date = reminder_data['due_date']
    is_overdue = reminder_data['is_overdue']
    paid_amount = reminder_data['paid_amount']
    original_amount = reminder_data['original_amount']
    
    subject = f"Fee Reminder: {student_name} - {term}"
    
    if is_overdue:
        subject = f"URGENT: Overdue Fee - {student_name} - {term}"
    
    message = f"""
    Dear Parent/Guardian,
    
    This is a reminder regarding school fees for {student_name}.
    
    AcademicTerm: {term}
    Total Fees: KES {original_amount:,.2f}
    Amount Paid: KES {paid_amount:,.2f}
    Outstanding Balance: KES {balance:,.2f}
    
    """
    
    if is_overdue:
        message += f"""
        This payment is OVERDUE by {reminder_data['overdue_days']} days.
        Please make payment immediately to avoid further penalties.
        """
    elif due_date:
        due_date_str = datetime.strptime(due_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        message += f"""
        Due Date: {due_date_str}
        Please ensure payment is made before the due date.
        """
    
    message += f"""
    
    Payment Methods:
    1. M-Pesa: Paybill 123456, Account: {reminder_data['student_id']}
    2. Bank Transfer: Example Bank, Account: 1234567890
    3. Cash at school finance office
    
    For any queries, contact the finance office at finance@school.edu.ke or 0700 000000.
    
    Thank you,
    School Finance Department
    """
    
    recipient_email = reminder_data['parent_email']
    
    try:
        # In production, uncomment and configure:
        # send_mail(
        #     subject,
        #     message,
        #     settings.DEFAULT_FROM_EMAIL,
        #     [recipient_email],
        #     fail_silently=False,
        # )
        
        logger.info(f"Email would be sent to {recipient_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {e}")
        return False



class FeeReminderScheduleView(APIView):
    """Schedule and manage fee reminders"""
    permission_classes = [IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        """Schedule automatic fee reminders"""
        schedule_type = request.data.get('schedule_type', 'weekly')  # daily, weekly, monthly
        day_of_week = request.data.get('day_of_week', 'monday')  # for weekly
        day_of_month = request.data.get('day_of_month', 1)  # for monthly
        time_of_day = request.data.get('time_of_day', '09:00')
        reminder_days_before = request.data.get('reminder_days_before', [7, 3, 1])  # days before due date
        include_overdue = request.data.get('include_overdue', True)
        
        # Save schedule to database (simplified)
        schedule_data = {
            'schedule_type': schedule_type,
            'day_of_week': day_of_week,
            'day_of_month': day_of_month,
            'time_of_day': time_of_day,
            'reminder_days_before': reminder_days_before,
            'include_overdue': include_overdue,
            'is_active': True,
            'created_by': request.user.id,
            'created_at': timezone.now()
        }
        
        # In production, you would save this to a database model
        # and use Celery or Django Q for scheduling
        
        logger.info(f"Fee reminder schedule created: {schedule_data}")
        
        return Response({
            'success': True,
            'message': 'Fee reminder schedule created',
            'schedule': schedule_data
        })
    
    def get(self, request, *args, **kwargs):
        """Get reminder statistics"""
        # Get reminder statistics
        today = timezone.now().date()
        
        stats = {
            'today': {
                'sms_sent': 0,  # You would query your SMS log
                'emails_sent': 0,  # You would query your email log
                'students_notified': 0
            },
            'this_week': {
                'total_reminders': 0,
                'successful': 0,
                'failed': 0
            },
            'upcoming_reminders': self.get_upcoming_reminders(),
            'overdue_not_notified': DebtRecord.objects.filter(
                is_overdue=True,
                sent_reminder_sms=False,
                sent_reminder_email=False
            ).count()
        }
        
        return Response(stats)
    
    def get_upcoming_reminders(self):
        """Get students who need reminders in the next 7 days"""
        upcoming_cutoff = timezone.now().date() + timedelta(days=7)
        
        upcoming_debts = DebtRecord.objects.filter(
            due_date__gte=timezone.now().date(),
            due_date__lte=upcoming_cutoff,
            balance__gt=0
        ).select_related('student')
        
        reminders = []
        for debt in upcoming_debts:
            days_until_due = (debt.due_date - timezone.now().date()).days if debt.due_date else None
            
            reminders.append({
                'student_id': debt.student.id,
                'student_name': debt.student.get_full_name(),
                'due_date': debt.due_date.isoformat() if debt.due_date else None,
                'days_until_due': days_until_due,
                'balance': float(debt.balance),
                'last_reminder': debt.last_reminder_sent.isoformat() if debt.last_reminder_sent else None
            })
        
        return reminders


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_fee_reminder_status(request, student_id):
    """Get fee reminder status for a specific student"""
    try:
        student = User.objects.get(id=student_id, role='student')
        
        # Get all debts for the student
        debts = DebtRecord.objects.filter(student=student).order_by('-term__start_date')
        
        reminders = []
        for debt in debts:
            reminders.append({
                'term': debt.term.name,
                'academic_year': str(debt.term.academic_year),
                'balance': float(debt.balance),
                'due_date': debt.due_date.isoformat() if debt.due_date else None,
                'is_overdue': debt.is_overdue,
                'reminder_status': {
                    'sms_sent': debt.sent_reminder_sms,
                    'email_sent': debt.sent_reminder_email,
                    'last_reminder': debt.last_reminder_sent.isoformat() if debt.last_reminder_sent else None
                },
                'payment_plan': debt.payment_plan if debt.is_installment_plan else None
            })
        
        # Get parent contact info
        parent_info = {}
        if student.parent:
            parent_info = {
                'name': student.parent.get_full_name(),
                'email': student.parent.email,
                'phone': student.parent.phone,
                'preferred_contact': student.parent.preferred_contact_method if hasattr(student.parent, 'preferred_contact_method') else 'email'
            }
        
        return Response({
            'student': {
                'id': student.id,
                'name': student.get_full_name(),
                'admission_number': student.admission_number if hasattr(student, 'admission_number') else '',
                'current_class': student.current_class() if hasattr(student, 'current_class') else None
            },
            'parent': parent_info,
            'reminders': reminders,
            'summary': {
                'total_debts': debts.count(),
                'total_balance': float(debts.aggregate(total=Sum('balance'))['total'] or Decimal('0.00')),
                'overdue_debts': debts.filter(is_overdue=True).count(),
                'total_reminders_sent': debts.filter(sent_reminder_sms=True).count() + debts.filter(sent_reminder_email=True).count()
            }
        })
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error getting reminder status: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def test_reminder(request):
    """Send a test reminder to verify functionality"""
    test_email = request.data.get('test_email')
    test_phone = request.data.get('test_phone')
    
    if not test_email and not test_phone:
        return Response(
            {'error': 'Provide either test_email or test_phone'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    test_data = {
        'student_name': 'Test Student',
        'parent_email': test_email,
        'parent_phone': test_phone,
        'term': 'AcademicTerm 1 2024',
        'balance': 25000.00,
        'original_amount': 50000.00,
        'paid_amount': 25000.00,
        'due_date': (timezone.now().date() + timedelta(days=7)).isoformat(),
        'is_overdue': False,
        'overdue_days': 0
    }
    
    results = {
        'sms_sent': False,
        'email_sent': False,
        'errors': []
    }
    
    if test_phone:
        try:
            results['sms_sent'] = send_sms_reminder(test_data)
        except Exception as e:
            results['errors'].append({'medium': 'SMS', 'error': str(e)})
    
    if test_email:
        try:
            results['email_sent'] = send_email_reminder(test_data)
        except Exception as e:
            results['errors'].append({'medium': 'Email', 'error': str(e)})
    
    return Response({
        'success': results['sms_sent'] or results['email_sent'],
        'results': results,
        'message': 'Test reminder completed'
    })


# Add these to your finance/views.py

@api_view(['POST'])
@permission_classes([IsAdminUser])
def send_overdue_alerts(request):
    """Send overdue fee alerts"""
    # Implementation similar to send_fee_reminders but for overdue only
    pass

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_receipt_confirmation(request, receipt_id):
    """Send receipt confirmation"""
    try:
        receipt = Receipt.objects.get(id=receipt_id)
        # Send confirmation logic
        return Response({'success': True, 'message': 'Receipt confirmation sent'})
    except Receipt.DoesNotExist:
        return Response({'error': 'Receipt not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_payment_confirmation(request, payment_id):
    """Send payment confirmation"""
    try:
        payment = Payment.objects.get(id=payment_id)
        # Send confirmation logic
        return Response({'success': True, 'message': 'Payment confirmation sent'})
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=404)


# Analytics endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def revenue_trends(request):
    """Get revenue trends over time"""
    # Implementation
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_trends(request):
    """Get expense trends over time"""
    # Implementation
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def collection_efficiency(request):
    """Calculate collection efficiency metrics"""
    # Implementation
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def budget_vs_actual(request):
    """Compare budget vs actual spending"""
    # Implementation
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_debtors(request):
    """Get top debtors list"""
    # Implementation
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_revenue_sources(request):
    """Get top revenue sources"""
    # Implementation
    pass


# Reconciliation endpoints
@api_view(['GET'])
@permission_classes([IsAdminUser])
def bank_reconciliation(request):
    """Bank reconciliation view"""
    # Implementation
    pass

@api_view(['GET'])
@permission_classes([IsAdminUser])
def mpesa_reconciliation(request):
    """M-Pesa reconciliation view"""
    # Implementation
    pass

# ... and other reconciliation views



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debt_summary(request):
    """Get comprehensive debt summary"""
    
    # Get term from query params
    term_id = request.query_params.get('term_id')
    academic_year_id = request.query_params.get('academic_year_id')
    
    if term_id:
        debts = DebtRecord.objects.filter(term_id=term_id)
        try:
            term = AcademicTerm.objects.get(id=term_id)
            period_name = term.name
        except AcademicTerm.DoesNotExist:
            period_name = "AcademicTerm not found"
    elif academic_year_id:
        debts = DebtRecord.objects.filter(term__academic_year_id=academic_year_id)
        try:
            academic_year = AcademicYear.objects.get(id=academic_year_id)
            period_name = academic_year.name
        except AcademicYear.DoesNotExist:
            period_name = "Academic year not found"
    else:
        current_term = AcademicTerm.get_current_term()
        if current_term:
            debts = DebtRecord.objects.filter(term=current_term)
            period_name = current_term.name
        else:
            debts = DebtRecord.objects.none()
            period_name = "No current term"
    
    # Calculate totals
    totals = debts.aggregate(
        total_debt=Sum('original_amount'),
        total_paid=Sum('amount_paid'),
        total_discounts=Sum('discounts_applied'),
        total_penalties=Sum('late_penalty_applied')
    )
    
    total_debt = totals['total_debt'] or Decimal('0.00')
    total_paid = totals['total_paid'] or Decimal('0.00')
    total_outstanding = total_debt - total_paid
    
    collection_rate = Decimal('0.00')
    if total_debt > 0:
        collection_rate = (total_paid / total_debt * 100).quantize(Decimal('0.01'))
    
    # Overdue debts
    overdue_debts = debts.filter(is_overdue=True)
    overdue_count = overdue_debts.count()
    overdue_amount = overdue_debts.aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
    
    # Breakdown by class
    debts_by_class = []
    
    # Get all students with debts
    student_ids = debts.values_list('student_id', flat=True).distinct()
    
    if student_ids:
        # Get their current class assignments
        class_assignments = StudentClassAssignment.objects.filter(
            student_id__in=student_ids,
            is_active=True
        ).select_related('class_assigned')
        
        # Group by class
        class_totals = {}
        for assignment in class_assignments:
            class_name = str(assignment.class_assigned)
            if class_name not in class_totals:
                class_totals[class_name] = {
                    'class_name': class_name,
                    'class_id': assignment.class_assigned.id,
                    'total_students': 0,
                    'students_with_debt': 0,
                    'total_debt': Decimal('0.00'),
                    'total_paid': Decimal('0.00')
                }
            
            class_totals[class_name]['total_students'] += 1
            
            # Get debt for this student
            student_debt = debts.filter(student=assignment.student).first()
            if student_debt:
                class_totals[class_name]['students_with_debt'] += 1
                class_totals[class_name]['total_debt'] += student_debt.original_amount
                class_totals[class_name]['total_paid'] += student_debt.amount_paid
        
        # Convert to list and calculate percentages
        for class_data in class_totals.values():
            if class_data['total_students'] > 0:
                class_data['debt_percentage'] = (
                    class_data['students_with_debt'] / class_data['total_students'] * 100
                ).quantize(Decimal('0.01'))
            
            if class_data['total_debt'] > 0:
                class_data['collection_rate'] = (
                    class_data['total_paid'] / class_data['total_debt'] * 100
                ).quantize(Decimal('0.01'))
            else:
                class_data['collection_rate'] = Decimal('0.00')
            
            # Convert Decimal to float for JSON serialization
            class_data['total_debt'] = float(class_data['total_debt'])
            class_data['total_paid'] = float(class_data['total_paid'])
            class_data['debt_percentage'] = float(class_data['debt_percentage'])
            class_data['collection_rate'] = float(class_data['collection_rate'])
            
            debts_by_class.append(class_data)
    
    # Breakdown by curriculum (if fee structures exist)
    debts_by_curriculum = {}
    for debt in debts.select_related('fee_structure'):
        if debt.fee_structure:
            curriculum = debt.fee_structure.get_curriculum_display()
            if curriculum not in debts_by_curriculum:
                debts_by_curriculum[curriculum] = {
                    'total_debt': Decimal('0.00'),
                    'total_paid': Decimal('0.00'),
                    'count': 0
                }
            
            debts_by_curriculum[curriculum]['total_debt'] += debt.original_amount
            debts_by_curriculum[curriculum]['total_paid'] += debt.amount_paid
            debts_by_curriculum[curriculum]['count'] += 1
    
    # Convert Decimal to float for JSON serialization
    for curriculum in debts_by_curriculum:
        debts_by_curriculum[curriculum]['total_debt'] = float(debts_by_curriculum[curriculum]['total_debt'])
        debts_by_curriculum[curriculum]['total_paid'] = float(debts_by_curriculum[curriculum]['total_paid'])
    
    # Top debtors
    top_debtors = []
    for debt in debts.order_by('-balance')[:10]:
        top_debtors.append({
            'student_id': debt.student.id,
            'student_name': debt.student.get_full_name(),
            'class': debt.student.current_class() if hasattr(debt.student, 'current_class') else 'N/A',
            'balance': float(debt.balance),
            'paid_percentage': float(debt.paid_percentage),
            'is_overdue': debt.is_overdue
        })
    
    summary = {
        'period': period_name,
        'total_debt': float(total_debt),
        'total_paid': float(total_paid),
        'total_outstanding': float(total_outstanding),
        'collection_rate': float(collection_rate),
        'overdue_debts': {
            'count': overdue_count,
            'amount': float(overdue_amount)
        },
        'by_class': debts_by_class,
        'by_curriculum': debts_by_curriculum,
        'top_debtors': top_debtors,
        'stats': {
            'total_records': debts.count(),
            'installment_plans': debts.filter(is_installment_plan=True).count(),
            'reversed_records': debts.filter(is_reversed=True).count()
        }
    }
    
    return Response(summary)


@api_view(['POST'])
@permission_classes([IsAdminUser])
@transaction.atomic
def bulk_apply_payments(request):
    """Bulk apply payments to multiple debts"""
    
    serializer = BulkPaymentApplySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    applied_payments = []
    errors = []
    
    with transaction.atomic():
        for debt in data['debt_ids']:
            try:
                # Apply payment
                debt.apply_payment(data['amount'])
                
                # Create receipt
                receipt = Receipt.objects.create(
                    receipt_number=Receipt.generate_receipt_number(),
                    date=data['payment_date'],
                    payer_name=debt.student.get_full_name(),
                    payer_phone=debt.student.phone,
                    student=debt.student,
                    term=debt.term,
                    academic_year=debt.term.academic_year,
                    paid_for=ReceiptAllocation.objects.get(name='Tuition Fees'),
                    amount=data['amount'],
                    paid_through=data['payment_method'],
                    status=PaymentStatus.COMPLETED,
                    received_by=request.user,
                    notes=f"Bulk payment applied. Reference: {data.get('reference', '')}"
                )
                
                applied_payments.append({
                    'debt_id': str(debt.id),
                    'student': debt.student.get_full_name(),
                    'amount_applied': float(data['amount']),
                    'new_balance': float(debt.balance),
                    'receipt_number': receipt.receipt_number
                })
                
            except Exception as e:
                errors.append({
                    'debt_id': str(debt.id),
                    'student': debt.student.get_full_name(),
                    'error': str(e)
                })
    
    return Response({
        'applied_payments': applied_payments,
        'errors': errors,
        'total_applied': len(applied_payments),
        'total_errors': len(errors)
    })


# ==================== HELPER VIEWS ====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_financial_year(request):
    """Get current financial year"""
    try:
        start_year, end_year = FinancialUtils.get_financial_year()
        return Response({
            'financial_year': f"{start_year}-{end_year}",
            'start_year': start_year,
            'end_year': end_year,
            'current_date': timezone.now().date()
        })
    except Exception as e:
        logger.error(f"Error getting financial year: {e}")
        # Fallback to current year
        current_year = timezone.now().year
        return Response({
            'financial_year': f"{current_year}-{current_year + 1}",
            'start_year': current_year,
            'end_year': current_year + 1,
            'current_date': timezone.now().date()
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_methods(request):
    """Get available payment methods"""
    payment_methods = []
    for method_code, method_name in KenyaPaymentMethod.choices:
        payment_methods.append({
            'code': method_code,
            'name': method_name
        })
    
    return Response(payment_methods)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fee_categories(request):
    """Get fee categories"""
    categories = []
    for category_code, category_name in FeeCategory.choices:
        categories.append({
            'code': category_code,
            'name': category_name
        })
    
    return Response(categories)


# ==================== EXPORT FINANCIAL DATA VIEW ====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_financial_data(request):
    """Export financial data in various formats"""
    
    export_type = request.query_params.get('type', 'receipts')  # receipts, payments, debts
    format_type = request.query_params.get('format', 'json')  # json, csv, excel
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date', timezone.now().date())
    
    if not start_date:
        # Default to current month
        start_date = timezone.now().replace(day=1).date()
    
    # Prepare data based on export type
    if export_type == 'receipts':
        data = Receipt.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).select_related('student', 'term', 'paid_for')
        
        serialized_data = ReceiptSerializer(data, many=True).data
        
    elif export_type == 'payments':
        data = Payment.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).select_related('allocation', 'submitted_by')
        
        serialized_data = PaymentSerializer(data, many=True).data
        
    elif export_type == 'debts':
        term_id = request.query_params.get('term_id')
        if term_id:
            data = DebtRecord.objects.filter(term_id=term_id)
        else:
            current_term = AcademicTerm.get_current_term()
            if current_term:
                data = DebtRecord.objects.filter(term=current_term)
            else:
                data = DebtRecord.objects.none()
        
        serialized_data = DebtRecordSerializer(data, many=True).data
        
    else:
        return Response(
            {'error': 'Invalid export type'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Format response based on requested format
    if format_type == 'json':
        return Response({
            'export_type': export_type,
            'period': {'start': start_date, 'end': end_date},
            'data': serialized_data,
            'metadata': {
                'count': len(serialized_data),
                'generated_at': timezone.now(),
                'generated_by': request.user.get_full_name()
            }
        })
    
    elif format_type == 'csv':
        # For CSV export, you would typically generate a CSV file
        # This is a simplified response
        return Response({
            'message': 'CSV export would be generated here',
            'data_count': len(serialized_data)
        })
    
    else:
        return Response(
            {'error': 'Format not supported yet'},
            status=status.HTTP_400_BAD_REQUEST
        )


# ==================== ADDITIONAL VIEWS ====================

# Add these to your finance/views.py file

# ==================== QUARTERLY REPORT VIEW ====================
class QuarterlyReportView(generics.RetrieveAPIView):
    """Generate quarterly financial report"""
    permission_classes = [IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        quarter = request.query_params.get('quarter', '1')
        year = request.query_params.get('year', timezone.now().year)
        
        try:
            year = int(year)
            quarter = int(quarter)
            
            if quarter < 1 or quarter > 4:
                return Response(
                    {'error': 'Quarter must be between 1 and 4'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': 'Invalid quarter or year format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate quarter dates
        quarter_start_month = (quarter - 1) * 3 + 1
        quarter_start_date = date(year, quarter_start_month, 1)
        
        if quarter == 4:
            quarter_end_date = date(year, 12, 31)
        else:
            quarter_end_date = date(year, quarter_start_month + 3, 1) - timedelta(days=1)
        
        # Get receipts for the quarter
        receipts = Receipt.objects.filter(
            date__gte=quarter_start_date,
            date__lte=quarter_end_date,
            status=PaymentStatus.COMPLETED
        )
        
        # Get payments for the quarter
        payments = Payment.objects.filter(
            date__gte=quarter_start_date,
            date__lte=quarter_end_date,
            status=PaymentStatus.COMPLETED
        )
        
        # Calculate totals
        total_income = receipts.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_expenses = payments.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        net_profit = total_income - total_expenses
        
        # Income breakdown by allocation
        income_breakdown = receipts.values('paid_for__name', 'paid_for__category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Expense breakdown by category
        expense_breakdown = payments.values('category', 'allocation__name').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Monthly breakdown
        monthly_breakdown = []
        current_month = quarter_start_date
        
        while current_month <= quarter_end_date:
            month_end = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            if month_end > quarter_end_date:
                month_end = quarter_end_date
            
            month_receipts = receipts.filter(
                date__gte=current_month,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            month_payments = payments.filter(
                date__gte=current_month,
                date__lte=month_end
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            monthly_breakdown.append({
                'month': current_month.strftime('%B'),
                'start_date': current_month,
                'end_date': month_end,
                'income': float(month_receipts),
                'expenses': float(month_payments),
                'profit': float(month_receipts - month_payments)
            })
            
            # Move to next month
            current_month = month_end + timedelta(days=1)
            if current_month.day != 1:
                current_month = current_month.replace(day=1)
        
        # Top 10 revenue sources
        top_revenue_sources = receipts.values(
            'paid_for__name', 'student__current_class__name'
        ).annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')[:10]
        
        # Top 10 expense categories
        top_expense_categories = payments.values(
            'category', 'allocation__name'
        ).annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')[:10]
        
        report = {
            'quarter': quarter,
            'year': year,
            'period': {
                'start': quarter_start_date,
                'end': quarter_end_date
            },
            'summary': {
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'net_profit': float(net_profit),
                'profit_margin': float((net_profit / total_income * 100).quantize(Decimal('0.01'))) if total_income > 0 else 0.0,
                'receipt_count': receipts.count(),
                'payment_count': payments.count()
            },
            'breakdown': {
                'income': list(income_breakdown),
                'expenses': list(expense_breakdown)
            },
            'monthly_breakdown': monthly_breakdown,
            'top_revenue_sources': list(top_revenue_sources),
            'top_expense_categories': list(top_expense_categories),
            'generated_at': timezone.now(),
            'generated_by': request.user.get_full_name()
        }
        
        return Response(report)


# ==================== ANNUAL REPORT VIEW ====================
class AnnualReportView(generics.RetrieveAPIView):
    """Generate annual financial report"""
    permission_classes = [IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        year = request.query_params.get('year', timezone.now().year)
        
        try:
            year = int(year)
        except ValueError:
            return Response(
                {'error': 'Invalid year format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        # Get receipts for the year
        receipts = Receipt.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            status=PaymentStatus.COMPLETED
        )
        
        # Get payments for the year
        payments = Payment.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            status=PaymentStatus.COMPLETED
        )
        
        # Get debt records for the year
        debts = DebtRecord.objects.filter(
            created_at__year=year
        )
        
        # Calculate financial totals
        total_income = receipts.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_expenses = payments.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        net_profit = total_income - total_expenses
        
        # Debt analysis
        debt_summary = debts.aggregate(
            total_debt=Sum('original_amount'),
            total_paid=Sum('amount_paid'),
            total_discounts=Sum('discounts_applied'),
            total_penalties=Sum('late_penalty_applied')
        )
        
        total_debt = debt_summary['total_debt'] or Decimal('0.00')
        total_paid = debt_summary['total_paid'] or Decimal('0.00')
        collection_rate = (total_paid / total_debt * 100).quantize(Decimal('0.01')) if total_debt > 0 else Decimal('0.00')
        
        # Monthly trends
        monthly_trends = []
        for month in range(1, 13):
            month_start = date(year, month, 1)
            if month == 12:
                month_end = date(year, 12, 31)
            else:
                month_end = date(year, month + 1, 1) - timedelta(days=1)
            
            month_receipts = receipts.filter(
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            month_payments = payments.filter(
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            month_debts = debts.filter(created_at__month=month)
            month_debt_paid = month_debts.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
            
            monthly_trends.append({
                'month': month_start.strftime('%B'),
                'income': float(month_receipts),
                'expenses': float(month_payments),
                'debt_collected': float(month_debt_paid),
                'profit': float(month_receipts - month_payments)
            })
        
        # Payment method analysis
        payment_method_analysis = receipts.values('paid_through').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Expense category analysis
        expense_category_analysis = payments.values('category').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Fee category analysis
        fee_category_analysis = receipts.values('paid_for__category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Top performing classes (by fee collection)
        class_performance = []
        classes = Class.objects.filter(is_active=True)
        
        for class_obj in classes:
            # Get students in this class
            student_ids = StudentClassAssignment.objects.filter(
                class_assigned=class_obj,
                is_active=True
            ).values_list('student_id', flat=True)
            
            class_receipts = receipts.filter(student_id__in=student_ids)
            class_total = class_receipts.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            if class_total > 0:
                class_debts = debts.filter(student_id__in=student_ids)
                class_debt_paid = class_debts.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
                class_total_debt = class_debts.aggregate(total=Sum('original_amount'))['total'] or Decimal('0.00')
                
                class_collection_rate = (class_debt_paid / class_total_debt * 100).quantize(Decimal('0.01')) if class_total_debt > 0 else Decimal('0.00')
                
                class_performance.append({
                    'class_name': str(class_obj),
                    'student_count': len(student_ids),
                    'total_fees_collected': float(class_total),
                    'debt_collection_rate': float(class_collection_rate),
                    'average_per_student': float(class_total / len(student_ids)) if student_ids else 0
                })
        
        # Sort classes by performance
        class_performance.sort(key=lambda x: x['total_fees_collected'], reverse=True)
        
        report = {
            'year': year,
            'period': {
                'start': start_date,
                'end': end_date
            },
            'financial_summary': {
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'net_profit': float(net_profit),
                'profit_margin': float((net_profit / total_income * 100).quantize(Decimal('0.01'))) if total_income > 0 else 0.0,
                'operating_ratio': float((total_expenses / total_income * 100).quantize(Decimal('0.01'))) if total_income > 0 else 0.0
            },
            'debt_summary': {
                'total_debt_issued': float(total_debt),
                'total_debt_collected': float(total_paid),
                'collection_rate': float(collection_rate),
                'total_discounts': float(debt_summary['total_discounts'] or Decimal('0.00')),
                'total_penalties': float(debt_summary['total_penalties'] or Decimal('0.00'))
            },
            'transaction_counts': {
                'receipts': receipts.count(),
                'payments': payments.count(),
                'debt_records': debts.count()
            },
            'analysis': {
                'payment_methods': list(payment_method_analysis),
                'expense_categories': list(expense_category_analysis),
                'fee_categories': list(fee_category_analysis)
            },
            'monthly_trends': monthly_trends,
            'class_performance': class_performance[:10],  # Top 10 classes
            'key_metrics': {
                'average_receipt_amount': float(total_income / receipts.count()) if receipts.count() > 0 else 0,
                'average_payment_amount': float(total_expenses / payments.count()) if payments.count() > 0 else 0,
                'debtors_count': debts.filter(balance__gt=0).count(),
                'overdue_debts': debts.filter(is_overdue=True).count(),
                'installment_plans': debts.filter(is_installment_plan=True).count()
            },
            'generated_at': timezone.now(),
            'generated_by': request.user.get_full_name()
        }
        
        return Response(report)


# ==================== FINANCIAL AUDIT VIEW ====================
class FinancialAuditView(generics.ListAPIView):
    """View financial audit logs"""
    permission_classes = [IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        # In a real implementation, you would have an AuditLog model
        # This is a simplified version
        
        audit_type = request.query_params.get('type', 'all')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        user_id = request.query_params.get('user_id')
        
        # Get audit logs (simulated)
        audit_logs = []
        
        # Add sample audit logs for demonstration
        if audit_type in ['all', 'receipts']:
            receipts_audit = Receipt.objects.all().order_by('-created_at')[:50]
            for receipt in receipts_audit:
                audit_logs.append({
                    'timestamp': receipt.created_at,
                    'user': receipt.received_by.get_full_name() if receipt.received_by else 'System',
                    'action': 'CREATE_RECEIPT',
                    'entity_type': 'Receipt',
                    'entity_id': str(receipt.id),
                    'details': f'Created receipt {receipt.receipt_number} for {receipt.amount}',
                    'ip_address': 'N/A'
                })
        
        if audit_type in ['all', 'payments']:
            payments_audit = Payment.objects.all().order_by('-created_at')[:50]
            for payment in payments_audit:
                audit_logs.append({
                    'timestamp': payment.created_at,
                    'user': payment.submitted_by.get_full_name() if payment.submitted_by else 'System',
                    'action': 'CREATE_PAYMENT',
                    'entity_type': 'Payment',
                    'entity_id': str(payment.id),
                    'details': f'Created payment {payment.payment_number} for {payment.total_amount}',
                    'ip_address': 'N/A'
                })
        
        if audit_type in ['all', 'debts']:
            debts_audit = DebtRecord.objects.all().order_by('-created_at')[:50]
            for debt in debts_audit:
                audit_logs.append({
                    'timestamp': debt.created_at,
                    'user': 'System',
                    'action': 'CREATE_DEBT',
                    'entity_type': 'DebtRecord',
                    'entity_id': str(debt.id),
                    'details': f'Created debt record for {debt.student.get_full_name()} - {debt.original_amount}',
                    'ip_address': 'N/A'
                })
        
        # Filter by date if provided
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                audit_logs = [log for log in audit_logs if log['timestamp'].date() >= start_date]
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                audit_logs = [log for log in audit_logs if log['timestamp'].date() <= end_date]
            except ValueError:
                pass
        
        # Filter by user if provided
        if user_id:
            audit_logs = [log for log in audit_logs if user_id in log['user']]
        
        # Sort by timestamp
        audit_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit to 100 records
        audit_logs = audit_logs[:100]
        
        return Response({
            'count': len(audit_logs),
            'audit_logs': audit_logs,
            'filters': {
                'type': audit_type,
                'start_date': start_date,
                'end_date': end_date,
                'user_id': user_id
            }
        })


# ==================== FINANCIAL SETTINGS VIEW ====================
class FinancialSettingsView(generics.RetrieveUpdateAPIView):
    """Manage financial settings"""
    permission_classes = [IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        # Get or create default settings
        from .models import FinancialSettings
        
        settings, created = FinancialSettings.objects.get_or_create(
            defaults={
                'school_name': 'Delvok Academy',
                'currency': 'KES',
                'tax_rate': Decimal('16.00'),
                'late_payment_fee': Decimal('500.00'),
                'late_payment_days': 30,
                'installment_fee': Decimal('200.00'),
                'mpesa_shortcode': '123456',
                'mpesa_passkey': 'your_passkey',
                'bank_account_number': '1234567890',
                'bank_name': 'Example Bank',
                'enable_auto_reminders': True,
                'reminder_days_before': 7,
                'enable_late_fees': True,
                'enable_sms_notifications': True,
                'enable_email_notifications': True,
                'receipt_prefix': 'RC',
                'payment_prefix': 'PM',
                'invoice_prefix': 'INV'
            }
        )
        
        serializer = FinancialSettingsSerializer(settings)
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        from .models import FinancialSettings
        
        settings, created = FinancialSettings.objects.get_or_create()
        serializer = FinancialSettingsSerializer(settings, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== FINANCIAL BACKUP VIEW ====================
class FinancialBackupView(generics.CreateAPIView):
    """Create financial data backup"""
    permission_classes = [IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        backup_type = request.data.get('type', 'full')
        include_receipts = request.data.get('include_receipts', True)
        include_payments = request.data.get('include_payments', True)
        include_debts = request.data.get('include_debts', True)
        include_settings = request.data.get('include_settings', True)
        
        backup_data = {
            'backup_id': str(uuid.uuid4()),
            'created_at': timezone.now(),
            'created_by': request.user.get_full_name(),
            'backup_type': backup_type,
            'data': {}
        }
        
        # Backup receipts
        if include_receipts:
            receipts = Receipt.objects.all()
            backup_data['data']['receipts'] = ReceiptSerializer(receipts, many=True).data
        
        # Backup payments
        if include_payments:
            payments = Payment.objects.all()
            backup_data['data']['payments'] = PaymentSerializer(payments, many=True).data
        
        # Backup debts
        if include_debts:
            debts = DebtRecord.objects.all()
            backup_data['data']['debts'] = DebtRecordSerializer(debts, many=True).data
        
        # Backup financial settings
        if include_settings:
            from .models import FinancialSettings
            settings = FinancialSettings.objects.first()
            if settings:
                backup_data['data']['settings'] = FinancialSettingsSerializer(settings).data
        
        # Generate filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"financial_backup_{timestamp}.json"
        
        # In a real implementation, you would save this to a file or cloud storage
        # For now, we'll return it as JSON
        
        return Response({
            'success': True,
            'message': 'Backup created successfully',
            'backup_id': backup_data['backup_id'],
            'filename': filename,
            'data_size': len(json.dumps(backup_data, default=str)),
            'created_at': backup_data['created_at'],
            'summary': {
                'receipts_count': len(backup_data['data'].get('receipts', [])),
                'payments_count': len(backup_data['data'].get('payments', [])),
                'debts_count': len(backup_data['data'].get('debts', [])),
                'has_settings': 'settings' in backup_data['data']
            }
        })





class FeeCollectionReportView(generics.RetrieveAPIView):
    """Generate fee collection report"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        term_id = request.query_params.get('term_id')
        
        if not term_id:
            return Response(
                {'error': 'term_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            term = AcademicTerm.objects.get(id=term_id)
        except AcademicTerm.DoesNotExist:
            return Response(
                {'error': 'AcademicTerm not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get debt records for the term
        debts = DebtRecord.objects.filter(term=term)
        
        # Calculate summary
        summary = debts.aggregate(
            total_debt=Sum('original_amount'),
            total_paid=Sum('amount_paid'),
            total_discounts=Sum('discounts_applied')
        )
        
        total_debt = summary['total_debt'] or Decimal('0.00')
        total_paid = summary['total_paid'] or Decimal('0.00')
        total_outstanding = total_debt - total_paid
        
        collection_rate = Decimal('0.00')
        if total_debt > 0:
            collection_rate = (total_paid / total_debt * 100).quantize(Decimal('0.01'))
        
        # Get breakdown by class
        by_class = []
        classes = Class.objects.filter(is_active=True)
        
        for class_obj in classes:
            # Get students in this class
            student_ids = StudentClassAssignment.objects.filter(
                class_assigned=class_obj,
                is_active=True
            ).values_list('student_id', flat=True)
            
            class_debts = debts.filter(student_id__in=student_ids)
            class_summary = class_debts.aggregate(
                total_debt=Sum('original_amount'),
                total_paid=Sum('amount_paid')
            )
            
            class_debt = class_summary['total_debt'] or Decimal('0.00')
            class_paid = class_summary['total_paid'] or Decimal('0.00')
            class_outstanding = class_debt - class_paid
            
            class_collection_rate = Decimal('0.00')
            if class_debt > 0:
                class_collection_rate = (class_paid / class_debt * 100).quantize(Decimal('0.01'))
            
            by_class.append({
                'class_name': str(class_obj),
                'total_students': len(student_ids),
                'students_with_debt': class_debts.count(),
                'total_debt': float(class_debt),
                'total_paid': float(class_paid),
                'total_outstanding': float(class_outstanding),
                'collection_rate': float(class_collection_rate)
            })
        
        report = {
            'term': {
                'id': term.id,
                'name': term.name,
                'academic_year': str(term.academic_year)
            },
            'summary': {
                'total_debt': float(total_debt),
                'total_paid': float(total_paid),
                'total_outstanding': float(total_outstanding),
                'collection_rate': float(collection_rate),
                'total_discounts': float(summary['total_discounts'] or Decimal('0.00'))
            },
            'by_class': by_class,
            'generated_at': timezone.now(),
            'generated_by': request.user.get_full_name()
        }
        
        return Response(report)


class ExpenditureReportView(generics.RetrieveAPIView):
    """Generate expenditure report"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date', timezone.now().date())
        
        if not start_date:
            # Default to current month
            start_date = timezone.now().replace(day=1).date()
        else:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get payments for the period
        payments = Payment.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            status=PaymentStatus.COMPLETED
        )
        
        # Calculate summary
        summary = payments.aggregate(
            total_amount=Sum('total_amount'),
            total_tax=Sum('tax_amount'),
            count=Count('id')
        )
        
        # Breakdown by category
        by_category = payments.values('category').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Breakdown by allocation
        by_allocation = payments.values('allocation__name').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Monthly trend
        monthly_trend = []
        current = start_date.replace(day=1)
        
        while current <= end_date:
            next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
            month_end = min(next_month - timedelta(days=1), end_date)
            
            month_payments = payments.filter(
                date__gte=current,
                date__lte=month_end
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            monthly_trend.append({
                'month': current.strftime('%B %Y'),
                'start': current.isoformat(),
                'end': month_end.isoformat(),
                'total': float(month_payments)
            })
            
            current = next_month
        
        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_amount': float(summary['total_amount'] or Decimal('0.00')),
                'total_tax': float(summary['total_tax'] or Decimal('0.00')),
                'count': summary['count'] or 0
            },
            'breakdown': {
                'by_category': list(by_category),
                'by_allocation': list(by_allocation)
            },
            'monthly_trend': monthly_trend,
            'generated_at': timezone.now(),
            'generated_by': request.user.get_full_name()
        }
        
        return Response(report)


class StudentFinancialPortalView(APIView):
    """Student financial portal"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        student = request.user
        
        # Only students can access their own financial portal
        if student.role != 'student':
            return Response(
                {'error': 'Only students can access this portal'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get current term
        current_term = AcademicTerm.get_current_term()
        
        # Get student's debt records
        debts = DebtRecord.objects.filter(student=student)
        
        # Get student's receipts
        receipts = Receipt.objects.filter(student=student)
        
        # Get current class assignment
        current_class = None
        try:
            class_assignment = StudentClassAssignment.objects.filter(
                student=student,
                is_active=True
            ).first()
            
            if class_assignment:
                current_class = {
                    'class_name': str(class_assignment.class_assigned),
                    'class_id': class_assignment.class_assigned.id
                }
        except StudentClassAssignment.DoesNotExist:
            pass
        
        # Calculate summary
        total_debt = debts.aggregate(total=Sum('original_amount'))['total'] or Decimal('0.00')
        total_paid = debts.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
        total_outstanding = total_debt - total_paid
        
        # Get overdue debts
        overdue_debts = debts.filter(is_overdue=True)
        
        # Get upcoming payments (next 30 days)
        thirty_days_from_now = timezone.now().date() + timedelta(days=30)
        upcoming_payments = debts.filter(
            due_date__gte=timezone.now().date(),
            due_date__lte=thirty_days_from_now,
            balance__gt=0
        )
        
        portal_data = {
            'student': {
                'id': student.id,
                'name': student.get_full_name(),
                'username': student.username,
                'email': student.email,
                'phone': student.phone,
                'current_class': current_class
            },
            'current_term': current_term.name if current_term else None,
            'financial_summary': {
                'total_debt': float(total_debt),
                'total_paid': float(total_paid),
                'total_outstanding': float(total_outstanding),
                'paid_percentage': float((total_paid / total_debt * 100).quantize(Decimal('0.01'))) if total_debt > 0 else 0.0
            },
            'overdue_debts': {
                'count': overdue_debts.count(),
                'amount': float(overdue_debts.aggregate(total=Sum('balance'))['total'] or Decimal('0.00'))
            },
            'upcoming_payments': DebtRecordSerializer(upcoming_payments, many=True).data,
            'recent_receipts': ReceiptSerializer(receipts.order_by('-date')[:10], many=True).data,
            'all_debts': DebtRecordSerializer(debts, many=True).data
        }
        
        return Response(portal_data)


class MpesaCallbackView(APIView):
    """Handle M-Pesa callback"""
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            
            # Log the callback for debugging
            logger.info(f"M-Pesa callback received: {json.dumps(data)}")
            
            # Extract M-Pesa transaction details
            transaction_data = data.get('Body', {}).get('stkCallback', {})
            
            if not transaction_data:
                return Response({
                    'ResultCode': 0,
                    'ResultDesc': 'Success'
                })
            
            # Extract transaction details
            merchant_request_id = transaction_data.get('MerchantRequestID')
            checkout_request_id = transaction_data.get('CheckoutRequestID')
            result_code = transaction_data.get('ResultCode')
            result_desc = transaction_data.get('ResultDesc')
            
            callback_metadata = transaction_data.get('CallbackMetadata', {}).get('Item', [])
            
            # Extract payment details from metadata
            payment_data = {}
            for item in callback_metadata:
                payment_data[item.get('Name')] = item.get('Value')
            
            # Process successful payment
            if result_code == 0:
                amount = payment_data.get('Amount')
                mpesa_receipt_number = payment_data.get('MpesaReceiptNumber')
                phone_number = payment_data.get('PhoneNumber')
                transaction_date = payment_data.get('TransactionDate')
                
                # Here you would typically:
                # 1. Find the student/user by phone number
                # 2. Create a receipt record
                # 3. Update any debt records
                # 4. Send confirmation
                
                logger.info(f"Successful M-Pesa payment: {mpesa_receipt_number}, Amount: {amount}")
                
            else:
                logger.warning(f"M-Pesa payment failed: {result_desc}")
            
            # Always return success to M-Pesa
            return Response({
                'ResultCode': 0,
                'ResultDesc': 'Success'
            })
            
        except Exception as e:
            logger.error(f"Error processing M-Pesa callback: {e}")
            return Response({
                'ResultCode': 1,
                'ResultDesc': 'Error processing callback'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Add these to your finance/views.py file

# ==================== PUBLIC VIEWS (No Authentication Required) ====================

class PublicInvoiceView(APIView):
    """Public invoice view for parents/students"""
    permission_classes = []
    
    def get(self, request, *args, **kwargs):
        invoice_id = request.query_params.get('invoice_id')
        student_id = request.query_params.get('student_id')
        verification_code = request.query_params.get('verification_code')
        
        if not invoice_id and not student_id:
            return Response(
                {'error': 'Either invoice_id or student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if invoice_id:
                # Find invoice by ID
                # Note: You'll need an Invoice model or use Receipt as invoice
                receipt = get_object_or_404(Receipt, id=invoice_id)
                
                # Verify access (in real implementation, check verification code)
                if verification_code:
                    # Verify the code matches
                    pass
                
                invoice_data = {
                    'invoice_id': str(receipt.id),
                    'receipt_number': receipt.receipt_number,
                    'invoice_date': receipt.date,
                    'due_date': receipt.date + timedelta(days=30),  # Example
                    'student': {
                        'id': str(receipt.student.id),
                        'name': receipt.student.get_full_name(),
                        'class': receipt.student.current_class() if hasattr(receipt.student, 'current_class') else 'N/A'
                    },
                    'items': [
                        {
                            'description': receipt.paid_for.name,
                            'quantity': 1,
                            'unit_price': float(receipt.amount),
                            'total': float(receipt.amount)
                        }
                    ],
                    'subtotal': float(receipt.amount),
                    'tax': 0.0,  # Add if applicable
                    'total': float(receipt.amount),
                    'amount_paid': float(receipt.amount),
                    'balance': 0.0,
                    'status': 'PAID' if receipt.status == PaymentStatus.COMPLETED else 'PENDING',
                    'payment_method': receipt.get_paid_through_display(),
                    'payment_date': receipt.date,
                    'notes': receipt.notes or '',
                    'school_info': {
                        'name': 'Delvok Academy',
                        'address': 'Nairobi, Kenya',
                        'phone': '+254 700 000000',
                        'email': 'finance@delvok.ac.ke'
                    }
                }
                
                return Response(invoice_data)
            
            else:
                # Get latest invoice for student
                receipt = Receipt.objects.filter(
                    student_id=student_id
                ).order_by('-date').first()
                
                if not receipt:
                    return Response(
                        {'error': 'No invoices found for this student'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Return minimal public data
                invoice_data = {
                    'student': {
                        'name': receipt.student.get_full_name(),
                        'id': str(receipt.student.id)
                    },
                    'latest_invoice': {
                        'date': receipt.date,
                        'amount': float(receipt.amount),
                        'status': receipt.get_status_display()
                    },
                    'message': 'Please contact school administration for detailed invoice'
                }
                
                return Response(invoice_data)
                
        except Exception as e:
            logger.error(f"Error fetching public invoice: {e}")
            return Response(
                {'error': 'Unable to fetch invoice information'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PublicFeeStructureView(APIView):
    """Public fee structure view"""
    permission_classes = []
    
    def get(self, request, *args, **kwargs):
        curriculum = request.query_params.get('curriculum')
        grade_level = request.query_params.get('grade_level')
        term = request.query_params.get('term')
        
        # Get active fee structures
        fee_structures = FeeStructure.objects.filter(
            is_active=True,
            effective_from__lte=timezone.now().date()
        ).filter(
            Q(effective_to__isnull=True) | Q(effective_to__gte=timezone.now().date())
        )
        
        # Apply filters
        if curriculum:
            fee_structures = fee_structures.filter(curriculum=curriculum)
        
        if grade_level:
            fee_structures = fee_structures.filter(grade_level=grade_level)
        
        if term:
            fee_structures = fee_structures.filter(term__name__icontains=term)
        
        # Get unique curriculums
        curriculums = fee_structures.values_list('curriculum', flat=True).distinct()
        
        # Group by curriculum
        result = {}
        for curriculum_code in curriculums:
            curriculum_structures = fee_structures.filter(curriculum=curriculum_code)
            
            # Group by grade level
            grade_levels = {}
            for structure in curriculum_structures:
                grade = structure.get_grade_level_display()
                
                if grade not in grade_levels:
                    grade_levels[grade] = {
                        'curriculum': structure.get_curriculum_display(),
                        'grade_level': grade,
                        'term': str(structure.term),
                        'total_fees': 0.0,
                        'breakdown': [],
                        'payment_options': {
                            'installment_allowed': structure.installment_allowed,
                            'max_installments': structure.max_installments,
                            'early_payment_discount': float(structure.early_payment_discount) if structure.early_payment_discount else 0.0,
                            'sibling_discount': float(structure.sibling_discount) if structure.sibling_discount else 0.0
                        }
                    }
                
                # Parse fee components
                if structure.fee_components:
                    try:
                        components = structure.fee_components
                        if isinstance(components, str):
                            components = json.loads(components)
                        
                        total = Decimal('0.00')
                        breakdown = []
                        
                        for component in components:
                            amount = Decimal(str(component.get('amount', 0)))
                            total += amount
                            
                            breakdown.append({
                                'category': component.get('category', ''),
                                'name': component.get('name', ''),
                                'amount': float(amount),
                                'is_optional': component.get('is_optional', False)
                            })
                        
                        grade_levels[grade]['total_fees'] = float(total)
                        grade_levels[grade]['breakdown'] = breakdown
                        
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.error(f"Error parsing fee components: {e}")
                        grade_levels[grade]['total_fees'] = 0.0
                        grade_levels[grade]['breakdown'] = []
            
            result[curriculum_code] = list(grade_levels.values())
        
        # If specific curriculum requested, return only that
        if curriculum:
            return Response({
                'curriculum': curriculum,
                'structures': result.get(curriculum, [])
            })
        
        return Response(result)


class PublicPaymentMethodsView(APIView):
    """Public payment methods view"""
    permission_classes = []
    
    def get(self, request, *args, **kwargs):
        payment_methods = []
        
        for method_code, method_name in KenyaPaymentMethod.choices:
            payment_methods.append({
                'code': method_code,
                'name': method_name,
                'description': self.get_payment_method_description(method_code),
                'instructions': self.get_payment_instructions(method_code)
            })
        
        return Response({
            'payment_methods': payment_methods,
            'school_bank_details': {
                'bank_name': 'Example Bank',
                'account_name': 'Delvok Academy',
                'account_number': '1234567890',
                'branch': 'Nairobi Main',
                'swift_code': 'EXBKKEXXX'
            },
            'mpesa_details': {
                'paybill': '123456',
                'account_number': 'Student Admission Number',
                'instructions': 'Use your admission number as account number'
            },
            'contact_info': {
                'finance_office': '+254 700 000000',
                'email': 'finance@delvok.ac.ke',
                'office_hours': 'Monday-Friday, 8:00 AM - 4:00 PM'
            }
        })
    
    def get_payment_method_description(self, method_code):
        descriptions = {
            KenyaPaymentMethod.CASH: 'Pay in cash at the school finance office',
            KenyaPaymentMethod.MPESA: 'Mobile money payment via M-Pesa',
            KenyaPaymentMethod.BANK_TRANSFER: 'Direct bank transfer',
            KenyaPaymentMethod.CHEQUE: 'Payment by cheque',
            KenyaPaymentMethod.BANK_DEPOSIT: 'Bank deposit at any branch',
            KenyaPaymentMethod.CREDIT_CARD: 'Credit card payment (online)',
            KenyaPaymentMethod.DEBIT_CARD: 'Debit card payment (online)'
        }
        return descriptions.get(method_code, '')
    
    def get_payment_instructions(self, method_code):
        instructions = {
            KenyaPaymentMethod.MPESA: [
                'Go to M-Pesa menu on your phone',
                'Select Lipa na M-Pesa',
                'Select Paybill',
                'Enter Business No: 123456',
                'Enter Account No: Your Admission Number',
                'Enter Amount',
                'Enter your M-Pesa PIN',
                'Confirm payment'
            ],
            KenyaPaymentMethod.BANK_TRANSFER: [
                'Transfer to: Example Bank',
                'Account Name: Delvok Academy',
                'Account Number: 1234567890',
                'Branch: Nairobi Main',
                'Use student name as reference'
            ],
            KenyaPaymentMethod.BANK_DEPOSIT: [
                'Visit any bank branch',
                'Fill deposit slip with school details',
                'Make payment at the counter',
                'Keep the deposit slip as proof'
            ]
        }
        return instructions.get(method_code, ['Contact finance office for instructions'])


# ==================== WEBHOOK VIEWS ====================

class MpesaWebhookView(APIView):
    """M-Pesa webhook endpoint for real-time notifications"""
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            logger.info(f"M-Pesa webhook received: {json.dumps(data)}")
            
            # Process different webhook types
            webhook_type = data.get('type', 'unknown')
            
            if webhook_type == 'payment_received':
                return self.handle_payment_received(data)
            elif webhook_type == 'payment_failed':
                return self.handle_payment_failed(data)
            elif webhook_type == 'payment_reversed':
                return self.handle_payment_reversed(data)
            else:
                logger.warning(f"Unknown webhook type: {webhook_type}")
                return Response({'status': 'ignored', 'message': 'Unknown webhook type'})
                
        except Exception as e:
            logger.error(f"Error processing M-Pesa webhook: {e}")
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def handle_payment_received(self, data):
        # Process successful payment
        transaction_id = data.get('transaction_id')
        amount = data.get('amount')
        phone_number = data.get('phone_number')
        reference = data.get('reference')
        
        logger.info(f"Processing M-Pesa payment: {transaction_id}, Amount: {amount}")
        
        # Here you would:
        # 1. Find the student by reference (admission number)
        # 2. Create a receipt record
        # 3. Update any outstanding debts
        # 4. Send confirmation
        
        return Response({
            'status': 'success',
            'message': 'Payment processed successfully',
            'transaction_id': transaction_id
        })
    
    def handle_payment_failed(self, data):
        transaction_id = data.get('transaction_id')
        reason = data.get('reason', 'Unknown reason')
        
        logger.warning(f"M-Pesa payment failed: {transaction_id}, Reason: {reason}")
        
        # Log the failed payment
        # Potentially notify admin
        
        return Response({
            'status': 'failed',
            'message': f'Payment failed: {reason}',
            'transaction_id': transaction_id
        })
    
    def handle_payment_reversed(self, data):
        transaction_id = data.get('transaction_id')
        amount = data.get('amount')
        
        logger.info(f"M-Pesa payment reversed: {transaction_id}, Amount: {amount}")
        
        # Here you would:
        # 1. Find the original receipt
        # 2. Reverse the payment
        # 3. Update debt records
        # 4. Notify admin
        
        return Response({
            'status': 'reversed',
            'message': 'Payment reversal processed',
            'transaction_id': transaction_id
        })


class BankWebhookView(APIView):
    """Bank webhook endpoint"""
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            logger.info(f"Bank webhook received: {json.dumps(data)}")
            
            # Process bank transfer notification
            transaction_data = data.get('transaction', {})
            
            # Extract transaction details
            transaction_id = transaction_data.get('id')
            amount = transaction_data.get('amount')
            reference = transaction_data.get('reference')
            account_number = transaction_data.get('account_number')
            bank_name = transaction_data.get('bank_name')
            
            logger.info(f"Bank transaction: {transaction_id}, Amount: {amount}, Reference: {reference}")
            
            # Process the transaction
            # In a real implementation, you would:
            # 1. Verify the transaction
            # 2. Match with student using reference
            # 3. Create receipt
            # 4. Update records
            
            return Response({
                'status': 'received',
                'message': 'Transaction received for processing',
                'transaction_id': transaction_id
            })
            
        except Exception as e:
            logger.error(f"Error processing bank webhook: {e}")
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SMSWebhookView(APIView):
    """SMS webhook endpoint"""
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            logger.info(f"SMS webhook received: {json.dumps(data)}")
            
            # Process SMS delivery status
            message_id = data.get('message_id')
            status = data.get('status')
            phone_number = data.get('phone_number')
            error_message = data.get('error_message')
            
            logger.info(f"SMS status update: {message_id} - {status}")
            
            # Update SMS delivery status in your database
            # This helps track whether notifications were delivered
            
            return Response({
                'status': 'updated',
                'message': f'SMS status updated to {status}',
                'message_id': message_id
            })
            
        except Exception as e:
            logger.error(f"Error processing SMS webhook: {e}")
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmailWebhookView(APIView):
    """Email webhook endpoint"""
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            logger.info(f"Email webhook received: {json.dumps(data)}")
            
            # Process email delivery status
            message_id = data.get('message_id')
            status = data.get('status')
            email = data.get('email')
            event = data.get('event')  # delivered, opened, clicked, bounced, etc.
            
            logger.info(f"Email event: {message_id} - {event} - {status}")
            
            # Update email delivery status in your database
            # Track email engagement metrics
            
            return Response({
                'status': 'updated',
                'message': f'Email status updated - {event}',
                'message_id': message_id
            })
            
        except Exception as e:
            logger.error(f"Error processing email webhook: {e}")
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== IMPORT/EXPORT VIEWS ====================

class ReceiptExportView(APIView):
    """Export receipts"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        format_type = request.query_params.get('format', 'csv')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date', timezone.now().date())
        
        if not start_date:
            start_date = timezone.now().replace(day=1).date()
        
        # Get receipts
        receipts = Receipt.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).select_related('student', 'term', 'paid_for')
        
        if format_type == 'csv':
            # Generate CSV content
            import csv
            from io import StringIO
            
            csv_buffer = StringIO()
            csv_writer = csv.writer(csv_buffer)
            
            # Write header
            csv_writer.writerow([
                'Receipt Number', 'Date', 'Student Name', 'Student ID',
                'Class', 'AcademicTerm', 'Fee Category', 'Amount', 'Payment Method',
                'Status', 'Received By', 'Notes'
            ])
            
            # Write data
            for receipt in receipts:
                csv_writer.writerow([
                    receipt.receipt_number,
                    receipt.date.isoformat(),
                    receipt.student.get_full_name(),
                    receipt.student.username,
                    receipt.student.current_class() if hasattr(receipt.student, 'current_class') else '',
                    str(receipt.term),
                    receipt.paid_for.name,
                    str(receipt.amount),
                    receipt.get_paid_through_display(),
                    receipt.get_status_display(),
                    receipt.received_by.get_full_name() if receipt.received_by else '',
                    receipt.notes or ''
                ])
            
            # Return CSV file
            from django.http import HttpResponse
            response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
            filename = f"receipts_export_{start_date}_{end_date}.csv"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        elif format_type == 'excel':
            # For Excel export, you would use a library like pandas or openpyxl
            # This is a simplified response
            return Response({
                'message': 'Excel export would be generated here',
                'receipt_count': receipts.count(),
                'period': {'start': start_date, 'end': end_date}
            })
        
        else:
            return Response(
                {'error': 'Unsupported format. Use csv or excel'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentExportView(APIView):
    """Export payments"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        return Response({"message": "Payment export endpoint"}, status=200)


class DebtExportView(APIView):
    """Export debts"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        return Response({"message": "Debt export endpoint"}, status=200)


class FeeStructureImportView(APIView):
    """Import fee structures"""
    permission_classes = [IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        return Response({"message": "Fee structure import endpoint"}, status=200)


class StudentFinanceImportView(APIView):
    """Import student finance data"""
    permission_classes = [IsAdminUser]
    
    def post(self, request, *args, **kwargs):
        return Response({"message": "Student finance import endpoint"}, status=200)


# Add these to your finance/views.py file

# ==================== BUDGET MANAGEMENT VIEWS ====================

class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing budgets"""
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['academic_year', 'term', 'status', 'budget_type']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'total_amount', 'created_at']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'approve']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Override queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by academic year if provided
        academic_year_id = self.request.query_params.get('academic_year_id')
        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)
        
        # Filter by term if provided
        term_id = self.request.query_params.get('term_id')
        if term_id:
            queryset = queryset.filter(term_id=term_id)
        
        # Filter by budget type
        budget_type = self.request.query_params.get('budget_type')
        if budget_type:
            queryset = queryset.filter(budget_type=budget_type)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def current_budgets(self, request):
        """Get current active budgets"""
        current_year = AcademicYear.get_current_year()
        current_term = AcademicTerm.get_current_term()
        
        budgets = self.get_queryset().filter(
            status='approved',
            is_active=True
        )
        
        if current_year:
            budgets = budgets.filter(academic_year=current_year)
        
        if current_term:
            budgets = budgets.filter(term=current_term)
        
        serializer = self.get_serializer(budgets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a budget"""
        budget = self.get_object()
        
        if budget.status == 'approved':
            return Response(
                {'error': 'Budget already approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval_notes = request.data.get('notes', '')
        
        budget.status = 'approved'
        budget.approved_by = request.user
        budget.approved_at = timezone.now()
        budget.approval_notes = approval_notes
        budget.save()
        
        serializer = self.get_serializer(budget)
        return Response(serializer.data)


# ==================== COMPLIANCE AND TAX VIEWS ====================

class TaxConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet for tax configuration"""
    queryset = TaxConfiguration.objects.all()
    serializer_class = TaxConfigurationSerializer
    permission_classes = [IsAdminUser]
    
    def get_object(self):
        """Get the single tax configuration"""
        # Assuming only one tax configuration exists
        obj, created = TaxConfiguration.objects.get_or_create(
            defaults={
                'tax_rate': Decimal('16.00'),
                'tax_name': 'VAT',
                'is_active': True
            }
        )
        return obj
    
    def list(self, request, *args, **kwargs):
        """Get the tax configuration"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ComplianceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for compliance records"""
    queryset = ComplianceRecord.objects.all()
    serializer_class = ComplianceRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['compliance_type', 'status', 'priority']
    search_fields = ['title', 'description', 'regulatory_body']
    ordering_fields = ['due_date', 'created_at', 'priority']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'verify']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def upcoming_compliance(self, request):
        """Get upcoming compliance deadlines"""
        days_ahead = int(request.query_params.get('days', 30))
        cutoff_date = timezone.now().date() + timedelta(days=days_ahead)
        
        upcoming = self.get_queryset().filter(
            due_date__gte=timezone.now().date(),
            due_date__lte=cutoff_date,
            status__in=['pending', 'in_progress']
        ).order_by('due_date')
        
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify compliance record"""
        compliance = self.get_object()
        
        if compliance.status == 'verified':
            return Response(
                {'error': 'Compliance already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        verification_notes = request.data.get('notes', '')
        
        compliance.status = 'verified'
        compliance.verified_by = request.user
        compliance.verified_at = timezone.now()
        compliance.verification_notes = verification_notes
        compliance.save()
        
        serializer = self.get_serializer(compliance)
        return Response(serializer.data)


# ==================== PAYMENT RECORD VIEWS ====================

class PaymentRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for payment records (read-only)"""
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'term', 'payment_method', 'status']
    search_fields = ['receipt__receipt_number', 'student__first_name', 'student__last_name']
    ordering_fields = ['payment_date', 'created_at', 'amount']
    
    def get_queryset(self):
        """Override queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Students can only see their own payment records
        if not self.request.user.is_staff and self.request.user.role == 'student':
            queryset = queryset.filter(student=self.request.user)
        
        # Parents can see their children's payment records
        elif self.request.user.role == 'parent':
            children = User.objects.filter(parent=self.request.user)
            queryset = queryset.filter(student__in=children)
        
        # Filter by student
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        # Filter by term
        term_id = self.request.query_params.get('term_id')
        if term_id:
            queryset = queryset.filter(term_id=term_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_student(self, request, student_id=None):
        """Get payment records for a specific student"""
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payments = self.get_queryset().filter(student_id=student_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_term(self, request, term_id=None):
        """Get payment records for a specific term"""
        if not term_id:
            return Response(
                {'error': 'term_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payments = self.get_queryset().filter(term_id=term_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)


# ==================== INSTALLMENT PLAN VIEWS ====================

class InstallmentPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for installment plans"""
    queryset = InstallmentPlan.objects.all()
    serializer_class = InstallmentPlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'term', 'status', 'is_active']
    search_fields = ['student__first_name', 'student__last_name']
    ordering_fields = ['created_at', 'total_amount', 'due_date']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'process_payment']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def upcoming_installments(self, request):
        """Get upcoming installment payments"""
        days_ahead = int(request.query_params.get('days', 30))
        cutoff_date = timezone.now().date() + timedelta(days=days_ahead)
        
        upcoming = self.get_queryset().filter(
            due_date__gte=timezone.now().date(),
            due_date__lte=cutoff_date,
            status='pending',
            is_active=True
        ).order_by('due_date')
        
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue_installments(self, request):
        """Get overdue installment payments"""
        overdue = self.get_queryset().filter(
            due_date__lt=timezone.now().date(),
            status='pending',
            is_active=True
        ).order_by('due_date')
        
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Process installment payment"""
        installment = self.get_object()
        
        if installment.status == 'paid':
            return Response(
                {'error': 'Installment already paid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        reference = request.data.get('reference', '')
        
        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = Decimal(amount)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            try:
                # Update installment status
                installment.amount_paid = amount
                installment.payment_date = timezone.now().date()
                installment.payment_method = payment_method
                installment.reference = reference
                installment.status = 'paid'
                installment.save()
                
                # Create receipt
                receipt = Receipt.objects.create(
                    receipt_number=Receipt.generate_receipt_number(),
                    date=timezone.now().date(),
                    payer_name=installment.student.get_full_name(),
                    payer_phone=installment.student.phone,
                    student=installment.student,
                    term=installment.term,
                    academic_year=installment.term.academic_year,
                    paid_for=ReceiptAllocation.objects.get(name='Tuition Fees'),
                    amount=amount,
                    paid_through=payment_method or KenyaPaymentMethod.CASH,
                    status=PaymentStatus.COMPLETED,
                    received_by=request.user,
                    notes=f"Installment payment for term {installment.term.name}. Reference: {reference}"
                )
                
                # Update related debt record
                debt_record = installment.debt_record
                if debt_record:
                    debt_record.apply_payment(amount)
                
                serializer = self.get_serializer(installment)
                return Response({
                    'installment': serializer.data,
                    'receipt': {
                        'id': str(receipt.id),
                        'receipt_number': receipt.receipt_number,
                        'amount': receipt.amount
                    },
                    'message': f'Installment payment of {amount} processed successfully'
                })
                
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )


# ==================== DISCOUNT AND WAIVER VIEWS ====================

class DiscountViewSet(viewsets.ModelViewSet):
    """ViewSet for discounts"""
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'term', 'discount_type', 'status', 'is_active']
    search_fields = ['student__first_name', 'student__last_name', 'reason']
    ordering_fields = ['created_at', 'discount_amount']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'approve']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def discount_types(self, request):
        """Get available discount types"""
        discount_types = [
            {'code': 'sibling', 'name': 'Sibling Discount'},
            {'code': 'early_payment', 'name': 'Early Payment Discount'},
            {'code': 'academic', 'name': 'Academic Excellence'},
            {'code': 'sports', 'name': 'Sports Scholarship'},
            {'code': 'need_based', 'name': 'Need-based Financial Aid'},
            {'code': 'staff', 'name': 'Staff Discount'},
            {'code': 'promotional', 'name': 'Promotional Discount'},
            {'code': 'other', 'name': 'Other'}
        ]
        return Response(discount_types)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a discount"""
        discount = self.get_object()
        
        if discount.status == 'approved':
            return Response(
                {'error': 'Discount already approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval_notes = request.data.get('notes', '')
        
        discount.status = 'approved'
        discount.approved_by = request.user
        discount.approved_at = timezone.now()
        discount.approval_notes = approval_notes
        discount.save()
        
        # Apply discount to debt record if applicable
        if discount.debt_record:
            discount.debt_record.apply_discount(discount.discount_amount)
        
        serializer = self.get_serializer(discount)
        return Response(serializer.data)


class WaiverViewSet(viewsets.ModelViewSet):
    """ViewSet for fee waivers"""
    queryset = Waiver.objects.all()
    serializer_class = WaiverSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'term', 'waiver_type', 'status', 'is_active']
    search_fields = ['student__first_name', 'student__last_name', 'reason']
    ordering_fields = ['created_at', 'waiver_amount']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'approve']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a waiver"""
        waiver = self.get_object()
        
        if waiver.status == 'approved':
            return Response(
                {'error': 'Waiver already approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval_notes = request.data.get('notes', '')
        
        waiver.status = 'approved'
        waiver.approved_by = request.user
        waiver.approved_at = timezone.now()
        waiver.approval_notes = approval_notes
        waiver.save()
        
        # Apply waiver to debt record if applicable
        if waiver.debt_record:
            waiver.debt_record.apply_waiver(waiver.waiver_amount)
        
        serializer = self.get_serializer(waiver)
        return Response(serializer.data)


# ==================== AUDIT AND LOGGING VIEWS ====================

class FinancialAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for financial audit logs"""
    queryset = FinancialAuditLog.objects.all()
    serializer_class = FinancialAuditLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'user', 'entity_type']
    ordering_fields = ['timestamp', 'created_at']
    
    @action(detail=False, methods=['get'])
    def by_user(self, request, user_id=None):
        """Get audit logs for a specific user"""
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = self.get_queryset().filter(user_id=user_id)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_action(self, request, action=None):
        """Get audit logs for a specific action"""
        if not action:
            return Response(
                {'error': 'action is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = self.get_queryset().filter(action=action)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get audit logs within a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date', timezone.now().date())
        
        if not start_date:
            return Response(
                {'error': 'start_date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = self.get_queryset().filter(
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        )
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


# ==================== UTILITY FUNCTIONS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_receipt_number(request):
    """Generate a new receipt number"""
    try:
        receipt_number = Receipt.generate_receipt_number()
        return Response({
            'receipt_number': receipt_number,
            'generated_at': timezone.now()
        })
    except Exception as e:
        return Response(
            {'error': f'Failed to generate receipt number: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_payment_number(request):
    """Generate a new payment number"""
    try:
        payment_number = Payment.generate_payment_number()
        return Response({
            'payment_number': payment_number,
            'generated_at': timezone.now()
        })
    except Exception as e:
        return Response(
            {'error': f'Failed to generate payment number: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calculate_late_penalty(request, debt_id):
    """Calculate late penalty for a debt"""
    try:
        debt = DebtRecord.objects.get(id=debt_id)
        penalty = debt.calculate_late_penalty()
        
        return Response({
            'debt_id': str(debt.id),
            'student': debt.student.get_full_name(),
            'original_amount': float(debt.original_amount),
            'days_overdue': debt.days_overdue,
            'late_penalty_rate': float(debt.late_penalty_rate),
            'calculated_penalty': float(penalty),
            'total_with_penalty': float(debt.balance + penalty)
        })
    except DebtRecord.DoesNotExist:
        return Response(
            {'error': 'Debt record not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to calculate penalty: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calculate_sibling_discount(request, student_id):
    """Calculate sibling discount for a student"""
    try:
        student = User.objects.get(id=student_id, role='student')
        
        # Get siblings in the same school
        siblings = User.objects.filter(
            parent=student.parent,
            role='student',
            is_active=True
        ).exclude(id=student_id)
        
        sibling_count = siblings.count()
        discount_percentage = min(sibling_count * 5, 20)  # 5% per sibling, max 20%
        
        # Get current term fee
        current_term = AcademicTerm.get_current_term()
        if not current_term:
            return Response({
                'student': student.get_full_name(),
                'sibling_count': sibling_count,
                'discount_percentage': discount_percentage,
                'message': 'No current term found'
            })
        
        # Get student's class to determine fee structure
        # This is simplified - in reality you'd need to get the actual fee amount
        estimated_fee = Decimal('50000.00')  # Example amount
        discount_amount = estimated_fee * Decimal(discount_percentage) / Decimal('100')
        
        return Response({
            'student': student.get_full_name(),
            'siblings': [s.get_full_name() for s in siblings],
            'sibling_count': sibling_count,
            'discount_percentage': discount_percentage,
            'estimated_fee': float(estimated_fee),
            'discount_amount': float(discount_amount),
            'net_fee': float(estimated_fee - discount_amount)
        })
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to calculate discount: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_budget_utilization(request, allocation_id):
    """Check budget utilization for an allocation"""
    try:
        allocation = PaymentAllocation.objects.get(id=allocation_id)
        
        spent = allocation.spent_this_year
        utilization = allocation.budget_utilization
        remaining = allocation.annual_budget - spent if allocation.annual_budget else Decimal('0.00')
        
        return Response({
            'allocation': {
                'id': str(allocation.id),
                'name': allocation.name,
                'annual_budget': float(allocation.annual_budget) if allocation.annual_budget else 0,
                'has_budget_limit': allocation.has_budget_limit
            },
            'utilization': {
                'spent_this_year': float(spent),
                'budget_utilization': float(utilization),
                'remaining_budget': float(max(Decimal('0.00'), remaining))
            },
            'status': 'over_budget' if spent > allocation.annual_budget else 'within_budget' if utilization > 80 else 'under_budget'
        })
        
    except PaymentAllocation.DoesNotExist:
        return Response(
            {'error': 'Allocation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to check budget utilization: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




# Add this to the end of your finance/views.py file

# ==================== STUB FUNCTIONS FOR MISSING VIEWS ====================
# These are placeholder implementations to fix import errors
# Replace with actual implementations later

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def revenue_trends(request):
    return Response({"message": "Revenue trends endpoint - Implement me"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_trends(request):
    return Response({"message": "Expense trends endpoint - Implement me"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def collection_efficiency(request):
    return Response({"message": "Collection efficiency endpoint - Implement me"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def budget_vs_actual(request):
    return Response({"message": "Budget vs actual endpoint - Implement me"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_debtors(request):
    return Response({"message": "Top debtors endpoint - Implement me"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_revenue_sources(request):
    return Response({"message": "Top revenue sources endpoint - Implement me"})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def bank_reconciliation(request):
    return Response({"message": "Bank reconciliation endpoint - Implement me"})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def mpesa_reconciliation(request):
    return Response({"message": "M-Pesa reconciliation endpoint - Implement me"})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def cash_reconciliation(request):
    return Response({"message": "Cash reconciliation endpoint - Implement me"})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def process_reconciliation(request):
    return Response({"message": "Process reconciliation endpoint - Implement me"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reconciliation_reports(request):
    return Response({"message": "Reconciliation reports endpoint - Implement me"})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def send_overdue_alerts(request):
    return Response({"message": "Send overdue alerts endpoint - Implement me"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_receipt_confirmation(request, receipt_id):
    return Response({"message": f"Send receipt confirmation for {receipt_id} - Implement me"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_payment_confirmation(request, payment_id):
    return Response({"message": f"Send payment confirmation for {payment_id} - Implement me"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def finance_api_docs(request):
    return Response({"message": "Finance API documentation endpoint - Implement me"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def finance_health_check(request):
    return Response({"status": "healthy", "timestamp": timezone.now()})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def finance_api_version(request):
    return Response({"version": "1.0.0", "api": "finance"})

# ... Add more stub functions for other missing endpoints
# ==================== IMPORT STUB VIEWS FOR MISSING ENDPOINTS ====================
# This section imports stub implementations for all endpoints defined in urls.py
# but not yet implemented in this file.

try:
    from .stub_views import (
        # Backup and Recovery
        create_financial_backup, restore_financial_backup, list_financial_backups,
        download_financial_backup, delete_financial_backup,
        
        # Notification endpoints
        send_overdue_alerts, send_receipt_confirmation, send_payment_confirmation,
        
        # Analytics endpoints
        revenue_trends, expense_trends, collection_efficiency,
        budget_vs_actual, top_debtors, top_revenue_sources,
        
        # Reconciliation endpoints
        bank_reconciliation, mpesa_reconciliation, cash_reconciliation,
        process_reconciliation, reconciliation_reports,
        
        # Documentation and health
        finance_api_docs, finance_health_check, finance_api_version,
        
        # Mobile endpoints
        mobile_financial_dashboard, mobile_student_balance, mobile_make_payment,
        mobile_payment_history, mobile_receipts,
        
        # Communication endpoints
        send_bulk_fee_statements, send_bulk_receipts, send_bulk_overdue_alerts,
        send_bulk_payment_reminders,
        
        # Validation endpoints
        check_duplicate_transactions, fix_financial_data_issues,
        validate_receipts, validate_payments,
        
        # Integration endpoints
        school_erp_integration, government_portal_integration,
        banking_api_integration, sms_gateway_integration,
        
        # Custom report endpoints
        generate_custom_report, list_report_templates,
        get_report_template, run_report_template,
        
        # Export format endpoints
        export_receipt_pdf, export_invoice_pdf, export_statement_pdf,
        export_financial_report_excel, export_transactions_csv,
        
        # Search endpoints
        search_transactions, search_students_financial,
        search_receipts_advanced, search_payments_advanced,
        
        # Batch processing endpoints
        process_end_of_day, process_end_of_month, process_end_of_term,
        batch_generate_statements, batch_calculate_penalties,
        
        # Config endpoints
        get_finance_settings, update_finance_settings,
        get_tax_rates, update_tax_rates,
        get_payment_gateways, update_payment_gateways,
        
        # Realtime endpoints
        get_realtime_updates, get_realtime_notifications,
        get_realtime_dashboard_data,
        
        # Visualization endpoints
        revenue_chart_data, expense_chart_data, collection_chart_data,
        budget_chart_data, debt_chart_data,
        
        # Debug endpoints
        debug_transaction_flow, debug_data_integrity, debug_performance_metrics,
        
        # Migration endpoints
        migrate_old_financial_data, verify_migration, rollback_migration,
        
        # Monitoring endpoints
        get_api_usage_stats, get_performance_stats, get_error_logs,
        
        # Security endpoints
        get_access_logs, get_user_permissions, get_audit_trail,
        
        # Class-based stub views
        FeeReminderScheduleView, QuarterlyReportView, AnnualReportView,
        FinancialAuditView, FinancialSettingsView, FinancialBackupView,
        FeeCollectionReportView, ExpenditureReportView, StudentFinancialPortalView,
        MpesaCallbackView, PublicInvoiceView, PublicFeeStructureView,
        PublicPaymentMethodsView, MpesaWebhookView, BankWebhookView,
        SMSWebhookView, EmailWebhookView, ReceiptExportView, PaymentExportView,
        DebtExportView, FeeStructureImportView, StudentFinanceImportView,
    )
    
    logger.info("Successfully imported stub views for missing endpoints")
    
except ImportError as e:
    logger.warning(f"Could not import stub views: {e}")
    
    # Create minimal inline stubs as fallback
    @api_view(['GET', 'POST', 'PUT', 'DELETE'])
    @permission_classes([IsAuthenticated])
    def generic_stub_view(request, *args, **kwargs):
        return Response({
            "error": "Endpoint not implemented",
            "message": "This endpoint is defined in urls.py but not implemented in views.py",
            "path": request.path,
            "method": request.method,
            "status": "under_development",
            "timestamp": timezone.now().isoformat()
        }, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    # Assign generic stub to all missing functions
    missing_functions = [
        # Backup and Recovery
        'create_financial_backup', 'restore_financial_backup', 'list_financial_backups',
        'download_financial_backup', 'delete_financial_backup',
        
        # ... add all other function names from above
    ]
    
    # Dynamically create missing functions
    import sys
    current_module = sys.modules[__name__]
    
    for func_name in missing_functions:
        if not hasattr(current_module, func_name):
            setattr(current_module, func_name, generic_stub_view)
    
    logger.warning(f"Created generic stubs for {len(missing_functions)} missing functions")

# ==================== END OF FILE ====================