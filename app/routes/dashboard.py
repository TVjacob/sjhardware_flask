from flask import Blueprint, jsonify
from app import db
from app.models import Product, Sale, SaleItem, Expense
from sqlalchemy import func
from datetime import datetime, timedelta

from app.utils.auth import token_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@token_required
@dashboard_bp.route('/metrics', methods=['GET'])
def get_dashboard_metrics():
    # ------------------ Total Products ------------------
    total_products = db.session.query(func.count(Product.id)) \
        .filter(Product.status != 9).scalar()

    # ------------------ Total Sales ------------------
    total_sales = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)) \
        .filter(Sale.status != 9).scalar()

    # ------------------ Total Expenses ------------------
    total_expenses = db.session.query(func.coalesce(func.sum(Expense.total_amount), 0)) \
        .filter(Expense.status != 9).scalar()

    # ------------------ Last 7 Days ------------------
    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days=6)
    days_list = [(seven_days_ago + timedelta(days=i)) for i in range(7)]

    # Sales Last 7 Days
    sales_data = dict(
        db.session.query(
            func.date(Sale.sale_date).label('day'),
            func.coalesce(func.sum(Sale.total_amount), 0)
        )
        .filter(Sale.status != 9, func.date(Sale.sale_date) >= seven_days_ago)
        .group_by(func.date(Sale.sale_date))
        .all()
    )
    sales_last_7_days = [
        {'day': day.strftime('%a'), 'amount': float(sales_data.get(day, 0))}
        for day in days_list
    ]

    # Expenses Last 7 Days
    expenses_data = dict(
        db.session.query(
            func.date(Expense.expense_date).label('day'),
            func.coalesce(func.sum(Expense.total_amount), 0)
        )
        .filter(Expense.status != 9, func.date(Expense.expense_date) >= seven_days_ago)
        .group_by(func.date(Expense.expense_date))
        .all()
    )
    expenses_last_7_days = [
        {'day': day.strftime('%a'), 'amount': float(expenses_data.get(day, 0))}
        for day in days_list
    ]

    # ------------------ Best Performing Products (by revenue) ------------------
    best_products = (
        db.session.query(
            SaleItem.product_id,
            func.coalesce(func.sum(SaleItem.total_price), 0).label('total_revenue')
        )
        .join(Sale)
        .filter(Sale.status != 9, SaleItem.status != 9)
        .group_by(SaleItem.product_id)
        .order_by(func.sum(SaleItem.total_price).desc())
        .limit(5)
        .all()
    )
    best_products_list = [
        {
            'product_id': p.product_id,
            'product_name': db.session.query(Product.name).filter(Product.id == p.product_id).scalar(),
            'total_revenue': float(p.total_revenue)
        } for p in best_products
    ]

    # ------------------ Least Performing Products (by revenue) ------------------
    least_products = (
        db.session.query(
            SaleItem.product_id,
            func.coalesce(func.sum(SaleItem.total_price), 0).label('total_revenue')
        )
        .join(Sale)
        .filter(Sale.status != 9, SaleItem.status != 9)
        .group_by(SaleItem.product_id)
        .order_by(func.sum(SaleItem.total_price).asc())
        .limit(5)
        .all()
    )
    least_products_list = [
        {
            'product_id': p.product_id,
            'product_name': db.session.query(Product.name).filter(Product.id == p.product_id).scalar(),
            'total_revenue': float(p.total_revenue)
        } for p in least_products
    ]

    return jsonify({
        'totalProducts': total_products,
        'totalSales': float(total_sales),
        'totalExpenses': float(total_expenses),
        'salesLast7Days': sales_last_7_days,
        'expensesLast7Days': expenses_last_7_days,
        'bestPerformingProducts': best_products_list,
        'leastPerformingProducts': least_products_list
    })
