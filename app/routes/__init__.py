from flask import Flask
 # Handles user authentication (login, register, logout)
from app.routes.auth import auth_bp
# Handles the main dashboard view for users
from app.routes.dashboard import dashboard_bp
# Handles income/expense transaction routes
from app.routes.transactions import transaction_bp
# Handles reports (charts, analytics, summaries)
from app.routes.reports import report_bp
# Handles user settings/preferences
from app.routes.settings import settings_bp
# Handles monthly budget/summary routes
from app.routes.monthly import monthly_bp
# Handles reminders (payment due, receivable, etc.)
from app.routes.reminders import reminders_bp







# Register each blueprint with the main Flask app instance

def register_blueprints(app: Flask):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(monthly_bp)
    app.register_blueprint(reminders_bp)
