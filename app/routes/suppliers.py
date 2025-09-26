from flask import Blueprint, request, jsonify
from app import db
from app.models import Account, Product, Supplier, PurchaseOrder, PurchaseOrderItem, SupplierPayment
from app.utils.auth import token_required
from app.utils.gl_utils import post_to_ledger, generate_transaction_number
from datetime import datetime

from sqlalchemy.orm import joinedload
# from flask import jsonify

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

# ------------------ Supplier CRUD ------------------ #

@token_required
# Get all suppliers
@suppliers_bp.route('/', methods=['GET'])
def get_suppliers():
    print("Request headers:", request.headers)

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


@token_required
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


@token_required
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


@token_required
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


@token_required
# Delete supplier
@suppliers_bp.route('/<int:id>', methods=['DELETE'])

def delete_supplier(id):
    s = Supplier.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': 'Supplier deleted successfully', 'id': id})

# ------------------ Purchase Orders ------------------ #

@token_required
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


@token_required
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


@token_required
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


@token_required
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


@token_required
# Delete purchase order
@suppliers_bp.route('/orders/<int:id>', methods=['DELETE'])

def delete_purchase_order(id):
    po = PurchaseOrder.query.get_or_404(id)
    db.session.delete(po)
    db.session.commit()
    return jsonify({'message': 'Purchase Order deleted successfully', 'id': id})


@token_required

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
    po.status = 3 if po.total_balance == 0 else 5 if po.total_paid == po.total_balance else 4

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

@token_required

@suppliers_bp.route('/purchase-order/<int:purchase_order_id>', methods=['GET'])

def purchase_order_details(purchase_order_id):
    return get_purchase_order_details(purchase_order_id)


def get_purchase_order_details(purchase_order_id):
    """
    Retrieve complete purchase order details including supplier info,
    items, payments, and financial totals.
    """
    # Fetch the Purchase Order with related Supplier, Items, and Payments
    purchase_order = (
        PurchaseOrder.query
        .options(
            joinedload(PurchaseOrder.supplier),
            joinedload(PurchaseOrder.items),
            joinedload(PurchaseOrder.supplier).joinedload(Supplier.purchase_orders)
        )
        .filter(PurchaseOrder.id == purchase_order_id, PurchaseOrder.status != 9)
        .first()
    )

    if not purchase_order:
        return {"error": "Purchase order not found or inactive"}, 404

    # Fetch all payments linked to this purchase order
    payments = SupplierPayment.query.filter_by(
        purchase_order_id=purchase_order_id,
        status=1
    ).all()

    # Calculate totals
    total_amount = sum(item.total_price for item in purchase_order.items if item.status != 9)
    total_paid = sum(payment.amount for payment in payments)
    balance = total_amount - total_paid

    # Prepare item details
    item_details = [
        {
            "product_id": item.product_id,
            "product_name": item.product.name if item.product else None,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.total_price
        }
        for item in purchase_order.items if item.status != 9
    ]

    # Prepare payment details
    payment_details = [

        {
            "payment_id": p.id,
            "amount": p.amount,
            "payment_type": p.payment_type,
            "payment_date": p.payment_date.strftime("%Y-%m-%d"),
            "reference": p.reference,
            "account_id":  Account.query.get(p.payment_account_id).name if p.payment_account_id else None,
        }
        for p in payments
    ]

    # Final response
    response = {
        "purchase_order_id": purchase_order.id,
        "invoice_number": purchase_order.invoice_number,
        "purchase_date": purchase_order.purchase_date.strftime("%Y-%m-%d"),
        "supplier": {
            "supplier_id": purchase_order.supplier.id,
            "name": purchase_order.supplier.name,
            "contact": purchase_order.supplier.contact,
            "email": purchase_order.supplier.email
        },
        "items": item_details,
        "payments": payment_details,
        "summary": {
            "total_amount": total_amount,
            "total_paid": total_paid,
            "balance": balance,
            "grand_total": total_amount  # Can add tax or other charges here later
        }
    }

    return jsonify(response)
