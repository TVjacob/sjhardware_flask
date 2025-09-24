from flask import Blueprint, request, jsonify
from app import db
from app.models import Account, Expense, ExpenseItem, GeneralLedger
from app.utils.gl_utils import post_to_ledger, generate_transaction_number
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')


# --------------------------------------------------------
# Create a new expense with full double-entry GL posting
# --------------------------------------------------------
@expenses_bp.route('/', methods=['POST'])
def create_expense():
    try:
        data = request.json

        # Extract header data
        description = data.get('description')
        payment_account_id = data.get('payment_account_id')
        expense_date = data.get('expense_date', datetime.utcnow().strftime('%Y-%m-%d'))
        reference = data.get('reference')
        items_data = data.get('items', [])

        if not description or not payment_account_id or not items_data:
            return jsonify({"error": "Missing required fields: description, payment_account_id, and items"}), 400

        # Convert expense_date to datetime
        expense_date_obj = datetime.strptime(expense_date, '%Y-%m-%d')

        # Create expense header
        expense = Expense(
            description=description,
            expense_date=expense_date_obj,
            payment_account_id=payment_account_id,
            reference=reference,
            status=1
        )
        db.session.add(expense)
        db.session.flush()  # Get expense.id

        # Create transaction number for GL
        txn_id, txn_no_str = generate_transaction_number('EXP',transaction_date=expense_date_obj)
        expense.transaction_no = txn_id

        # --- Insert expense items ---
        total_amount = 0
        for item in items_data:
            account_id = item.get('account_id')
            item_name = item.get('item_name')
            amount = float(item.get('amount', 0))

            if not account_id or not item_name or amount <= 0:
                return jsonify({"error": "Each item must have account_id, item_name, and amount > 0"}), 400

            total_amount += amount

            # Save the expense item
            expense_item = ExpenseItem(
                expense_id=expense.id,
                account_id=account_id,
                item_name=item_name,
                description=item.get('description'),
                amount=amount
            )
            db.session.add(expense_item)

        # Update total
        expense.total_amount = total_amount

        # --- Post to General Ledger ---
        # Debit each expense account for its amount
        gl_entries = []
        for item in expense.items:
            account=db.session.query(Account).filter_by(id=item.account_id).first()  # Ensure account exists
            gl_entries.append({
                "account_id": account.code,
                "transaction_type": "Debit",
                "amount": item.amount
            })
        account=db.session.query(Account).filter_by(id=payment_account_id).first()  # Ensure account exists

        # Credit payment account with total
        gl_entries.append({
            "account_id": account.code,
            "transaction_type": "Credit",
            "amount": total_amount
        })

        # Post entries to the ledger
        post_to_ledger(
            gl_entries,
            transaction_no_id=txn_id,
            description=f"Expense #{expense.id}: {description}",
            transaction_date=expense_date_obj
        )

        # Commit everything
        db.session.commit()

        return jsonify({
            "message": "Expense created and posted to GL successfully",
            "expense_id": expense.id,
            "transaction_no": txn_no_str,
            "total_amount": total_amount
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- Get all expenses ---
@expenses_bp.route('/', methods=['GET'])
def get_expenses():
    expenses = Expense.query.filter_by( status=1).all()
    data = [{
        "id": e.id,
        "description": e.description,
        "total_amount": e.total_amount,  # FIXED: replaced 'amount' with 'total_amount'
        "payment_account_id": e.payment_account_id,
        "expense_date": e.expense_date.strftime('%Y-%m-%d') if e.expense_date else None,
        "reference": e.reference,
        "status": e.status,
        "transaction_no": e.transaction_no,
        "items": [
            {
                "id": item.id,
                "account_id": item.account_id,
                "item_name": item.item_name,
                "description": item.description,
                "amount": item.amount
            }
            for item in e.items
        ]
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


# # --- Delete expense with GL reversal ---
# @expenses_bp.route('/<int:id>', methods=['DELETE'])
# def delete_expense(id):
#     expense = Expense.query.get_or_404(id)

#     # Reverse GL entries
#     if expense.transaction_no:
#         original_entries = GeneralLedger.query.filter_by(transaction_no=expense.transaction_no).all()
#         for entry in original_entries:
#             reverse_type = 'Credit' if entry.transaction_type == 'Debit' else 'Debit'
#             reverse_entry = GeneralLedger(
#                 account_id=entry.account_id,
#                 transaction_type=reverse_type,
#                 amount=entry.amount,
#                 description=f"Reversal of {entry.description} on deletion",
#                 transaction_date=datetime.utcnow(),
#                 transaction_no=entry.transaction_no
#             )
#             db.session.add(reverse_entry)

#     # Mark as inactive instead of hard delete
#     expense.status = 0
#     expense.updated_at = datetime.utcnow()
#     db.session.commit()
#     return jsonify({"message": "Expense marked inactive and GL reversed", "expense_id": id})



# --- Delete expense with GL reversal ---
@expenses_bp.route('/<int:id>', methods=['DELETE'])
def delete_expense(id):
    expense = Expense.query.get_or_404(id)

    # Reverse GL entries for the main transaction
    if expense.transaction_no:
        original_entries = GeneralLedger.query.filter_by(transaction_no=expense.transaction_no).all()
        for entry in original_entries:
            reverse_type = 'Credit' if entry.transaction_type == 'Debit' else 'Debit'
            reverse_entry = GeneralLedger(
                account_id=entry.account_id,
                transaction_type=reverse_type,
                amount=entry.amount,
                description=f"Reversal of {entry.description} on expense deletion",
                transaction_date=datetime.utcnow(),
                transaction_no=entry.transaction_no
            )
            db.session.add(reverse_entry)

        # Reverse each expense item individually as double entry
        for item in expense.items:
            if item.account_id and item.amount:
                # Reverse entry for the item account
                reverse_item_entry = GeneralLedger(
                    account_id=item.account_id,
                    transaction_type='Credit',  # Assuming original was Debit
                    amount=item.amount,
                    description=f"Reversal of expense item {item.item_name}",
                    transaction_date=datetime.utcnow(),
                    transaction_no=expense.transaction_no
                )
                db.session.add(reverse_item_entry)

                # Counter-entry for payment account
                reverse_payment_entry = GeneralLedger(
                    account_id=expense.payment_account_id,
                    transaction_type='Debit',  # Assuming original was Credit
                    amount=item.amount,
                    description=f"Reversal of payment for expense item {item.item_name}",
                    transaction_date=datetime.utcnow(),
                    transaction_no=expense.transaction_no
                )
                db.session.add(reverse_payment_entry)

    # Soft delete by setting status = 9
    expense.status = 9
    expense.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Expense marked deleted (status=9) and GL entries reversed", "expense_id": id})
