from flask import Flask,redirect,url_for,session,flash,render_template,jsonify,Blueprint
from app.models import Transaction
from sqlalchemy import func,desc,extract
from app import db
from datetime import datetime

# blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard_bp', __name__)



#dashboard route 
@dashboard_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('auth_bp.login'))

    try:
     user_id=session['user_id']

    #total income 
     Total_Income = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id, type='income').scalar()

   #total expense
     Total_expense=db.session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id,type='expense').scalar()
    
  #remaing balance never neagtive
     reamaing_balance=0
     if Total_Income is not None:
      reamaing_balance=max(Total_Income-(Total_expense or 0), 0)



   # Recent transactions (last recent  5 transactions)
     recent_trans = Transaction.query.filter_by(user_id=user_id).order_by(desc(Transaction.date)).limit(5).all()


   
     return render_template('dashboard.html',Total_Income=Total_Income,Total_expense=Total_expense,reamaing_balance=reamaing_balance,recent_trans=recent_trans)

    except Exception as e:
        flash(f'Error Occur{e}','danger')
        return render_template('dashboard.html')




#graph
@dashboard_bp.route('/data')
def data():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 403
    

    try: 
     user_id=session['user_id']


    #Monthly expense 
     monthly_expenses = db.session.query(extract('month', Transaction.date).label('month'),func.sum(Transaction.amount)).filter_by(user_id=user_id, type='expense').filter(extract('year', Transaction.date) == datetime.now().year).group_by('month') .order_by('month').all()


    #Monthly income
     monthly_incomes=db.session.query(extract('month', Transaction.date).label('month'),func.sum(Transaction.amount)).filter_by(user_id=user_id, type='income').filter(extract('year', Transaction.date) == datetime.now().year).group_by('month') .order_by('month').all()

    # List of month labels (Jan → Dec)
     months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


     expense_data = [0]*12
     income_data = [0]*12

    # Fill expense data by month index
     for m, amt in monthly_expenses:
        expense_data[int(m)-1] = float(amt)
    # Fill income data by month index
     for m, amt in monthly_incomes:
        income_data[int(m)-1] = float(amt)

     #returen to json response to frontend for charts 
     return jsonify({'months': months,
                     'expenses': expense_data,
                     'income': income_data})
    except Exception as e:
        return jsonify({'error':str(e)}),500

