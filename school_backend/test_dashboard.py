import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_backend.settings')
sys.path.insert(0, os.getcwd())

django.setup()

from datetime import date
from decimal import Decimal
from finance.models import FinancialDashboard

print("Testing FinancialDashboard model...")

# Try to create a dashboard
try:
    today = date.today()
    
    # Delete any existing dashboard for today
    FinancialDashboard.objects.filter(dashboard_date=today).delete()
    
    # Create new dashboard
    dashboard = FinancialDashboard.objects.create(
        dashboard_date=today,
        total_receipts_today=Decimal('50000.00'),
        total_payments_today=Decimal('25000.00'),
        cash_balance=Decimal('25000.00'),
        fee_collection_rate=Decimal('85.50'),
        outstanding_debt=Decimal('150000.00'),
        pending_approvals=3,
        is_current=True
    )
    
    print(f"✓ Dashboard created successfully")
    print(f"  ID: {dashboard.id}")
    print(f"  Date: {dashboard.dashboard_date}")
    print(f"  Receipts: {dashboard.total_receipts_today}")
    print(f"  Payments: {dashboard.total_payments_today}")
    print(f"  Cash Balance: {dashboard.cash_balance}")
    print(f"  Collection Rate: {dashboard.fee_collection_rate}")
    print(f"  Outstanding Debt: {dashboard.outstanding_debt}")
    
    # Test refresh_metrics
    try:
        dashboard.refresh_metrics()
        print(f"✓ refresh_metrics() executed successfully")
    except Exception as e:
        print(f"⚠ refresh_metrics() failed: {e}")
    
    # Test get_or_create
    dashboard2, created = FinancialDashboard.objects.get_or_create(
        dashboard_date=today,
        defaults={
            'total_receipts_today': Decimal('0.00'),
            'total_payments_today': Decimal('0.00'),
            'cash_balance': Decimal('0.00'),
        }
    )
    print(f"\n✓ get_or_create test:")
    print(f"  Created new: {created}")
    print(f"  Retrieved ID: {dashboard2.id}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
