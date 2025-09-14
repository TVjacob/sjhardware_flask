from flask import Blueprint, request, jsonify
from app import db
from app.models import Expense, GeneralLedger
from app.utils.gl_utils import post_to_ledger, generate_transaction_number
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

# --- Add new expense with GL entries ---
@expenses_bp.route('/', methods=['POST'])
def add_expense():
    data = request.json
    amount = data['amount']
    expense = Expense(
        description=data['description'],
        amount=amount,
        category=data.get('category'),
        expense_date=data.get('expense_date', datetime.utcnow()),
        status=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(expense)
    db.session.flush()  # get expense.id before commit

    # Generate transaction number
    txn_id, txn_no_str = generate_transaction_number('EXP')
    expense.transaction_no = txn_id

    # Post GL entries: Debit Expense, Credit Cash/Bank
    entries = [
        {"account_id": 600, "transaction_type": "Debit", "amount": amount},  # Expense account
        {"account_id": 1, "transaction_type": "Credit", "amount": amount}    # Cash/Bank
    ]
    post_to_ledger(entries, transaction_no_id=txn_id, description=f"Expense #{expense.id}: {expense.description}")

    db.session.commit()
    return jsonify({
        "message": "Expense added with GL entries",
        "expense_id": expense.id,
        "transaction_no": txn_no_str
    }), 201


# --- Get all expenses ---
@expenses_bp.route('/', methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    data = [{
        "id": e.id,
        "description": e.description,
        "amount": e.amount,
        "category": e.category,
        "expense_date": e.expense_date,
        "status": e.status,
        "created_at": e.created_at,
        "updated_at": e.updated_at,
        "transaction_no": e.transaction_no
    } for e in expenses]
    return jsonify(data)


# --- Get expense by ID ---
@expenses_bp.route('/<int:id>', methods=['GET'])
def get_expense(id):
    e = Expense.query.get_or_404(id)
    return jsonify({
        "id": e.id,
        "description": e.description,
        "amount": e.amount,
        "category": e.category,
        "expense_date": e.expense_date,
        "status": e.status,
        "created_at": e.created_at,
        "updated_at": e.updated_at,
        "transaction_no": e.transaction_no
    })


# --- Update expense with GL reversal ---
@expenses_bp.route('/<int:id>', methods=['PUT'])
def update_expense(id):
    expense = Expense.query.get_or_404(id)
    data = request.json
    new_amount = data.get('amount', expense.amount)
    new_description = data.get('description', expense.description)
    new_category = data.get('category', expense.category)
    new_date = data.get('expense_date', expense.expense_date)

    # Reverse previous GL entries
    if expense.transaction_no:
        original_entries = GeneralLedger.query.filter_by(transaction_no=expense.transaction_no).all()
        for entry in original_entries:
            reverse_type = 'Credit' if entry.transaction_type == 'Debit' else 'Debit'
            reverse_entry = GeneralLedger(
                account_id=entry.account_id,
                transaction_type=reverse_type,
                amount=entry.amount,
                description=f"Reversal of {entry.description} before update",
                transaction_date=datetime.utcnow(),
                transaction_no=entry.transaction_no
            )
            db.session.add(reverse_entry)

    # Update expense fields
    expense.amount = new_amount
    expense.description = new_description
    expense.category = new_category
    expense.expense_date = new_date
    expense.updated_at = datetime.utcnow()
    expense.status = 1
    db.session.add(expense)
    db.session.flush()

    # Post new GL entries
    txn_id, txn_no_str = generate_transaction_number('EXP')
    expense.transaction_no = txn_id
    entries = [
        {"account_id": 600, "transaction_type": "Debit", "amount": new_amount},
        {"account_id": 1, "transaction_type": "Credit", "amount": new_amount}
    ]
    post_to_ledger(entries, transaction_no_id=txn_id, description=f"Updated Expense #{expense.id}: {expense.description}")

    db.session.commit()
    return jsonify({"message": "Expense updated with GL entries", "expense_id": expense.id})


# --- Delete expense with GL reversal ---
@expenses_bp.route('/<int:id>', methods=['DELETE'])
def delete_expense(id):
    expense = Expense.query.get_or_404(id)

    # Reverse GL entries
    if expense.transaction_no:
        original_entries = GeneralLedger.query.filter_by(transaction_no=expense.transaction_no).all()
        for entry in original_entries:
            reverse_type = 'Credit' if entry.transaction_type == 'Debit' else 'Debit'
            reverse_entry = GeneralLedger(
                account_id=entry.account_id,
                transaction_type=reverse_type,
                amount=entry.amount,
                description=f"Reversal of {entry.description} on deletion",
                transaction_date=datetime.utcnow(),
                transaction_no=entry.transaction_no
            )
            db.session.add(reverse_entry)

    # Mark as inactive instead of hard delete
    expense.status = 0
    expense.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Expense marked inactive and GL reversed", "expense_id": id})
