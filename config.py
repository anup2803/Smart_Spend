import os
class Config:
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@@aws.connect.psdb.cloud/smart_spend'  its used for development 

    #but for production Database connection (Render will pull from environment variable)
    SQLALCHEMY_DATABASE_URI =os.environ.get("DATABASE_URL")
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/smart_spend'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'super_secret_key123'



    # Flask app domain settings
    SERVER_NAME = 'smart-spend-1.onrender.com'   # or 'yourdomain.com' in production
    PREFERRED_URL_SCHEME = 'https'


    # Flask-Mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'kumalanup555@gmail.com'
    MAIL_PASSWORD = 'lbhh uuad rkek ovnc' 
    MAIL_DEFAULT_SENDER = 'kumalanup555@gmail.com'


