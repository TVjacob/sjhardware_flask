from flask import Blueprint, request, jsonify
from app import db
from app.models import Product, Sale, SaleItem, GeneralLedger
from app.utils.gl_utils import post_to_ledger, generate_transaction_number
from datetime import datetime

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

# ------------------ Helper function for updating timestamps ------------------ #
def update_timestamps(obj):
    obj.updated_at = datetime.utcnow()
    if not obj.created_at:
        obj.created_at = datetime.utcnow()

# # ------------------ Create a Sale & Invoice with GL ------------------ #
# @sales_bp.route('/', methods=['POST'])
# def create_sale():
#     data = request.json
#     items = data['items']  # [{"product_id":1,"quantity":2}, ...]
#     total_amount = 0
#     cogs_total = 0  # Cost of goods sold total

#     # Create new Sale with StatusMixin defaults
#     sale = Sale(
#         sale_number=data['sale_number'],
#         total_amount=0,
#         payment_status='Pending',
#         status=1
#     )
#     update_timestamps(sale)
#     db.session.add(sale)
#     db.session.flush()  # Get sale.id before committing

#     for item in items:
#         product = Product.query.get(item['product_id'])
#         if not product:
#             return jsonify({"error": f"Product {item['product_id']} not found"}), 404
#         if product.quantity < item['quantity']:
#             return jsonify({"error": f"Insufficient stock for {product.name}"}), 400
        
#         product.quantity -= item['quantity']
#         db.session.add(product)

#         sale_item = SaleItem(
#             sale_id=sale.id,
#             product_id=product.id,
#             product_name=product.name,
#             quantity=item['quantity'],
#             unit_price=product.price,
#             total_price=product.price * item['quantity'],
#             status=1
#         )
#         update_timestamps(sale_item)
#         total_amount += sale_item.total_price
#         cogs_total += product.price * item['quantity']
#         db.session.add(sale_item)

#     sale.total_amount = total_amount
#     update_timestamps(sale)
#     db.session.flush()

#     # Generate transaction number for GL
#     txn_id, txn_str = generate_transaction_number('INV')

#     # Double-entry: Revenue & COGS
#     entries = [
#         {"account_id": 1100, "transaction_type": "Debit", "amount": total_amount},  # Accounts Receivable
#         {"account_id": 4000, "transaction_type": "Credit", "amount": total_amount}, # Sales Revenue
#         {"account_id": 5000, "transaction_type": "Debit", "amount": cogs_total},    # COGS
#         {"account_id": 1200, "transaction_type": "Credit", "amount": cogs_total},   # Inventory
#     ]
#     gl_entries = post_to_ledger(entries, transaction_no_id=txn_id, description=f"Sale #{sale.id}")
#     sale.transaction_no = gl_entries[0].id

#     # # Create invoice linked to sale
#     # invoice = Invoice(
#     #     sale_id=sale.id,
#     #     invoice_number=txn_str,
#     #     total_amount=total_amount,
#     #     transaction_no=gl_entries[0].id,
#     #     status=1
#     # )
#     # update_timestamps(invoice)
#     # db.session.add(invoice)
#     # db.session.commit()

#     return jsonify({
#         "message": "Sale and invoice created with GL entries",
#         "sale_id": sale.id,
#         # "invoice_id": invoice.id,
#         "transaction_no": txn_str
#     }), 201

@sales_bp.route('/', methods=['POST'])
def create_sale():
    data = request.json
    items = data['items']  # [{"product_id":1,"quantity":2,"unit_price":50,"purchase_price":40}, ...]
    amount_paid = data.get('amount_paid', 0)  # frontend can send how much was paid upfront

    if not items or len(items) == 0:
        return jsonify({"error": "At least one item is required"}), 400


    # Create Sale
    sale = Sale(
        sale_number=data['sale_number'],
        customer_id=data.get('customer_id', 1),  # default Walk-in
        total_paid=amount_paid,
        status=1
    )
    db.session.add(sale)
    db.session.flush()  # get sale.id

    total_amount = 0
    cogs_total = 0

    for item_data in items:
        product = Product.query.get(item_data['product_id'])
        if not product:
            return jsonify({"error": f"Product {item_data['product_id']} not found"}), 404
        if product.quantity < item_data['quantity']:
            return jsonify({"error": f"Insufficient stock for {product.name}"}), 400

        # Reduce stock
        product.quantity -= item_data['quantity']
        db.session.add(product)

        # Use frontend price for total, purchase_price for COGS
        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=product.id,
            product_name=product.name,
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            total_price=item_data['unit_price'] * item_data['quantity'],
            status=1
        )
        db.session.add(sale_item)

        total_amount += sale_item.total_price
        cogs_total += item_data.get('purchase_price', 0) * item_data['quantity']

    sale.total_amount = total_amount

    # Calculate balance & update payment_status automatically
    sale.update_totals()

    db.session.flush()

    # Generate GL transaction
    txn_id, txn_str = generate_transaction_number('INV')
    entries = [
        {"account_id": 1100, "transaction_type": "Debit", "amount": total_amount},  # Accounts Receivable
        {"account_id": 4000, "transaction_type": "Credit", "amount": total_amount}, # Sales Revenue
        {"account_id": 5000, "transaction_type": "Debit", "amount": cogs_total},    # COGS
        {"account_id": 1200, "transaction_type": "Credit", "amount": cogs_total},   # Inventory
    ]
    gl_entries = post_to_ledger(entries, transaction_no_id=txn_id, description=f"Sale #{sale.id}")
    sale.transaction_no = gl_entries[0].id

    db.session.commit()

    return jsonify({
        "message": "Sale created successfully",
        "sale_id": sale.id,
        "total_amount": sale.total_amount,
        "total_paid": sale.total_paid,
        "balance": sale.balance,
        "payment_status": sale.payment_status,
        "transaction_no": txn_str
    }), 201


# ------------------ Get All Sales ------------------ #
@sales_bp.route('/', methods=['GET'])
def get_sales():
    sales = Sale.query.filter(Sale.status == 1).all()  # Only active
    data = []
    for s in sales:
        sale_items = SaleItem.query.filter_by(sale_id=s.id, status=1).all()
        items = [{
            "product_id": i.product_id,
            "product_name": i.product_name,
            "quantity": i.quantity,
            "unit_price": i.unit_price,
            "total_price": i.total_price
        } for i in sale_items]

        data.append({
            "sale_id": s.id,
            "sale_number": s.sale_number,
            "total_amount": s.total_amount,
            "payment_status": s.payment_status,
            "sale_date": s.sale_date,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
            "items": items
        })
    return jsonify(data)


# ------------------ Get Single Sale ------------------ #
@sales_bp.route('/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    sale_items = SaleItem.query.filter_by(sale_id=sale.id, status=1).all()

    items = [{
        "product_id": i.product_id,
        "product_name": i.product_name,
        "quantity": i.quantity,
        "unit_price": i.unit_price,
        "total_price": i.total_price
    } for i in sale_items]

    return jsonify({
        "sale_id": sale.id,
        "sale_number": sale.sale_number,
        "total_amount": sale.total_amount,
        "payment_status": sale.payment_status,
        "sale_date": sale.sale_date,
        "created_at": sale.created_at,
        "updated_at": sale.updated_at,
        "items": items
    })


# ------------------ Update Sale ------------------ #
@sales_bp.route('/<int:sale_id>', methods=['PUT'])
def update_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    data = request.json
    new_items = data.get('items')

    # Reverse old GL entries
    if sale.transaction_no:
        original_entries = GeneralLedger.query.filter_by(transaction_no=sale.transaction_no).all()
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

    # Update Sale main fields
    sale.sale_number = data.get('sale_number', sale.sale_number)
    sale.payment_status = data.get('payment_status', sale.payment_status)
    update_timestamps(sale)

    # Update sale items
    if new_items:
        # Restore stock from old items
        for item in sale.saleitem_set:
            product = Product.query.get(item.product_id)
            if product:
                product.quantity += item.quantity
                db.session.add(product)
            db.session.delete(item)

        # Add new items
        total_amount = 0
        for item in new_items:
            product = Product.query.get(item['product_id'])
            if not product:
                return jsonify({"error": f"Product {item['product_id']} not found"}), 404
            if product.quantity < item['quantity']:
                return jsonify({"error": f"Insufficient stock for {product.name}"}), 400

            product.quantity -= item['quantity']
            db.session.add(product)

            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                product_name=product.name,
                quantity=item['quantity'],
                unit_price=product.price,
                total_price=product.price * item['quantity'],
                status=1
            )
            update_timestamps(sale_item)
            total_amount += sale_item.total_price
            db.session.add(sale_item)

        sale.total_amount = total_amount

        # Post new GL entries
        txn_id, txn_no_str = generate_transaction_number('SAL')
        entries = [
            {"account_id": 1, "transaction_type": "Debit", "amount": total_amount},   # Cash/Bank
            {"account_id": 2, "transaction_type": "Credit", "amount": total_amount}  # Sales Revenue
        ]
        gl_entries = post_to_ledger(entries, txn_id, description=f"Sale #{sale.id} updated")
        sale.transaction_no = txn_id

    db.session.commit()
    return jsonify({"message": "Sale updated with GL entries", "sale_id": sale.id})


# ------------------ Soft Delete Sale (Status = 0) ------------------ #
@sales_bp.route('/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    sale.status = 0
    update_timestamps(sale)

    for item in sale.saleitem_set:
        item.status = 0
        update_timestamps(item)
        product = Product.query.get(item.product_id)
        if product:
            product.quantity += item.quantity
            db.session.add(product)

    # Reverse GL entries
    if sale.transaction_no:
        original_entries = GeneralLedger.query.filter_by(transaction_no=sale.transaction_no).all()
        for entry in original_entries:
            reverse_type = 'Credit' if entry.transaction_type == 'Debit' else 'Debit'
            reverse_entry = GeneralLedger(
                account_id=entry.account_id,
                transaction_type=reverse_type,
                amount=entry.amount,
                description=f"Reversal of {entry.description}",
                transaction_date=datetime.utcnow(),
                transaction_no=entry.transaction_no
            )
            db.session.add(reverse_entry)

    db.session.commit()
    return jsonify({"message": "Sale soft deleted and GL reversed", "sale_id": sale_id})
