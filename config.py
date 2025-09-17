import os

class Config:
   
    # Database configuration
    # Use DATABASE_URL from environment (Render/production) or fallback to local MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost/smart_spend"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    
    # Security
   
    SECRET_KEY = 'super_secret_key123'  # change this for production

    
    # Flask-Mail configuration
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'smartspend94@gmail.com'
    MAIL_PASSWORD = 'jgpt pkuf xrxb ykpt'  # replace with your actual app password
    MAIL_DEFAULT_SENDER = 'SmartSpend <smartspend94@gmail.com>'  # must be a string

   
    # Flask app URL settings

    SERVER_NAME = 'smart-spend-1.onrender.com'
    PREFERRED_URL_SCHEME = 'https'
