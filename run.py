from app import create_app, db
from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError, OperationalError, IntegrityError
from sqlalchemy import text

from app.models import AssetSubtypeEnum, EquitySubtypeEnum, ExpenseSubtypeEnum, LiabilitySubtypeEnum, RevenueSubtypeEnum
from datetime import datetime, timezone

app = create_app()


# Mapping of accounts with proper enum subtypes and parent_id
account_updates = [
    {"id": 1, "account_subtype": AssetSubtypeEnum.CASH, "parent_id": None},   # Cash on Hand
    {"id": 2, "account_subtype": AssetSubtypeEnum.CASH, "parent_id": 1},      # Petty Cash
    {"id": 3, "account_subtype": AssetSubtypeEnum.CASH, "parent_id": 1},      # MTN Mobile Money
    {"id": 4, "account_subtype": AssetSubtypeEnum.CASH, "parent_id": 1},      # Airtel Money
    {"id": 5, "account_subtype": AssetSubtypeEnum.CASH, "parent_id": 1},      # Other Mobile Wallets
    {"id": 6, "account_subtype": AssetSubtypeEnum.BANK, "parent_id": None}, # Stanbic Bank Account
    {"id": 7, "account_subtype": AssetSubtypeEnum.BANK, "parent_id": None}, # Equity Bank Account
    {"id": 8, "account_subtype": AssetSubtypeEnum.BANK, "parent_id": None}, # Centenary Bank Account
    {"id": 9, "account_subtype": AssetSubtypeEnum.BANK, "parent_id": None}, # Other Bank Accounts
    {"id": 10, "account_subtype": AssetSubtypeEnum.ACCOUNTS_RECEIVABLE, "parent_id": None}, # Accounts Receivable
    {"id": 11, "account_subtype": AssetSubtypeEnum.PREPAID_EXPENSES, "parent_id": None},     # Employee Advances
    {"id": 12, "account_subtype": AssetSubtypeEnum.INVENTORY, "parent_id": None}, # Inventory
    {"id": 13, "account_subtype": AssetSubtypeEnum.PREPAID_EXPENSES, "parent_id": None}, # Prepaid Expenses
    {"id": 14, "account_subtype": AssetSubtypeEnum.FIXED_ASSET, "parent_id": None}, # Fixed Assets
    {"id": 15, "account_subtype": LiabilitySubtypeEnum.ACCOUNTS_PAYABLE, "parent_id": None}, # Accounts Payable
    {"id": 16, "account_subtype": LiabilitySubtypeEnum.ACCRUED_LIABILITIES, "parent_id": None}, # Accrued Expenses
    {"id": 17, "account_subtype": LiabilitySubtypeEnum.ACCRUED_LIABILITIES, "parent_id": None}, # Taxes Payable
    {"id": 18, "account_subtype": LiabilitySubtypeEnum.ACCRUED_LIABILITIES, "parent_id": None}, # Wages Payable
    {"id": 19, "account_subtype": LiabilitySubtypeEnum.LONG_TERM_DEBT, "parent_id": None}, # Loan Payable
    {"id": 20, "account_subtype": LiabilitySubtypeEnum.ACCOUNTS_PAYABLE, "parent_id": None}, # Mobile Money Payable
    {"id": 21, "account_subtype": LiabilitySubtypeEnum.ACCOUNTS_PAYABLE, "parent_id": None}, # Credit Card Payable
    {"id": 22, "account_subtype": EquitySubtypeEnum.OWNERS_EQUITY, "parent_id": None}, # Owner's Equity
    {"id": 23, "account_subtype": EquitySubtypeEnum.RETAINED_EARNINGS, "parent_id": None}, # Retained Earnings
    {"id": 24, "account_subtype": EquitySubtypeEnum.OWNERS_EQUITY, "parent_id": None}, # Drawings
    {"id": 25, "account_subtype": RevenueSubtypeEnum.SALES, "parent_id": None}, # Sales Revenue
    {"id": 26, "account_subtype": RevenueSubtypeEnum.SERVICE, "parent_id": 25}, # Service Revenue
    {"id": 27, "account_subtype": RevenueSubtypeEnum.SERVICE, "parent_id": 25}, # Mobile Money Income
    {"id": 28, "account_subtype": RevenueSubtypeEnum.SERVICE, "parent_id": 25}, # Bank Transfer Income
    {"id": 29, "account_subtype": RevenueSubtypeEnum.SERVICE, "parent_id": 25}, # Other Income
    {"id": 30, "account_subtype": ExpenseSubtypeEnum.COGS, "parent_id": None}, # Cost of Goods Sold
    {"id": 31, "account_subtype": ExpenseSubtypeEnum.RENT, "parent_id": None}, # Rent Expense
    {"id": 32, "account_subtype": ExpenseSubtypeEnum.SALARIES, "parent_id": None}, # Salaries & Wages Expense
    {"id": 33, "account_subtype": ExpenseSubtypeEnum.SALARIES, "parent_id": 32}, # Overtime Expense
    {"id": 34, "account_subtype": ExpenseSubtypeEnum.SALARIES, "parent_id": 32}, # Employee Benefits Expense
    {"id": 35, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Utilities Expense
    {"id": 36, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Office Supplies Expense
    {"id": 37, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": 36},   # Cleaning Supplies Expense
    {"id": 38, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Waste Management Expense
    {"id": 39, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Repairs & Maintenance Expense
    {"id": 40, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # IT Maintenance Expense
    {"id": 41, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Depreciation Expense
    {"id": 42, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Insurance Expense
    {"id": 43, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Bank Charges Expense
    {"id": 44, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Mobile Money Charges Expense
    {"id": 45, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Credit Card Fees Expense
    {"id": 46, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Advertising Expense
    {"id": 47, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": 46},   # Promotional Expense
    {"id": 48, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Travel Expense
    {"id": 49, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Training Expense
    {"id": 50, "account_subtype": ExpenseSubtypeEnum.UTILITIES, "parent_id": None}, # Miscellaneous Expense
]


def update_all_accounts():
    try:
        for acc in account_updates:
            account = Account.query.filter_by(id=acc["id"]).first()
            if account:
                # Convert enum to string
                subtype = acc.get("account_subtype")
                if subtype:
                    account.account_subtype = subtype.value  # <-- key change
                account.parent_id = acc.get("parent_id")
                account.updated_at = datetime.now(timezone.utc)  # timezone-aware
        db.session.commit()
        print("✅ All 50 accounts updated successfully with ENUM subtypes and parent_id references.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to update accounts: {e}")



def normalize_account_type_enum_uppercase():
    print("🔄 Converting account_type to uppercase enum...")

    with app.app_context():
        try:
            db.session.execute(text("""
                ALTER TYPE accounttypeenum RENAME TO accounttypeenum_old;
            """))
            db.session.execute(text("""
                CREATE TYPE accounttypeenum AS ENUM ('ASSET','LIABILITY','EQUITY','REVENUE','EXPENSE');
            """))
            db.session.execute(text("""
                ALTER TABLE account
                ALTER COLUMN account_type TYPE accounttypeenum
                USING UPPER(account_type::text)::accounttypeenum;
            """))
            db.session.execute(text("""
                DROP TYPE accounttypeenum_old;
            """))
            db.session.commit()
            print("✅ account_type is now uppercase and enum-safe.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Failed to normalize account_type: {e}")



def create_default_admin():
    """Create a default admin user if not already present."""
    existing_user = User.query.filter_by(username='admin').first()
    if existing_user:
        print("ℹ️ Admin user already exists.")
        return

    try:
        admin = User(
            username='admin',
            role='Admin',
            password_hash=generate_password_hash('123456')
        )

        # Assign all permissions
        for perm in Permission.query.all():
            admin.add_permission(perm)

        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin user created (Username: admin | Password: 123456)")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"❌ Failed to create admin user: {e}")


def fix_missing_purchase_order_transactions():
    """Fix purchase orders missing transaction_no."""
    missing = PurchaseOrder.query.filter_by(transaction_no=None).all()
    if not missing:
        print("ℹ️ No purchase orders with missing transaction numbers.")
        return

    for po in missing:
        po.update_totals()
        total = po.total_amount

        entries = [
            {"account_id": 1200, "transaction_type": "Debit", "amount": total},
            {"account_id": 2100, "transaction_type": "Credit", "amount": total},
        ]

        txn_id, _ = generate_transaction_number("CREDIT-PAY", transaction_date=po.purchase_date)
        po.transaction_no = txn_id

        post_to_ledger(
            entries,
            transaction_no_id=txn_id,
            description=f"Credit for PO #{po.id}",
            transaction_date=po.purchase_date
        )

        db.session.add(po)

    try:
        db.session.commit()
        print(f"✅ Fixed {len(missing)} purchase orders.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"❌ Failed to update purchase orders: {e}")


def seed_chart_of_accounts():
    """Seed and assign chart of accounts, subtypes, and parents in one pass."""
    predefined_accounts = [
        # ASSETS
        {"code": "1000", "name": "Cash on Hand", "account_type": "ASSET", "description": "Physical cash kept at the premises"},
        {"code": "1010", "name": "Petty Cash", "account_type": "ASSET", "description": "Small cash for expenses"},
        {"code": "1020", "name": "MTN Mobile Money", "account_type": "ASSET", "description": "MTN mobile money balance"},
        {"code": "1030", "name": "Airtel Money", "account_type": "ASSET", "description": "Airtel mobile money balance"},
        {"code": "1040", "name": "Other Mobile Wallets", "account_type": "ASSET", "description": "Other wallet balances"},
        {"code": "1050", "name": "Stanbic Bank Account", "account_type": "ASSET", "description": "Stanbic bank account balance"},
        {"code": "1060", "name": "Equity Bank Account", "account_type": "ASSET", "description": "Equity bank account balance"},
        {"code": "1070", "name": "Centenary Bank Account", "account_type": "ASSET", "description": "Centenary bank account balance"},
        {"code": "1080", "name": "Other Bank Accounts", "account_type": "ASSET", "description": "Secondary bank accounts"},
        {"code": "1100", "name": "Accounts Receivable", "account_type": "ASSET", "description": "Money owed by customers"},
        {"code": "1200", "name": "Inventory", "account_type": "ASSET", "description": "Goods available for sale"},
        {"code": "1400", "name": "Fixed Assets", "account_type": "ASSET", "description": "Property, plant, and equipment"},
        # LIABILITIES
        {"code": "2000", "name": "Accounts Payable", "account_type": "LIABILITY", "description": "Money owed to suppliers"},
        {"code": "2100", "name": "Accrued Expenses", "account_type": "LIABILITY", "description": "Expenses incurred but unpaid"},
        # EQUITY
        {"code": "3000", "name": "Owner's Equity", "account_type": "EQUITY", "description": "Owner capital"},
        # REVENUE
        {"code": "4000", "name": "Sales Revenue", "account_type": "REVENUE", "description": "Sales income"},
        # EXPENSE
        {"code": "5000", "name": "Cost of Goods Sold", "account_type": "EXPENSE", "description": "Direct cost of sales"},
    ]

    subtype_map = {
        "ASSET": {"1000": "Cash", "1010": "Cash", "1050": "Bank"},
        "LIABILITY": {"2000": "Current Liability", "2100": "Accrued"},
        "EQUITY": {"3000": "Owner Equity"},
        "REVENUE": {"4000": "Sales"},
        "EXPENSE": {"5000": "COGS"},
    }

    parent_map = {"1000": None, "2000": None, "3000": None, "4000": None, "5000": None}

    existing = {a.code: a for a in Account.query.all()}
    added = []

    for acc in predefined_accounts:
        if acc["code"] in existing:
            continue

        new_acc = Account(
            name=acc["name"],
            code=acc["code"],
            account_type=acc["account_type"],
            description=acc["description"],
            status=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        subtype = subtype_map.get(acc["account_type"], {}).get(acc["code"])
        if subtype:
            new_acc.account_subtype = subtype

        if acc["code"] not in parent_map:
            parent_code = str(int(acc["code"]) // 1000 * 1000)
            parent = existing.get(parent_code)
            if parent:
                new_acc.parent_id = parent.id

        db.session.add(new_acc)
        existing[acc["code"]] = new_acc
        added.append(acc["name"])

    try:
        db.session.commit()
        print(f"✅ Seeded {len(added)} new accounts.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"❌ Failed to seed accounts: {e}")


if __name__ == "__main__":
    with app.app_context():
        from app.models import Account, PurchaseOrder, User, Permission
        from app.utils.gl_utils import generate_transaction_number, post_to_ledger
        update_all_accounts()
        normalize_account_type_enum_uppercase()
        seed_chart_of_accounts()
        create_default_admin()
        fix_missing_purchase_order_transactions()

    app.run(debug=True)
