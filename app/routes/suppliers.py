from flask import Blueprint, request, jsonify
from app import db
from app.models import Account, Product, Supplier, PurchaseOrder, PurchaseOrderItem, SupplierPayment
from app.utils.gl_utils import post_to_ledger, generate_transaction_number
from datetime import datetime

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

# ------------------ Supplier CRUD ------------------ #

# Get all suppliers
@suppliers_bp.route('/', methods=['GET'])
def get_suppliers():
    suppliers = Supplier.query.filter_by(status=1).all()
    data = [{
        'id': s.id,
        'name': s.name,
        'contact': s.contact,
        'email': s.email,
        'status': s.status,
        'created_at': s.created_at
    } for s in suppliers]
    return jsonify(data), 200


# Get single supplier
@suppliers_bp.route('/<int:id>', methods=['GET'])
def get_supplier(id):
    s = Supplier.query.get_or_404(id)
    return jsonify({
        'id': s.id,
        'name': s.name,
        'contact': s.contact,
        'email': s.email,
        'status': s.status,
        'created_at': s.created_at
    })


# Add a new supplier
@suppliers_bp.route('/', methods=['POST'])
def add_supplier():
    data = request.get_json()
    supplier = Supplier(
        name=data['name'],
        contact=data.get('contact'),
        email=data.get('email'),
        status=1
    )
    db.session.add(supplier)
    db.session.commit()
    return jsonify({'message': 'Supplier created successfully', 'id': supplier.id}), 201


# Update supplier
@suppliers_bp.route('/<int:id>', methods=['PUT'])
def update_supplier(id):
    s = Supplier.query.get_or_404(id)
    data = request.get_json()
    s.name = data.get('name', s.name)
    s.contact = data.get('contact', s.contact)
    s.email = data.get('email', s.email)
    s.status = data.get('status', s.status)
    db.session.commit()
    return jsonify({'message': 'Supplier updated successfully', 'id': s.id})


# Delete supplier
@suppliers_bp.route('/<int:id>', methods=['DELETE'])
def delete_supplier(id):
    s = Supplier.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': 'Supplier deleted successfully', 'id': id})

# ------------------ Purchase Orders ------------------ #

# Get all purchase orders
@suppliers_bp.route('/orders', methods=['GET'])
def get_purchase_orders():
    orders = PurchaseOrder.query.filter(PurchaseOrder.status.in_([1, 2, 3])).all()
    data = [{
        'id': o.id,
        'supplier_id': o.supplier_id,
        'supplier_name': o.supplier.name if o.supplier else None,
        'invoice_number': o.invoice_number,
        'total_amount': o.total_amount,
        'total_paid': o.total_paid,
        'total_balance': o.total_balance,
        'status': o.status,
        'created_at': o.created_at
    } for o in orders]
    return jsonify(data), 200


# Get purchase order by ID
@suppliers_bp.route('/orders/<int:id>', methods=['GET'])
def get_purchase_order(id):
    po = PurchaseOrder.query.get_or_404(id)
    return jsonify({
        'id': po.id,
        'supplier_id': po.supplier_id,
        'supplier_name': po.supplier.name if po.supplier else None,
        'invoice_number': po.invoice_number,
        'memo': po.memo,
        'purchase_date': po.purchase_date,
        'total_amount': po.total_amount,
        'total_paid': po.total_paid,
        'total_balance': po.total_balance,
        'status': po.status,
        'items': [{
            'id': item.id,
            'product_id': item.product_id,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'total_price': item.total_price,
            'status': item.status
        } for item in po.items]
    })


# Add new purchase order with multiple items
# @suppliers_bp.route('/orders', methods=['POST'])
# def add_purchase_order():
#     data = request.get_json()

#     if not data.get('items') or len(data['items']) == 0:
#         return jsonify({'error': 'At least one item is required'}), 400

#     # Create new Purchase Order
#     po = PurchaseOrder(
#         supplier_id=data['supplier_id'],
#         invoice_number=data['invoice_number'],
#         purchase_date=data.get('purchase_date', datetime.utcnow()),
#         memo=data.get('memo'),
#         status=1
#     )
#     db.session.add(po)
#     db.session.flush()  # to get PO id before committing

#     total_amount = 0

#     # Add purchase order items
#     for item_data in data['items']:
#         item = PurchaseOrderItem(
#             purchase_order_id=po.id,
#             product_id=item_data['product_id'],
#             quantity=item_data['quantity'],
#             unit_price=item_data['cost_price'],
#             status=1
#         )
#         item.calculate_total()
#         db.session.add(item)
#         total_amount += item.total_price

#     # Update totals
#     po.total_amount = total_amount
#     po.total_balance = total_amount
#     db.session.commit()

#     return jsonify({'message': 'Purchase Order created successfully', 'po_id': po.id}), 200


# Add new purchase order with multiple items
@suppliers_bp.route('/orders', methods=['POST'])
def add_purchase_order():
    data = request.get_json()

    if not data.get('items') or len(data['items']) == 0:
        return jsonify({'error': 'At least one item is required'}), 400

    # Create new Purchase Order
    po = PurchaseOrder(
        supplier_id=data['supplier_id'],
        invoice_number=data['invoice_number'],
        purchase_date=data.get('purchase_date', datetime.utcnow()),
        memo=data.get('memo'),
        status=1
    )
    db.session.add(po)
    db.session.flush()  # to get PO id before committing

    total_amount = 0

    # Add purchase order items
    for item_data in data['items']:
        item = PurchaseOrderItem(
            purchase_order_id=po.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            unit_price=item_data['cost_price'],
            status=1
        )
        item.calculate_total()
        db.session.add(item)
        total_amount += item.total_price

        # Update product stock
        product = Product.query.get(item.product_id)
        if product:
            product.quantity = (product.quantity or 0) + item.quantity
            db.session.add(product)

    # Update totals
    po.total_amount = total_amount
    po.total_balance = total_amount
    db.session.commit()

    return jsonify({'message': 'Purchase Order created successfully', 'po_id': po.id}), 200


# Update purchase order details
@suppliers_bp.route('/orders/<int:id>', methods=['PUT'])
def update_purchase_order(id):
    po = PurchaseOrder.query.get_or_404(id)
    data = request.get_json()

    po.supplier_id = data.get('supplier_id', po.supplier_id)
    po.invoice_number = data.get('invoice_number', po.invoice_number)
    po.memo = data.get('memo', po.memo)
    po.purchase_date = data.get('purchase_date', po.purchase_date)

    # Update items if provided
    if 'items' in data:
        for item_data in data['items']:
            if 'id' in item_data:
                # Update existing item
                item = PurchaseOrderItem.query.get(item_data['id'])
                if item and item.purchase_order_id == po.id:
                    item.quantity = item_data.get('quantity', item.quantity)
                    item.unit_price = item_data.get('unit_price', item.unit_price)
                    item.calculate_total()
            else:
                # Add new item
                new_item = PurchaseOrderItem(
                    purchase_order_id=po.id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    status=1
                )
                new_item.calculate_total()
                db.session.add(new_item)

    # Recalculate totals
    po.update_totals()
    db.session.commit()

    return jsonify({'message': 'Purchase Order updated successfully', 'id': po.id})


# Delete purchase order
@suppliers_bp.route('/orders/<int:id>', methods=['DELETE'])
def delete_purchase_order(id):
    po = PurchaseOrder.query.get_or_404(id)
    db.session.delete(po)
    db.session.commit()
    return jsonify({'message': 'Purchase Order deleted successfully', 'id': id})


# ------------------ Supplier Payments ------------------ #
# @suppliers_bp.route('/orders/<int:id>/pay', methods=['POST'])
# def pay_purchase_order(id):
#     po = PurchaseOrder.query.get_or_404(id)
#     data = request.get_json()
#     amount = data['amount']
#     payment_type = data.get('payment_type', 'Cash')
#     reference = data.get('reference')

#     if amount <= 0:
#         return jsonify({'error': 'Invalid payment amount'}), 400

#     if amount > po.total_balance:
#         return jsonify({'error': 'Payment exceeds remaining balance'}), 400

#     # Create supplier payment
#     payment = SupplierPayment(
#         purchase_order_id=po.id,
#         amount=amount,
#         payment_type=payment_type,
#         reference=reference,
#         status=1
#     )
#     db.session.add(payment)

#     # Update PurchaseOrder totals
#     po.total_paid += amount
#     po.total_balance = po.total_amount - po.total_paid
#     if po.total_balance == 0:
#         po.status = 2  # Fully Paid
#     else:
#         po.status = 3  # Partially Paid

#     db.session.commit()

#     return jsonify({
#         "message": f"Payment of {amount} recorded for PO #{po.id}",
#         "payment_id": payment.id,
#         "new_balance": po.total_balance,
#         "po_status": po.status
#     }), 201


# ------------------ Supplier Payments ------------------ #
# @suppliers_bp.route('/orders/<int:id>/pay', methods=['POST'])
# def pay_purchase_order(id):
#     po = PurchaseOrder.query.get_or_404(id)
#     data = request.get_json()

#     amount = data['amount']
#     payment_type = data.get('payment_type', 'Cash')  # Cash, Bank, Mobile Money
#     reference = data.get('reference')
#     payment_account_id = data.get('payment_account_id')  # <-- Payment account
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

#     if not payment_account_id:
#         return jsonify({'error': 'Payment account is required'}), 400

#     # Validate payment account exists
#     payment_account = Account.query.get(payment_account_id)
#     if not payment_account:
#         return jsonify({'error': 'Invalid payment account selected'}), 400

#     if amount <= 0:
#         return jsonify({'error': 'Invalid payment amount'}), 400

#     if amount > po.total_balance:
#         return jsonify({'error': 'Payment exceeds remaining balance'}), 400

#     # Create supplier payment record
#     payment = SupplierPayment(
#         purchase_order_id=po.id,
#         payment_account_id=payment_account_id,
#         amount=amount,
#         payment_type=payment_type,
#         reference=reference,
#         payment_date=transaction_date,  # <-- Save date to DB
#         status=1
#     )
#     db.session.add(payment)
#     db.session.flush()

#     # Update PurchaseOrder totals
#     po.total_paid += amount
#     po.total_balance = po.total_amount - po.total_paid

#     if po.total_balance == 0:
#         po.status = 2  # Fully Paid
#     else:
#         po.status = 3  # Partially Paid

#     # ---------- Generate GL Double Entry ----------
#     txn_id, txn_str = generate_transaction_number('SUPP-PAY',transaction_date  =transaction_date)

#     # Debit Accounts Payable (reduce liability)
#     # Credit Cash/Bank/Mobile Money account
#     entries = [
#         {
#             "account_id": 2100,  # Example: Accounts Payable
#             "transaction_type": "Debit",
#             "amount": amount
#         },
#         {
#             "account_id": payment_account.code,  # Dynamic based on selected payment account
#             "transaction_type": "Credit",
#             "amount": amount
#         }
#     ]

#     gl_entries = post_to_ledger(
#         entries,
#         transaction_no_id=txn_id,
#         description=f"Payment for PO #{po.id}",
#         transaction_date=transaction_date  # <-- Use provided transaction date
#     )

#     # Link the transaction number to supplier payment
#     payment.transaction_no = gl_entries[0].id

#     db.session.commit()

#     return jsonify({
#         "message": f"Payment of {amount} recorded for PO #{po.id}",
#         "payment_id": payment.id,
#         "new_balance": po.total_balance,
#         "po_status": po.status,
#         "gl_transaction_id": txn_id
#     }), 201


@suppliers_bp.route('/orders/<int:id>/pay', methods=['POST'])
def pay_purchase_order(id):
    po = PurchaseOrder.query.get_or_404(id)
    data = request.get_json()

    amount = data['amount']
    payment_type = data.get('payment_type', 'Cash')
    reference = data.get('reference')
    payment_account_id = data.get('payment_account_id')
    transaction_date_str = data.get('transaction_date')  # <-- New field from frontend

    # Validate transaction date or fallback to UTC now
    try:
        if transaction_date_str:
            # Parse provided date
            transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d')
        else:
            transaction_date = datetime.utcnow()
    except ValueError:
        return jsonify({'error': 'Invalid transaction date format. Use YYYY-MM-DD'}), 400

    if not payment_account_id:
        return jsonify({'error': 'Payment account is required'}), 400

    # Validate payment account exists
    payment_account = Account.query.get(payment_account_id)
    if not payment_account:
        return jsonify({'error': 'Invalid payment account selected'}), 400

    if amount <= 0:
        return jsonify({'error': 'Invalid payment amount'}), 400

    if amount > po.total_balance:
        return jsonify({'error': 'Payment exceeds remaining balance'}), 400

    # ---------- Generate Transaction Number First ----------
    txn_id, txn_str = generate_transaction_number('SUPP-PAY',transaction_date=transaction_date)

    # Create supplier payment record AFTER txn number exists
    payment = SupplierPayment(
        purchase_order_id=po.id,
        payment_account_id=payment_account_id,
        amount=amount,
        payment_type=payment_type,
        reference=reference,
        transaction_no=txn_id,  # ✅ Now guaranteed to exist
        payment_date=transaction_date,
        status=1
    )
    db.session.add(payment)
    db.session.flush()

    # Update PurchaseOrder totals
    po.total_paid += amount
    po.total_balance = po.total_amount - po.total_paid
    po.status = 2 if po.total_balance == 0 else 3

    # ---------- Generate GL Double Entry ----------
    entries = [
        {
            "account_id": 2100,  # Accounts Payable
            "transaction_type": "Debit",
            "amount": amount
        },
        {
            "account_id": payment_account.code,  # Dynamic account
            "transaction_type": "Credit",
            "amount": amount
        }
    ]

    post_to_ledger(
        entries,
        transaction_no_id=txn_id,
        description=f"Payment for PO #{po.id}",
        transaction_date=transaction_date
    )

    # Final commit
    db.session.commit()

    return jsonify({
        "message": f"Payment of {amount} recorded for PO #{po.id}",
        "payment_id": payment.id,
        "new_balance": po.total_balance,
        "po_status": po.status,
        "gl_transaction_id": txn_id
    }), 201
