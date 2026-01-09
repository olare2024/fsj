# clean_finance.py
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_backend.settings')
django.setup()

from django.db import connection

sql_commands = """
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS finance_budgetitem;
DROP TABLE IF EXISTS finance_budget;
DROP TABLE IF EXISTS finance_receiptallocation;
DROP TABLE IF EXISTS finance_paymentallocation;
DROP TABLE IF EXISTS finance_feestructure;
DROP TABLE IF EXISTS finance_debtrecord;
DROP TABLE IF EXISTS finance_receipt;
DROP TABLE IF EXISTS finance_payment;
DROP TABLE IF EXISTS finance_paymentrecord;
DROP TABLE IF EXISTS finance_financialreport;
DROP TABLE IF EXISTS finance_taxconfiguration;
DROP TABLE IF EXISTS finance_compliancerecord;
DROP TABLE IF EXISTS finance_financialdashboard;
DROP TABLE IF EXISTS finance_financialsettings;
DROP TABLE IF EXISTS finance_financialauditlog;
DROP TABLE IF EXISTS finance_bankreconciliation;
DROP TABLE IF EXISTS finance_mpesareconciliation;
DROP TABLE IF EXISTS finance_installmentplan;
DROP TABLE IF EXISTS finance_discount;
DROP TABLE IF EXISTS finance_waiver;
SET FOREIGN_KEY_CHECKS = 1;

DELETE FROM django_migrations WHERE app = 'finance';
"""

with connection.cursor() as cursor:
    for command in sql_commands.split(';'):
        if command.strip():
            cursor.execute(command)

print("Finance tables and migration history cleaned successfully!")