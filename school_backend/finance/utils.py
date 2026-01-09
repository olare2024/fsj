# finance/utils.py
"""
Finance utility functions for Delvok Academy
"""

from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from .models import (
    Receipt, Payment, DebtRecord, PaymentStatus,
    KenyaPaymentMethod, FinancialUtils
)

logger = logging.getLogger(__name__)


def calculate_debt_penalties():
    """Calculate and apply late payment penalties for overdue debts"""
    today = timezone.now().date()
    overdue_debts = DebtRecord.objects.filter(
        is_overdue=True,
        is_active=True,
        is_reversed=False
    )
    
    updated_count = 0
    for debt in overdue_debts:
        if debt.due_date:
            overdue_days = (today - debt.due_date).days
            if overdue_days > debt.overdue_days:
                # Calculate penalty for new overdue days
                new_overdue_days = overdue_days - debt.overdue_days
                penalty_rate = Decimal('0.5')  # 0.5% per day
                penalty = debt.original_amount * (penalty_rate / 100) * new_overdue_days
                
                debt.late_penalty_applied += penalty
                debt.overdue_days = overdue_days
                debt.save()
                
                updated_count += 1
                logger.info(f"Applied penalty of {penalty} to debt {debt.id}")
    
    return updated_count


def generate_financial_report(report_type, start_date, end_date, user):
    """Generate financial report for given period"""
    from .models import FinancialReport
    
    # Calculate report data based on type
    if report_type == 'fee_collection':
        receipts = Receipt.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            status=PaymentStatus.COMPLETED
        )
        
        total_income = receipts.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        report_data = {
            'period': {'start': start_date, 'end': end_date},
            'total_income': float(total_income),
            'receipt_count': receipts.count(),
            'breakdown_by_method': list(receipts.values('paid_through').annotate(
                total=Sum('amount'),
                count=Count('id')
            )),
            'breakdown_by_allocation': list(receipts.values('paid_for__name').annotate(
                total=Sum('amount'),
                count=Count('id')
            ))
        }
        
    elif report_type == 'expenditure':
        payments = Payment.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            status=PaymentStatus.COMPLETED
        )
        
        total_expenses = payments.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        report_data = {
            'period': {'start': start_date, 'end': end_date},
            'total_expenses': float(total_expenses),
            'payment_count': payments.count(),
            'breakdown_by_category': list(payments.values('category').annotate(
                total=Sum('total_amount'),
                count=Count('id')
            )),
            'breakdown_by_allocation': list(payments.values('allocation__name').annotate(
                total=Sum('total_amount'),
                count=Count('id')
            ))
        }
    
    else:
        raise ValueError(f"Unsupported report type: {report_type}")
    
    # Create report
    report = FinancialReport.objects.create(
        report_type=report_type,
        title=f"{report_type.replace('_', ' ').title()} Report - {start_date} to {end_date}",
        description=f"Automatically generated {report_type} report",
        period_start=start_date,
        period_end=end_date,
        report_data=report_data,
        generated_by=user
    )
    
    return report


def send_payment_reminders():
    """Send payment reminders for upcoming due dates"""
    today = timezone.now().date()
    next_week = today + timedelta(days=7)
    
    upcoming_debts = DebtRecord.objects.filter(
        due_date__gte=today,
        due_date__lte=next_week,
        balance__gt=0,
        is_active=True,
        is_reversed=False
    ).select_related('student')
    
    reminders_sent = 0
    
    for debt in upcoming_debts:
        # Here you would implement actual SMS/email sending
        # This is a placeholder for the logic
        
        student = debt.student
        due_date = debt.due_date
        balance = debt.balance
        
        # Simulate sending reminder
        logger.info(f"Sending payment reminder to {student.get_full_name()} "
                   f"for balance {balance} due on {due_date}")
        
        debt.sent_reminder_sms = True
        debt.last_reminder_sent = timezone.now()
        debt.save()
        
        reminders_sent += 1
    
    return reminders_sent


def reconcile_daily_transactions(date=None):
    """Reconcile daily transactions"""
    if not date:
        date = timezone.now().date()
    
    # Get all receipts for the day
    receipts = Receipt.objects.filter(date=date, status=PaymentStatus.COMPLETED)
    
    # Get all payments for the day
    payments = Payment.objects.filter(date=date, status=PaymentStatus.COMPLETED)
    
    # Calculate totals
    total_receipts = receipts.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_payments = payments.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    reconciliation_data = {
        'date': date,
        'receipts': {
            'count': receipts.count(),
            'total': float(total_receipts),
            'by_method': list(receipts.values('paid_through').annotate(
                total=Sum('amount'),
                count=Count('id')
            ))
        },
        'payments': {
            'count': payments.count(),
            'total': float(total_payments),
            'by_category': list(payments.values('category').annotate(
                total=Sum('total_amount'),
                count=Count('id')
            ))
        },
        'net_cash_flow': float(total_receipts - total_payments),
        'reconciled_at': timezone.now(),
        'status': 'success'
    }
    
    return reconciliation_data