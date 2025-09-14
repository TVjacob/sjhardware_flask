from flask import Blueprint, request, jsonify
from app import db
from app.models import Account
from datetime import datetime

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')

# --- Add new account ---
@accounts_bp.route('/', methods=['POST'])
def add_account():
    data = request.json
    account = Account(
        name=data['name'],
        code=data['code'],
        account_type=data['account_type'],
        description=data.get('description'),
        status=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(account)
    db.session.commit()
    return jsonify({"message": "Account added", "account_id": account.id}), 201


# --- Get all accounts ---
@accounts_bp.route('/', methods=['GET'])
def get_accounts():
    accounts = Account.query.all()
    data = [{
        "id": a.id,
        "name": a.name,
        "code": a.code,
        "account_type": a.account_type,
        "description": a.description,
        "status": a.status,
        "created_at": a.created_at,
        "updated_at": a.updated_at
    } for a in accounts]
    return jsonify(data)


# --- Get account by ID ---
@accounts_bp.route('/<int:id>', methods=['GET'])
def get_account(id):
    a = Account.query.get_or_404(id)
    return jsonify({
        "id": a.id,
        "name": a.name,
        "code": a.code,
        "account_type": a.account_type,
        "description": a.description,
        "status": a.status,
        "created_at": a.created_at,
        "updated_at": a.updated_at
    })


# --- Update account ---
@accounts_bp.route('/<int:id>', methods=['PUT'])
def update_account(id):
    a = Account.query.get_or_404(id)
    data = request.json
    a.name = data.get('name', a.name)
    a.code = data.get('code', a.code)
    a.account_type = data.get('account_type', a.account_type)
    a.description = data.get('description', a.description)
    a.updated_at = datetime.utcnow()
    a.status = 1
    db.session.commit()
    return jsonify({"message": "Account updated", "account_id": a.id})


# --- Delete account (soft delete) ---
@accounts_bp.route('/<int:id>', methods=['DELETE'])
def delete_account(id):
    a = Account.query.get_or_404(id)
    a.status = 0
    a.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Account marked inactive", "account_id": id})


# --- Seed predefined chart of accounts ---
@accounts_bp.route('/seed', methods=['POST'])
def seed_accounts():
    """
    Inserts a predefined chart of accounts into the database.
    Avoids duplicates by checking account code.
    """
    predefined_accounts = [
        # Assets
        {"code": "1000", "name": "Cash", "account_type": "Asset", "description": "Cash on hand"},
        {"code": "1100", "name": "Accounts Receivable", "account_type": "Asset", "description": "Money owed by customers"},
        {"code": "1200", "name": "Inventory", "account_type": "Asset", "description": "Products available for sale"},
        {"code": "1300", "name": "Prepaid Expenses", "account_type": "Asset", "description": "Expenses paid in advance"},

        # Liabilities
        {"code": "2000", "name": "Accounts Payable", "account_type": "Liability", "description": "Money owed to suppliers"},
        {"code": "2100", "name": "Accrued Liabilities", "account_type": "Liability", "description": "Expenses incurred but not paid"},

        # Equity
        {"code": "3000", "name": "Owner's Equity", "account_type": "Equity", "description": "Owner's capital account"},
        {"code": "3100", "name": "Retained Earnings", "account_type": "Equity", "description": "Accumulated profits"},

        # Revenue
        {"code": "4000", "name": "Sales Revenue", "account_type": "Revenue", "description": "Revenue from sales"},
        {"code": "4100", "name": "Service Revenue", "account_type": "Revenue", "description": "Revenue from services"},

        # Expenses
        {"code": "5000", "name": "Cost of Goods Sold", "account_type": "Expense", "description": "Direct costs of goods sold"},
        {"code": "5100", "name": "Rent Expense", "account_type": "Expense", "description": "Rent costs"},
        {"code": "5200", "name": "Salaries Expense", "account_type": "Expense", "description": "Salaries and wages"},
        {"code": "5300", "name": "Utilities Expense", "account_type": "Expense", "description": "Electricity, water, etc."}
    ]

    added_accounts = []
    skipped_accounts = []

    for acc in predefined_accounts:
        existing = Account.query.filter_by(code=acc["code"]).first()
        if not existing:
            new_account = Account(
                name=acc["name"],
                code=acc["code"],
                account_type=acc["account_type"],
                description=acc.get("description"),
                status=1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(new_account)
            added_accounts.append(acc["name"])
        else:
            skipped_accounts.append(acc["name"])

    db.session.commit()

    return jsonify({
        "message": "Chart of Accounts seeded",
        "added_accounts": added_accounts,
        "skipped_accounts": skipped_accounts
    })
