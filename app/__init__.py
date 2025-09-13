from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_apscheduler import APScheduler




scheduler = APScheduler()
mail = Mail()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

# initialize SQLAlchemy with the app
    db.init_app(app)  
    
    mail.init_app(app)

    scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()


    

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.transactions import transaction_bp
    from app.routes.monthly import monthly_bp
    from app.routes.reports import report_bp
    from app.routes.settings import settings_bp
    from app.routes.reminders import reminders_bp



    #register blueprint
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(monthly_bp)
    app.register_blueprint(reminders_bp)

    return app
