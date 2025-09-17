class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/smart_spend'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'super_secret_key123'



    # # Flask app domain settings
    # SERVER_NAME = '6f21-102-45-89-34.ngrok.io'   # or 'yourdomain.com' in production
    # PREFERRED_URL_SCHEME = 'https'


    # Flask-Mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'kumalanup555@gmail.com'
    MAIL_PASSWORD = 'lbhh uuad rkek ovnc' 
    MAIL_DEFAULT_SENDER = 'kumalanup555@gmail.com'