from flask import Flask
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.transactions import transaction_bp
from app.routes.reports import report_bp
from app.routes.settings import settings_bp
from app.routes.monthly import monthly_bp
from app.routes.reminders import reminders_bp

def register_blueprints(app: Flask):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(monthly_bp)
    app.register_blueprint(reminders_bp)
