# from app import create_app

# app = create_app()

# if __name__ == '__main__':
#     app.run(debug=True)
from app import create_app, db
from app.models import Account
from datetime import datetime

app = create_app()

def seed_chart_of_accounts():
    """
    Runs at startup to check if essential chart of accounts exists,
    and creates them if missing.
    """
    predefined_accounts = [
        # -------------------------
        # ASSETS
        # -------------------------
        {"code": "1000", "name": "Cash on Hand", "account_type": "Asset", "description": "Physical cash kept at the premises"},
        {"code": "1010", "name": "Petty Cash", "account_type": "Asset", "description": "Small amount of cash for minor expenses"},

        # Mobile Money Accounts
        {"code": "1020", "name": "MTN Mobile Money", "account_type": "Asset", "description": "MTN mobile money account balance"},
        {"code": "1030", "name": "Airtel Money", "account_type": "Asset", "description": "Airtel mobile money account balance"},
        {"code": "1040", "name": "Other Mobile Wallets", "account_type": "Asset", "description": "Balances in other mobile wallets"},

        # Bank Accounts
        {"code": "1050", "name": "Stanbic Bank Account", "account_type": "Asset", "description": "Primary Stanbic bank account balance"},
        {"code": "1060", "name": "Equity Bank Account", "account_type": "Asset", "description": "Equity bank account balance"},
        {"code": "1070", "name": "Centenary Bank Account", "account_type": "Asset", "description": "Centenary bank account balance"},
        {"code": "1080", "name": "Other Bank Accounts", "account_type": "Asset", "description": "Other secondary bank accounts"},

        # Accounts Receivable
        {"code": "1100", "name": "Accounts Receivable", "account_type": "Asset", "description": "Money owed by customers"},
        {"code": "1110", "name": "Employee Advances", "account_type": "Asset", "description": "Cash advances given to employees"},

        # Inventory & Prepaid
        {"code": "1200", "name": "Inventory", "account_type": "Asset", "description": "Products available for sale"},
        {"code": "1300", "name": "Prepaid Expenses", "account_type": "Asset", "description": "Expenses paid in advance"},
        {"code": "1400", "name": "Fixed Assets", "account_type": "Asset", "description": "Property, plant, and equipment"},

        # -------------------------
        # LIABILITIES
        # -------------------------
        {"code": "2000", "name": "Accounts Payable", "account_type": "Liability", "description": "Money owed to suppliers"},
        {"code": "2100", "name": "Accrued Expenses", "account_type": "Liability", "description": "Expenses incurred but not yet paid"},
        {"code": "2200", "name": "Taxes Payable", "account_type": "Liability", "description": "Outstanding tax obligations"},
        {"code": "2300", "name": "Wages Payable", "account_type": "Liability", "description": "Wages owed to employees"},
        {"code": "2400", "name": "Loan Payable", "account_type": "Liability", "description": "Outstanding business loans"},
        {"code": "2500", "name": "Mobile Money Payable", "account_type": "Liability", "description": "Mobile money amounts owed to customers or suppliers"},
        {"code": "2600", "name": "Credit Card Payable", "account_type": "Liability", "description": "Outstanding balances on business credit cards"},

        # -------------------------
        # EQUITY
        # -------------------------
        {"code": "3000", "name": "Owner's Equity", "account_type": "Equity", "description": "Owner's capital contribution"},
        {"code": "3100", "name": "Retained Earnings", "account_type": "Equity", "description": "Accumulated profits kept in the business"},
        {"code": "3200", "name": "Drawings", "account_type": "Equity", "description": "Owner withdrawals for personal use"},

        # -------------------------
        # REVENUE
        # -------------------------
        {"code": "4000", "name": "Sales Revenue", "account_type": "Revenue", "description": "Revenue from sale of goods"},
        {"code": "4100", "name": "Service Revenue", "account_type": "Revenue", "description": "Revenue from services rendered"},
        {"code": "4200", "name": "Mobile Money Income", "account_type": "Revenue", "description": "Revenue received via mobile money transactions"},
        {"code": "4300", "name": "Bank Transfer Income", "account_type": "Revenue", "description": "Revenue received through bank transfers"},
        {"code": "4400", "name": "Other Income", "account_type": "Revenue", "description": "Miscellaneous income sources"},

        # -------------------------
        # EXPENSES
        # -------------------------

        # Cost of Sales
        {"code": "5000", "name": "Cost of Goods Sold", "account_type": "Expense", "description": "Direct cost of goods sold"},

        # Operating Expenses
        {"code": "5100", "name": "Rent Expense", "account_type": "Expense", "description": "Rental payments for premises"},
        {"code": "5200", "name": "Salaries & Wages Expense", "account_type": "Expense", "description": "Employee salaries and wages"},
        {"code": "5210", "name": "Overtime Expense", "account_type": "Expense", "description": "Extra pay for employee overtime"},
        {"code": "5220", "name": "Employee Benefits Expense", "account_type": "Expense", "description": "Benefits like health insurance and allowances"},
        {"code": "5300", "name": "Utilities Expense", "account_type": "Expense", "description": "Electricity, water, internet, etc."},

        # Office & Cleaning
        {"code": "5400", "name": "Office Supplies Expense", "account_type": "Expense", "description": "Office supplies and consumables"},
        {"code": "5410", "name": "Cleaning Supplies Expense", "account_type": "Expense", "description": "Cleaning supplies and detergents"},
        {"code": "5420", "name": "Waste Management Expense", "account_type": "Expense", "description": "Garbage collection and disposal fees"},

        # Maintenance & Repairs
        {"code": "5500", "name": "Repairs & Maintenance Expense", "account_type": "Expense", "description": "Repair and maintenance costs for equipment or facilities"},
        {"code": "5510", "name": "IT Maintenance Expense", "account_type": "Expense", "description": "Software updates, system maintenance, and IT repairs"},

        # Financial & Administrative
        {"code": "5600", "name": "Depreciation Expense", "account_type": "Expense", "description": "Depreciation of fixed assets"},
        {"code": "5610", "name": "Insurance Expense", "account_type": "Expense", "description": "Business insurance premiums"},
        {"code": "5620", "name": "Bank Charges Expense", "account_type": "Expense", "description": "Bank service charges and fees"},
        {"code": "5630", "name": "Mobile Money Charges Expense", "account_type": "Expense", "description": "Transaction fees for mobile money services"},
        {"code": "5640", "name": "Credit Card Fees Expense", "account_type": "Expense", "description": "Credit card processing fees"},

        # Marketing & Advertising
        {"code": "5700", "name": "Advertising Expense", "account_type": "Expense", "description": "Marketing and advertising costs"},
        {"code": "5710", "name": "Promotional Expense", "account_type": "Expense", "description": "Discounts and promotional offers"},

        # Travel & Miscellaneous
        {"code": "5800", "name": "Travel Expense", "account_type": "Expense", "description": "Travel and transportation expenses"},
        {"code": "5810", "name": "Training Expense", "account_type": "Expense", "description": "Employee training and development costs"},
        {"code": "5820", "name": "Miscellaneous Expense", "account_type": "Expense", "description": "Any other minor expenses"}
    ]


    with app.app_context():
        added_accounts = []
        skipped_accounts = []

        for acc in predefined_accounts:
            exists = Account.query.filter_by(code=acc["code"]).first()
            if not exists:
                new_account = Account(
                    name=acc["name"],
                    code=acc["code"],
                    account_type=acc["account_type"],
                    description=acc["description"],
                    status=1,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_account)
                added_accounts.append(acc["name"])
            else:
                skipped_accounts.append(acc["name"])

        if added_accounts:
            db.session.commit()
            print(f"✅ Added {len(added_accounts)} new accounts: {', '.join(added_accounts)}")
        else:
            print("ℹ️ All predefined accounts already exist.")

# --- Run the app and seed data ---
if __name__ == '__main__':
    seed_chart_of_accounts()
    app.run(debug=True)
