import os

class Config:
    # Fallback to local dev if DATABASE_URL not set
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost/smart_spend"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'super_secret_key123'

    # Mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'kumalanup555@gmail.com'
    MAIL_PASSWORD = 'your_app_password'
    MAIL_DEFAULT_SENDER = 'kumalanup555@gmail.com'

    SERVER_NAME = 'smart-spend-1.onrender.com'
    PREFERRED_URL_SCHEME = 'https'
