from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    # Enable CORS globally
    CORS(app, resources={r"/api/*": {"origins": "*"}})  # You can restrict origins

    from app.routes.inventory import inventory_bp
    from app.routes.suppliers import suppliers_bp
    from app.routes.sales import sales_bp
    from app.routes.payments import payments_bp
    from app.routes.expenses import expenses_bp
    from app.routes.accounts import accounts_bp
    from app.routes.ledger import ledger_bp
    from app.routes.users import users_bp
    from app.routes.customer import customer_bp


    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(expenses_bp, url_prefix='/api/expenses')
    app.register_blueprint(accounts_bp, url_prefix='/api/accounts')
    app.register_blueprint(ledger_bp, url_prefix='/api/ledgers')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(customer_bp, url_prefix='/api/customer')


    return app
