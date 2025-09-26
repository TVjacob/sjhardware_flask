from flask import Blueprint, jsonify
from app.models import Category, GeneralLedger, SaleItem, PurchaseOrder, Expense,Customer, Supplier, Sale, PurchaseOrder, Product, Account
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload

from app.utils.auth import token_required


reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

# ------------------ General Ledger ------------------
@token_required
@reports_bp.route('/general-ledger', methods=['GET'])
def general_ledger():
    ledgers = db.session.query(
        GeneralLedger.id,
        GeneralLedger.transaction_date,
        GeneralLedger.transaction_type,
        GeneralLedger.amount,
        GeneralLedger.description,
        Account.name.label('account_name'),
        Account.account_type
    ).join(Account, GeneralLedger.account_id == Account.id).filter(GeneralLedger.status != 9).order_by(GeneralLedger.transaction_date.desc()).all()

    result = [{
        "id": g.id,
        "transaction_date": g.transaction_date.strftime('%Y-%m-%d'),
        "transaction_type": g.transaction_type,
        "amount": float(g.amount),
        "description": g.description,
        "account_name": g.account_name,
        "account_type": g.account_type
    } for g in ledgers]

    return jsonify(result)

# ------------------ Trial Balance ------------------
@token_required
@reports_bp.route('/trial-balance', methods=['GET'])
def trial_balance():
    # Group by account
    accounts = db.session.query(
        Account.id,
        Account.name,
        Account.account_type,
        func.coalesce(func.sum(GeneralLedger.amount), 0).label('balance')
    ).join(GeneralLedger, GeneralLedger.account_id == Account.id).filter(GeneralLedger.status != 9).group_by(Account.id).all()

    result = [{
        "account_id": a.id,
        "account_name": a.name,
        "account_type": a.account_type,
        "balance": float(a.balance)
    } for a in accounts]

    return jsonify(result)

# ------------------ Profit & Loss ------------------
@token_required
@reports_bp.route('/profit-loss', methods=['GET'])
def profit_loss():
    # Total sales
    total_sales = db.session.query(func.coalesce(func.sum(GeneralLedger.amount), 0)).join(Account).filter(
        GeneralLedger.status != 9,
        Account.account_type.ilike('%Revenue%')
    ).scalar()

    # Total expenses
    total_expenses = db.session.query(func.coalesce(func.sum(GeneralLedger.amount), 0)).join(Account).filter(
        GeneralLedger.status != 9,
        Account.account_type.ilike('%Expense%')
    ).scalar()

    result = {
        "total_sales": float(total_sales),
        "total_expenses": float(total_expenses),
        "net_profit": float(total_sales - total_expenses)
    }

    return jsonify(result)

# ------------------ Cash Flow ------------------
@token_required
@reports_bp.route('/cash-flow', methods=['GET'])
def cash_flow():
    # Cash inflows: Sales
    cash_inflow = db.session.query(func.coalesce(func.sum(GeneralLedger.amount), 0)).join(Account).filter(
        GeneralLedger.status != 9,
        Account.account_type.ilike('%Cash%')
    ).scalar()

    # Cash outflows: Purchases + Expenses
    cash_outflow = db.session.query(func.coalesce(func.sum(GeneralLedger.amount), 0)).join(Account).filter(
        GeneralLedger.status != 9,
        Account.account_type.ilike('%Payable%') | Account.account_type.ilike('%Expense%')
    ).scalar()

    result = {
        "cash_inflow": float(cash_inflow),
        "cash_outflow": float(cash_outflow),
        "net_cash_flow": float(cash_inflow - cash_outflow)
    }

    return jsonify(result)


# from flask import Blueprint, jsonify
# from app.models import Customer, Supplier, Sale, PurchaseOrder, Product, Expense, db
# from sqlalchemy import func
# from datetime import datetime, timedelta

# reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

# ------------------ Debtors Report ------------------
@token_required
@reports_bp.route('/debtors-report', methods=['GET'])
def debtors_report():
    # Only include customers with outstanding balance > 0
    debtors = db.session.query(
        Customer.id,
        Customer.name,
        Customer.phone,
        func.coalesce(func.sum(Sale.balance), 0).label('balance')
    ).join(Sale, Sale.customer_id == Customer.id).filter(
        Customer.status != 9,
        Sale.status != 9
    ).group_by(Customer.id).having(func.sum(Sale.balance) > 0).all()

    result = [{
        "id": d.id,
        "name": d.name,
        "phone": d.phone,
        "balance": float(d.balance)
    } for d in debtors]

    return jsonify(result)


# ------------------ Creditors Report ------------------
@token_required
@reports_bp.route('/creditors-report', methods=['GET'])
def creditors_report():
    # Only include suppliers with unpaid purchase orders
    creditors = db.session.query(
        Supplier.id,
        Supplier.name,
        Supplier.contact,
        func.coalesce(func.sum(PurchaseOrder.total_balance), 0).label('balance')
    ).join(PurchaseOrder, PurchaseOrder.supplier_id == Supplier.id).filter(
        Supplier.status != 9,
        PurchaseOrder.status != 9
    ).group_by(Supplier.id).having(func.sum(PurchaseOrder.total_balance) > 0).all()

    result = [{
        "id": c.id,
        "name": c.name,
        "phone": c.contact,
        "balance": float(c.balance)
    } for c in creditors]

    return jsonify(result)




# ------------------ Out of Stock ------------------
@token_required
@reports_bp.route('/out-of-stock', methods=['GET'])
def out_of_stock():
    products = db.session.query(Product,Category).join(Category,Product.category_id==Category.id).filter(Product.status != 9, Product.quantity <= 0).all()
    result = [{
        "id": p.id,
        "name": p.name,
        "sku": p.sku,
        "category_name": cat.name if cat.id else "N/A",
        "quantity": p.quantity
    } for p,cat in products]
    return jsonify(result)

# ------------------ Stock List ------------------
@token_required

@reports_bp.route('/stock-list', methods=['GET'])
def stock_list():
    # Use joinedload to avoid N+1 queries
    products = db.session.query(Product,Category).join(Category,Product.category_id==Category.id).filter(Product.status != 9).all()

    result = []
    for p, cat in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "category_name": cat.name if cat.id else "N/A",
            "quantity": p.quantity
        })

    return jsonify(result)

# ------------------ Consumption List ------------------
@token_required
@reports_bp.route('/consumption-list', methods=['GET'])
def consumption_list():
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Get sales in the last 7 days that are active
    sales = db.session.query(Sale).filter(Sale.status != 9, Sale.sale_date >= seven_days_ago).all()
    
    result = []

    for sale in sales:
        for item in sale.items:  # Loop through SaleItems
            result.append({
                "id": item.id,
                "product_name": item.product_name or (item.product.name if item.product else "N/A"),
                "quantity_sold": item.quantity,
                "total_amount": float(item.total_price),
                "sale_date": sale.sale_date.strftime('%Y-%m-%d')
            })
    
    return jsonify(result)

# ------------------ Performance List ------------------
@token_required
@reports_bp.route('/performance-list', methods=['GET'])
def performance_list():
    # Best performing products by revenue
    performance = (
        db.session.query(
            Product.id,
            Product.name,
            func.coalesce(func.sum(SaleItem.total_price), 0).label('total_revenue')
        )
        .join(SaleItem, SaleItem.product_id == Product.id)
        .filter(Product.status != 9, SaleItem.status != 9)
        .group_by(Product.id)
        .order_by(func.sum(SaleItem.total_price).desc())
        .all()
    )

    result = [{
        "product_id": p.id,
        "product_name": p.name,
        "total_revenue": float(p.total_revenue)
    } for p in performance]

    return jsonify(result)

# ------------------ Sales List ------------------
@token_required
@reports_bp.route('/sales-list', methods=['GET'])
def sales_list():
    sales = db.session.query(Sale).filter(Sale.status != 9).all()
    result = [{
        "id": s.id,
        "product_name": s.product.name if s.product else "N/A",
        "quantity": s.quantity,
        "total_amount": float(s.total_amount),
        "sale_date": s.sale_date.strftime('%Y-%m-%d')
    } for s in sales]
    return jsonify(result)

# ------------------ Purchases List ------------------
@token_required
@reports_bp.route('/purchases-list', methods=['GET'])
def purchases_list():
    purchases = db.session.query(PurchaseOrder).filter(PurchaseOrder.status != 9).all()
    result = [{
        "id": p.id,
        "product_name": p.product.name if p.product else "N/A",
        "quantity": p.quantity,
        "total_amount": float(p.total_amount),
        "purchase_date": p.purchase_date.strftime('%Y-%m-%d')
    } for p in purchases]
    return jsonify(result)

# ------------------ Expenses Report ------------------
@token_required
@reports_bp.route('/expenses-report', methods=['GET'])
def expenses_report():
    expenses = db.session.query(Expense).filter(Expense.status != 9).all()
    result = [{
        "id": e.id,
        "description": e.description,
        "amount": float(e.total_amount),
        "expense_date": e.expense_date.strftime('%Y-%m-%d')
    } for e in expenses]
    return jsonify(result)