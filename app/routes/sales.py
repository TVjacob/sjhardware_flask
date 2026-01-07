
from flask import Blueprint, request, jsonify
from app import db
from app.models import (
    Product, ProductUnit, Customer, Sale, SaleItem,
    InventoryTransaction, Payment, GeneralLedger, PurchaseOrderItem, Account
)
from app.utils.auth import token_required
from app.utils.gl_utils import post_to_ledger, generate_transaction_number_partone
from datetime import datetime
from sqlalchemy import desc, or_

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

# Helper: Get latest purchase unit_price for COGS
def get_latest_cost_price(product_id):
    latest = PurchaseOrderItem.query \
        .filter_by(product_id=product_id, status=1) \
        .order_by(desc(PurchaseOrderItem.id)) \
        .first()
    return float(latest.unit_price) if latest else 0.0

# ------------------ Create Sale with Product Units ------------------ #
@token_required
@sales_bp.route('/', methods=['POST'])
def create_sale():
    data = request.get_json()
    items = data.get('items', [])
    amount_paid = float(data.get('amount_paid', 0))
    payment_account_id = data.get('payment_account_id')
    sale_date_str = data.get('sale_date')
    customer_id = data.get('customer_id', 1)  # default walk-in

    if not items:
        return jsonify({"error": "At least one item is required"}), 400

    # Parse sale date
    try:
        sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d").date() if sale_date_str else datetime.utcnow().date()
    except:
        return jsonify({"error": "Invalid sale_date format. Use YYYY-MM-DD"}), 400

    if amount_paid > 0 and not payment_account_id:
        return jsonify({"error": "Payment account required when amount_paid > 0"}), 400

    try:
        total_amount = 0.0
        cogs_total = 0.0
        txn_id, txn_str = generate_transaction_number_partone('INV', transaction_date=sale_date)

        # Create Sale header
        sale = Sale(
            sale_number=txn_str,
            customer_id=customer_id,
            total_amount=0,  # will update later
            total_paid=amount_paid,
            balance=0,
            sale_date=sale_date,
            status=1
        )
        db.session.add(sale)
        db.session.flush()  # get sale.id

        # Process each item
        for item_data in items:
            product_id = item_data['product_id']
            unit_id = item_data.get('unit_id')
            quantity = float(item_data['quantity'])  # quantity in selected unit
            retail_price= float(item_data["unit_price"])


            product = Product.query.get_or_404(product_id)

            # Get unit
            if not unit_id:
                return jsonify({"error": f"unit_id required for product {product.name}"}), 400

            unit = ProductUnit.query.filter_by(id=unit_id, product_id=product_id, status=1).first()
            if not unit:
                return jsonify({"error": f"Invalid or inactive unit for product {product.name}"}), 400

            # Check stock in base units
            required_base_qty = quantity * unit.conversion_quantity
            if product.quantity < required_base_qty:
                return jsonify({"error": f"Insufficient stock for {product.name} ({unit.unit_name})"}), 400

            # Use unit retail price
            unit_price = float(retail_price or 0)
            item_total = unit_price * quantity

            # Deduct stock in base units
            product.quantity -= required_base_qty

            # Create SaleItem
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                unit_id=unit.id,
                product_name=product.name,
                quantity=quantity,  # in selected unit
                unit_price=unit_price,
                total_price=item_total,
                status=1
            )
            db.session.add(sale_item)

            # Inventory Transaction (outflow in base units)
            inv_txn = InventoryTransaction(
                transaction_no=txn_id,
                sale_id=sale.id,
                product_id=product.id,
                unit_id=unit.id,
                quantity=required_base_qty,  # stored in base units
                unit_price=get_latest_cost_price(product.id),  # for COGS
                total_price=get_latest_cost_price(product.id) * required_base_qty,
                transaction_type='Sale',
                status=1
            )
            db.session.add(inv_txn)

            total_amount += item_total
            cogs_total += get_latest_cost_price(product.id) * required_base_qty

        # Update sale totals
        sale.total_amount = total_amount
        sale.balance = total_amount - amount_paid

        # Set status
        if amount_paid >= total_amount:
            sale.status = 1  # Fully paid
        elif amount_paid > 0:
            sale.status = 4  # Partial
        else:
            sale.status = 3  # Credit

        # Post to General Ledger
        if amount_paid > 0:
            payment_account = Account.query.get(payment_account_id)
            if not payment_account:
                raise ValueError("Invalid payment account")

            entries = [
                # Debit payment account (Cash/Bank/Mobile)
                {"account_id": payment_account.code, "transaction_type": "Debit", "amount": amount_paid},
                # Credit Sales Revenue
                {"account_id": 4000, "transaction_type": "Credit", "amount": amount_paid},
            ]

            if sale.balance > 0:
                # Debit Accounts Receivable for credit portion
                entries.append({"account_id": 1100, "transaction_type": "Debit", "amount": sale.balance})
                # Credit Sales Revenue for full amount
                entries.append({"account_id": 4000, "transaction_type": "Credit", "amount": sale.balance})

            # COGS & Inventory
            entries += [
                {"account_id": 5000, "transaction_type": "Debit", "amount": cogs_total},  # COGS
                {"account_id": 1200, "transaction_type": "Credit", "amount": cogs_total},  # Inventory
            ]
        else:
            # Full credit sale
            entries = [
                {"account_id": 1100, "transaction_type": "Debit", "amount": total_amount},  # A/R
                {"account_id": 4000, "transaction_type": "Credit", "amount": total_amount},  # Sales
                {"account_id": 5000, "transaction_type": "Debit", "amount": cogs_total},
                {"account_id": 1200, "transaction_type": "Credit", "amount": cogs_total},
            ]

        post_to_ledger(
            entries,
            transaction_no_id=txn_id,
            description=f"Sale Invoice #{txn_str}",
            transaction_date=sale_date
        )

        sale.transaction_no = txn_id

        # Record payment if any
        if amount_paid > 0:
            payment = Payment(
                sale_id=sale.id,
                amount=amount_paid,
                payment_type=data.get('payment_type', 'Cash'),
                payment_date=sale_date,
                reference=txn_str,
                payment_account_id=payment_account_id,
                transaction_no=txn_id,
                status=1
            )
            db.session.add(payment)

        db.session.commit()

        return jsonify({
            "message": "Sale created successfully",
            "sale_id": sale.id,
            "sale_number": txn_str,
            "total_amount": total_amount,
            "amount_paid": amount_paid,
            "balance": sale.balance,
            "sale_date": sale_date.strftime("%Y-%m-%d")
        }), 201

    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Sale error: {e}")
        return jsonify({"error": "Failed to create sale"}), 500

# ------------------ Get All Sales ------------------ #
@token_required
@sales_bp.route('/', methods=['GET'])
def get_sales():
    search = request.args.get('search', '').strip()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Sale.query.join(Customer).filter(Sale.status.in_([1, 3, 4]))

    if search:
        query = query.filter(
            or_(
                Sale.sale_number.ilike(f"%{search}%"),
                Customer.name.ilike(f"%{search}%")
            )
        )

    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)

    sales = query.order_by(Sale.id.desc()).all()

    result = []
    for s in sales:
        items = SaleItem.query.filter_by(sale_id=s.id, status=1).all()
        items_data = []
        for i in items:
            unit = ProductUnit.query.get(i.unit_id) if i.unit_id else None
            items_data.append({
                "product_id": i.product_id,
                "product_name": i.product_name,
                "unit_name": unit.unit_name if unit else "Unknown",
                "quantity": float(i.quantity),
                "unit_price": float(i.unit_price),
                "total_price": float(i.total_price)
            })

        result.append({
            "id": s.id,
            "sale_id": s.id,
            "sale_number": s.sale_number,
            "customer_name": s.customer.name,
            "total_amount": float(s.total_amount),
            "total_paid": float(s.total_paid),
            "balance": float(s.balance),
            "sale_date": s.sale_date.strftime("%Y-%m-%d"),
            "status": s.status,
            "items": items_data
        })

    return jsonify(result)

# ------------------ Get Single Sale ------------------ #
@token_required
@sales_bp.route('/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    items = SaleItem.query.filter_by(sale_id=sale.id, status=1).all()
    items_data = []
    for i in items:
        unit = ProductUnit.query.get(i.unit_id) if i.unit_id else None
        items_data.append({
            "product_id": i.product_id,
            "product_name": i.product_name,
            "unit_id": i.unit_id,
            "unit_name": unit.unit_name if unit else "N/A",
            "quantity": float(i.quantity),
            "unit_price": float(i.unit_price),
            "total_price": float(i.total_price)
        })

    return jsonify({
        "id": sale.id,
        "sale_number": sale.sale_number,
        "customer_id": sale.customer_id,
        "customer_name": sale.customer.name,
        "total_amount": float(sale.total_amount),
        "total_paid": float(sale.total_paid),
        "balance": float(sale.balance),
        "sale_date": sale.sale_date.strftime("%Y-%m-%d"),
        "items": items_data
    })