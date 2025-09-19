class Config:
    # Database (local)
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/smart_spend"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SECRET_KEY = "super_secret_key123"

    # Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'smartspend94@gmail.com'
    MAIL_PASSWORD = 'jgpt pkuf xrxb ykpt'
    MAIL_DEFAULT_SENDER = 'SmartSpend <smartspend94@gmail.com>'
