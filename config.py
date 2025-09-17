import os

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost/smart_spend"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super_secret_key123')

    # Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'smartspend94@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'jgpt pkuf xrxb ykpt')
    MAIL_DEFAULT_SENDER = 'SmartSpend <smartspend94@gmail.com>'


    SERVER_NAME = 'smart-spend-1.onrender.com'
    PREFERRED_URL_SCHEME = 'https'
