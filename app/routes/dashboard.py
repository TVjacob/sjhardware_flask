# from operator import or_
from flask import Blueprint, jsonify, request
from app import db
from app.models import Category, Product, ProductUnit, PurchaseOrderItem, Sale, SaleItem, Expense, Customer, Supplier, PurchaseOrder
from sqlalchemy import func,or_
from datetime import datetime, timedelta

from app.utils.auth import token_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


# @token_required
# @dashboard_bp.route('/metrics', methods=['GET'])
# def get_dashboard_metrics():
#     today = datetime.utcnow().date()
#     seven_days_ago = today - timedelta(days=6)
#     days_list = [(seven_days_ago + timedelta(days=i)) for i in range(7)]

#     # ------------------ Totals ------------------
#     total_products = db.session.query(func.count(Product.id)).filter(Product.status != 9).scalar()
#     total_sales = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(Sale.status != 9).scalar()
#     total_expenses = db.session.query(func.coalesce(func.sum(Expense.total_amount), 0)).filter(Expense.status != 9).scalar()
#     total_customers = db.session.query(func.count(Customer.id)).filter(Customer.status != 9).scalar()
#     total_suppliers = db.session.query(func.count(Supplier.id)).filter(Supplier.status != 9).scalar()
#     total_purchase_orders = db.session.query(func.count(PurchaseOrder.id)).filter(PurchaseOrder.status != 9).scalar()
    
#     # ------------------ Outstanding Balances ------------------
#     outstanding_sales = db.session.query(func.coalesce(func.sum(Sale.balance), 0)).filter(Sale.status != 9).scalar()
#     outstanding_po = db.session.query(func.coalesce(func.sum(PurchaseOrder.total_balance), 0)).filter(PurchaseOrder.status != 9).scalar()

#     # ------------------ Sales Last 7 Days ------------------
#     sales_data = dict(
#         db.session.query(
#             func.date(Sale.sale_date).label('day'),
#             func.coalesce(func.sum(Sale.total_amount), 0)
#         )
#         .filter(Sale.status != 9, func.date(Sale.sale_date) >= seven_days_ago)
#         .group_by(func.date(Sale.sale_date))
#         .all()
#     )
#     sales_last_7_days = [{'day': day.strftime('%a'), 'amount': float(sales_data.get(day, 0))} for day in days_list]

#     # ------------------ Expenses Last 7 Days ------------------
#     expenses_data = dict(
#         db.session.query(
#             func.date(Expense.expense_date).label('day'),
#             func.coalesce(func.sum(Expense.total_amount), 0)
#         )
#         .filter(Expense.status != 9, func.date(Expense.expense_date) >= seven_days_ago)
#         .group_by(func.date(Expense.expense_date))
#         .all()
#     )
#     expenses_last_7_days = [{'day': day.strftime('%a'), 'amount': float(expenses_data.get(day, 0))} for day in days_list]

#     # ------------------ Best & Least Products by Revenue ------------------
#     best_products_query = (
#         db.session.query(SaleItem.product_id, func.coalesce(func.sum(SaleItem.total_price), 0).label('total_revenue'))
#         .join(Sale)
#         .filter(Sale.status != 9, SaleItem.status != 9)
#         .group_by(SaleItem.product_id)
#         .order_by(func.sum(SaleItem.total_price).desc())
#         .limit(5)
#         .all()
#     )
#     best_products = [{'product_id': p.product_id,
#                       'product_name': db.session.query(Product.name).filter(Product.id == p.product_id).scalar(),
#                       'total_revenue': float(p.total_revenue)} for p in best_products_query]

#     least_products_query = (
#         db.session.query(SaleItem.product_id, func.coalesce(func.sum(SaleItem.total_price), 0).label('total_revenue'))
#         .join(Sale)
#         .filter(Sale.status != 9, SaleItem.status != 9)
#         .group_by(SaleItem.product_id)
#         .order_by(func.sum(SaleItem.total_price).asc())
#         .limit(5)
#         .all()
#     )
#     least_products = [{'product_id': p.product_id,
#                        'product_name': db.session.query(Product.name).filter(Product.id == p.product_id).scalar(),
#                        'total_revenue': float(p.total_revenue)} for p in least_products_query]

#     return jsonify({
#         "totalProducts": total_products,
#         "totalSales": float(total_sales),
#         "totalExpenses": float(total_expenses),
#         "totalCustomers": total_customers,
#         "totalSuppliers": total_suppliers,
#         "totalPurchaseOrders": total_purchase_orders,
#         "outstandingSales": float(outstanding_sales),
#         "outstandingPO": float(outstanding_po),
#         "salesLast7Days": sales_last_7_days,
#         "expensesLast7Days": expenses_last_7_days,
#         "bestPerformingProducts": best_products,
#         "leastPerformingProducts": least_products
#     })
@dashboard_bp.route("/metrics", methods=["GET"])
@token_required
def get_dashboard_metrics():
    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days=6)
    days_list = [(seven_days_ago + timedelta(days=i)) for i in range(7)]

    # ------------------ Totals ------------------
    total_products = db.session.query(func.count(Product.id)).filter(Product.status != 9).scalar() or 0
    total_sales = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(Sale.status != 9).scalar() or 0
    total_expenses = db.session.query(func.coalesce(func.sum(Expense.total_amount), 0)).filter(Expense.status != 9).scalar() or 0
    total_customers = db.session.query(func.count(Customer.id)).filter(Customer.status != 9).scalar() or 0
    total_suppliers = db.session.query(func.count(Supplier.id)).filter(Supplier.status != 9).scalar() or 0
    total_purchase_orders = db.session.query(func.count(PurchaseOrder.id)).filter(PurchaseOrder.status != 9).scalar() or 0
    
    # ------------------ Outstanding Balances ------------------
    outstanding_sales = db.session.query(func.coalesce(func.sum(Sale.balance), 0)).filter(Sale.status != 9, Sale.status!=1).scalar() or 0
    outstanding_po = db.session.query(func.coalesce(func.sum(PurchaseOrder.total_balance), 0)).filter(PurchaseOrder.status != 9).scalar() or 0

    # ------------------ Sales Last 7 Days ------------------
    sales_data = dict(
        db.session.query(
            func.date(Sale.sale_date).label('day'),
            func.coalesce(func.sum(Sale.total_amount), 0)
        )
        .filter(Sale.status != 9, func.date(Sale.sale_date) >= seven_days_ago)
        .group_by(func.date(Sale.sale_date))
        .all()
    )
    sales_last_7_days = [{'day': day.strftime('%a'), 'amount': float(sales_data.get(day, 0))} for day in days_list]

    # ------------------ Expenses Last 7 Days ------------------
    expenses_data = dict(
        db.session.query(
            func.date(Expense.expense_date).label('day'),
            func.coalesce(func.sum(Expense.total_amount), 0)
        )
        .filter(Expense.status != 9, func.date(Expense.expense_date) >= seven_days_ago)
        .group_by(func.date(Expense.expense_date))
        .all()
    )
    expenses_last_7_days = [{'day': day.strftime('%a'), 'amount': float(expenses_data.get(day, 0))} for day in days_list]

    # ------------------ Best & Least Products ------------------
    best_products_query = (
        db.session.query(SaleItem.product_id, func.coalesce(func.sum(SaleItem.total_price), 0).label('total_revenue'))
        .join(Sale)
        .filter(Sale.status != 9, SaleItem.status != 9)
        .group_by(SaleItem.product_id)
        .order_by(func.sum(SaleItem.total_price).desc())
        .limit(5)
        .all()
    )
    best_products = [
        {'product_id': p.product_id,
         'product_name': db.session.query(Product.name).filter(Product.id == p.product_id).scalar() or 'Unknown',
         'total_revenue': float(p.total_revenue)}
        for p in best_products_query
    ]

    least_products_query = (
        db.session.query(SaleItem.product_id, func.coalesce(func.sum(SaleItem.total_price), 0).label('total_revenue'))
        .join(Sale)
        .filter(Sale.status != 9, SaleItem.status != 9)
        .group_by(SaleItem.product_id)
        .order_by(func.sum(SaleItem.total_price).asc())
        .limit(5)
        .all()
    )
    least_products = [
        {'product_id': p.product_id,
         'product_name': db.session.query(Product.name).filter(Product.id == p.product_id).scalar() or 'Unknown',
         'total_revenue': float(p.total_revenue)}
        for p in least_products_query
    ]

    return jsonify({
        "totalProducts": total_products,
        "totalSales": float(total_sales),
        "totalExpenses": float(total_expenses),
        "totalCustomers": total_customers,
        "totalSuppliers": total_suppliers,
        "totalPurchaseOrders": total_purchase_orders,
        "outstandingSales": float(outstanding_sales),
        "outstandingPO": float(outstanding_po),
        "salesLast7Days": sales_last_7_days,
        "expensesLast7Days": expenses_last_7_days,
        "bestPerformingProducts": best_products,
        "leastPerformingProducts": least_products
    })