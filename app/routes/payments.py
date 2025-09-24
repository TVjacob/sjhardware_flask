from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import Account, Payment, Sale, GeneralLedger
from app.utils.gl_utils import post_to_ledger, generate_transaction_number

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')


# ------------------ Helper Function ------------------
# def recalc_sale_payment_status(sale_id):
#     """Recalculate and update a sale's payment status."""
#     sale = Sale.query.get(sale_id)
#     total_paid = db.session.query(db.func.sum(Payment.amount)).filter_by(sale_id=sale_id, status=1).scalar() or 0

#     if total_paid >= sale.total_amount:
#         sale.payment_status = "Paid"
#     elif total_paid > 0:
#         sale.payment_status = "Partial"
#     else:
#         sale.payment_status = "Pending"

#     sale.updated_at = datetime.utcnow()
#     return total_paid, sale.payment_status
# ------------------ Helper Function ------------------
def recalc_sale_payment_status(sale_id):
    """Recalculate and update a sale's payment status."""
    sale = Sale.query.get(sale_id)
    total_paid = db.session.query(db.func.sum(Payment.amount)).filter_by(sale_id=sale_id, status=1).scalar() or 0

    if total_paid >= sale.total_amount:
        status = "Paid"
    elif total_paid > 0:
        status = "Partial"
    else:
        status = "Pending"

    return total_paid, status


# # ------------------ Record a Payment ------------------
# @payments_bp.route('/', methods=['POST'])
# def add_payment():
#     data = request.json
#     sale = Sale.query.get(data['sale_id'])
#     if not sale:
#         return jsonify({"error": "Sale not found"}), 404

#     amount = data['amount']
#     payment_type = data.get('payment_type', 'Cash')
#     reference = data.get('reference')
#     payment_account_id = data.get('payment_account_id')
#     transaction_date_str = data.get('transaction_date')  # <-- New field from frontend

#     # Validate transaction date or fallback to UTC now
#     try:
#         if transaction_date_str:
#             # Parse provided date
#             transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d')
#         else:
#             transaction_date = datetime.utcnow()
#     except ValueError:
#         return jsonify({'error': 'Invalid transaction date format. Use YYYY-MM-DD'}), 400
    
#         # Validate payment account exists
#     payment_account = Account.query.get(payment_account_id)
#     if not payment_account:
#         return jsonify({'error': 'Invalid payment account selected'}), 400

#     # Create Payment
#     payment = Payment(
#         sale_id=sale.id,
#         amount=amount,
#         payment_type=payment_type,
#         reference=reference,
#         payment_date=transaction_date,
#         payment_account_id=payment_account_id
#     )
#     db.session.add(payment)
#     db.session.flush()  # Get payment.id before commit

#     # Generate Transaction Number
#     txn_id, txn_no_str = generate_transaction_number('PAY',transaction_date=transaction_date)
    

#     # Post to General Ledger (Debit Cash, Credit Accounts Receivable)
#     entries = [
#         {"account_id": payment_account.code, "transaction_type": "Debit", "amount": amount},   # Cash/Bank
#         {"account_id": 1100, "transaction_type": "Credit", "amount": amount} # Accounts Receivable
#     ]
#     gl_entries = post_to_ledger(entries, transaction_no_id=txn_id, description=f"Payment for Sale #{sale.id}",transaction_date=transaction_date)

#     # Link Payment to Transaction Number
#     payment.transaction_no = txn_id
#     payment.updated_at = datetime.utcnow()

#     # Update Sale payment status
#     recalc_sale_payment_status(sale.id)

#     db.session.commit()

#     return jsonify({
#         "message": "Payment recorded with GL entries",
#         "payment_id": payment.id,
#         "transaction_no": txn_no_str,
#         "sale_status": sale.payment_status
#     }), 201


# # ------------------ Get All Payments ------------------
# @payments_bp.route('/', methods=['GET'])
# def get_payments():
#     payments = Payment.query.filter_by(status=1).all()
#     data = [{
#         "payment_id": p.id,
#         "sale_id": p.sale_id,
#         "amount": p.amount,
#         "payment_type": p.payment_type,
#         "reference": p.reference,
#         "payment_date": p.payment_date,
#         "transaction_no": p.transaction_no,
#         "status": p.status,
#         "created_at": p.created_at,
#         "updated_at": p.updated_at
#     } for p in payments]
#     return jsonify(data), 200

# ------------------ Record a Payment ------------------
@payments_bp.route('/', methods=['POST'])
def add_payment():
    data = request.json
    sale = Sale.query.get(data['sale_id'])
    if not sale:
        return jsonify({"error": "Sale not found"}), 404

    amount = data['amount']
    payment_type = data.get('payment_type', 'Cash')
    reference = data.get('reference')
    payment_account_id = data.get('payment_account_id')
    transaction_date_str = data.get('transaction_date')  # <-- New field from frontend

    # Validate transaction date or fallback to UTC now
    try:
        if transaction_date_str:
            transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d')
        else:
            transaction_date = datetime.utcnow()
    except ValueError:
        return jsonify({'error': 'Invalid transaction date format. Use YYYY-MM-DD'}), 400
    
    # Validate payment account
    payment_account = Account.query.get(payment_account_id)
    if not payment_account:
        return jsonify({'error': 'Invalid payment account selected'}), 400

    # ----------------- Create Payment -----------------
    payment = Payment(
        sale_id=sale.id,
        amount=amount,
        payment_type=payment_type,
        reference=reference,
        payment_date=transaction_date,
        payment_account_id=payment_account_id
    )
    db.session.add(payment)
    db.session.flush()  # So we can access payment.id before commit

    # ----------------- Generate Transaction Number -----------------
    txn_id, txn_no_str = generate_transaction_number('PAY', transaction_date=transaction_date)

    # ----------------- Post to General Ledger -----------------
    entries = [
        {"account_id": payment_account.code, "transaction_type": "Debit", "amount": amount},  # Cash/Bank
        {"account_id": 1100, "transaction_type": "Credit", "amount": amount}  # Accounts Receivable
    ]
    gl_entries = post_to_ledger(
        entries,
        transaction_no_id=txn_id,
        description=f"Payment for Sale #{sale.id}",
        transaction_date=transaction_date
    )

    # Link payment to transaction
    payment.transaction_no = txn_id
    payment.updated_at = datetime.utcnow()

    # ----------------- Update Sale Totals -----------------
    total_paid, payment_status = recalc_sale_payment_status(sale.id)
    
    sale.total_paid = total_paid
    sale.balance = max(sale.total_amount - total_paid, 0)  # Ensure it doesn't go negative
    sale.payment_status = payment_status
    sale.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "message": "Payment recorded with GL entries",
        "payment_id": payment.id,
        "transaction_no": txn_no_str,
        "sale_status": sale.payment_status,
        "total_paid": sale.total_paid,
        "balance": sale.balance
    }), 201

# ------------------ Get Payment by ID ------------------
@payments_bp.route('/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    p = Payment.query.get_or_404(payment_id)
    return jsonify({
        "payment_id": p.id,
        "sale_id": p.sale_id,
        "amount": p.amount,
        "payment_type": p.payment_type,
        "reference": p.reference,
        "payment_date": p.payment_date,
        "transaction_no": p.transaction_no,
        "status": p.status,
        "created_at": p.created_at,
        "updated_at": p.updated_at
    })


# ------------------ Update a Payment ------------------
@payments_bp.route('/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    sale = Sale.query.get(payment.sale_id)
    data = request.json

    new_amount = data.get('amount', payment.amount)
    new_payment_type = data.get('payment_type', payment.payment_type)
    new_reference = data.get('reference', payment.reference)

    # Reverse previous GL entries
    if payment.transaction_no:
        original_entries = GeneralLedger.query.filter_by(transaction_no=payment.transaction_no, status=1).all()
        for entry in original_entries:
            reverse_type = 'Credit' if entry.transaction_type == 'Debit' else 'Debit'
            reverse_entry = GeneralLedger(
                account_id=entry.account_id,
                transaction_type=reverse_type,
                amount=entry.amount,
                description=f"Reversal of {entry.description} before update",
                transaction_date=datetime.utcnow(),
                transaction_no=payment.transaction_no,
                status=1
            )
            db.session.add(reverse_entry)

    # Update payment fields
    payment.amount = new_amount
    payment.payment_type = new_payment_type
    payment.reference = new_reference
    payment.updated_at = datetime.utcnow()
    db.session.add(payment)
    db.session.flush()

    # Post new GL entries
    txn_id, txn_no_str = generate_transaction_number('PAY')
    entries = [
        {"account_id": 1, "transaction_type": "Debit", "amount": new_amount},
        {"account_id": 101, "transaction_type": "Credit", "amount": new_amount}
    ]
    gl_entries = post_to_ledger(entries, transaction_no_id=txn_id, description=f"Updated payment for Sale #{sale.id}")
    payment.transaction_no = txn_id

    # Update sale payment status
    recalc_sale_payment_status(sale.id)

    db.session.commit()
    return jsonify({
        "message": "Payment updated with GL entries",
        "payment_id": payment.id,
        "transaction_no": txn_no_str,
        "sale_status": sale.payment_status
    })


# ------------------ Delete Payment (Soft Delete + GL Reversal) ------------------
@payments_bp.route('/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    sale = Sale.query.get(payment.sale_id)

    # Reverse GL entries
    if payment.transaction_no:
        original_entries = GeneralLedger.query.filter_by(transaction_no=payment.transaction_no, status=1).all()
        for entry in original_entries:
            reverse_type = 'Credit' if entry.transaction_type == 'Debit' else 'Debit'
            reverse_entry = GeneralLedger(
                account_id=entry.account_id,
                transaction_type=reverse_type,
                amount=entry.amount,
                description=f"Reversal of {entry.description} on deletion",
                transaction_date=datetime.utcnow(),
                transaction_no=payment.transaction_no,
                status=1
            )
            db.session.add(reverse_entry)

    # Soft delete payment
    payment.status = 0
    payment.updated_at = datetime.utcnow()

    # Update sale payment status
    recalc_sale_payment_status(sale.id)

    db.session.commit()

    return jsonify({
        "message": "Payment soft-deleted and GL reversed",
        "payment_id": payment_id,
        "sale_status": sale.payment_status
    })
