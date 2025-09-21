from flask import Flask,redirect,url_for,session,flash,render_template,jsonify,Blueprint
from app.models import Transaction,Budget,User
from sqlalchemy import func,desc,extract
from app import db
from datetime import datetime


# blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard_bp', __name__)





@dashboard_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('auth_bp.login'))

    try:
        user_id = session['user_id']
        summary_data = []
        user = User.query.filter_by(id=user_id).first()

        today = datetime.now()
        current_month = today.month
        current_year = today.year

        # Fetch all budgets (you can filter to current month if needed)
        budgets = Budget.query.filter_by(user_id=user_id).all()

        # Total Income and Expense for current month
        Total_Income = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'income',
            extract('month', Transaction.date) == current_month,
            extract('year', Transaction.date) == current_year
        ).scalar() or 0

        Total_Expense = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            extract('month', Transaction.date) == current_month,
            extract('year', Transaction.date) == current_year
        ).scalar() or 0

        # Recent 5 transactions (latest first)
        recent_trans = Transaction.query.filter_by(user_id=user_id).order_by(desc(Transaction.date)).limit(5).all()

        for b in budgets:
            category = b.category
            total_budget = b.amount

            # Expenses only for the month/year of the budget
            total_expense = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.category == category,
                extract('month', Transaction.date) == b.month,
                extract('year', Transaction.date) == b.year
            ).scalar() or 0

            remaining_balance = total_budget - total_expense

            percentage = round((total_expense / total_budget) * 100, 2) if total_budget else 0

            if percentage < 50:
                color_class = "progress-green"
            elif percentage < 80:
                color_class = "progress-orange"
            else:
                color_class = "progress-red"

            summary_data.append({
                "category": category,
                "total_budget": total_budget,
                "total_expense": total_expense,
                "remaining": remaining_balance,
                "percentage": percentage,
                "color_class": color_class
            })

        # Optional: show only first 2 summaries (keep your previous logic)
        summary_data = summary_data[:2]

        return render_template(
            'dashboard.html',
            user=user,
            Total_Income=Total_Income,
            Total_expense=Total_Expense,
            recent_trans=recent_trans,
            summaries=summary_data
        )

    except Exception as e:
        flash(f'Error Occurred: {e}', 'danger')
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


