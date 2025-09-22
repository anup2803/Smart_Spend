from app import db


class User(db.Model):
    __tablename__ = 'register'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    phonenumber=db.Column(db.String(10),nullable=False,unique=True)
    password = db.Column(db.String(200), nullable=False)
    is_verified=db.Column(db.Boolean, default=False)  
    created_at=db.Column(db.DateTime,default=db.func.now()) 


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('register.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200))


class Budget(db.Model):
    __tablename__='budget'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('register.id'))
    category = db.Column(db.String(50))
    amount = db.Column(db.Float)
    month = db.Column(db.Integer)   
    year = db.Column(db.Integer)



class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reminder_type = db.Column(db.String(50), nullable=False)  # Payable or Receivable
    category = db.Column(db.String(50), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    amount=db.Column(db.Integer,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('register.id'), nullable=False)
    notified = db.Column(db.Boolean, default=False)    # Email notification sent status

