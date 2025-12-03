# app/__init__.py — FINAL VERSION (Vue + Flask working perfectly)
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/')
    app.config.from_object('app.config.Config')
    app.config["SECRET_KEY"] = "sjhardwaresecretkey"

    db.init_app(app)
    migrate.init_app(app, db)

    # CORS — works for local dev AND production
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:5174", "*"]}},
        supports_credentials=True,
        expose_headers=["Content-Type", "Authorization"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"]
    )

    # ==================== IMPORT BLUEPRINTS ====================
    from app.routes.inventory import inventory_bp
    from app.routes.suppliers import suppliers_bp
    from app.routes.sales import sales_bp
    from app.routes.payments import payments_bp
    from app.routes.expenses import expenses_bp
    from app.routes.accounts import accounts_bp
    from app.routes.ledger import ledger_bp
    from app.routes.users import users_bp
    from app.routes.customer import customer_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.reports import reports_bp

    # Register them
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(expenses_bp, url_prefix='/api/expenses')
    app.register_blueprint(accounts_bp, url_prefix='/api/accounts')
    app.register_blueprint(ledger_bp, url_prefix='/api/ledgers')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(customer_bp, url_prefix='/api/customer')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')

    # ==================== SERVE VUE FRONTEND (THIS IS THE KEY!) ====================
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_vue(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, "index.html")

    return app