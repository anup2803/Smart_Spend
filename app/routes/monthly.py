from flask import render_template,session,url_for,redirect,flash,Blueprint
from app.models import Budget, Transaction
from app.forms import BudgetForm
from sqlalchemy import func
from app import db
from datetime import datetime

#blueprint object created
monthly_bp=Blueprint('monthly_bp',__name__)



#monthly route 
@monthly_bp.route('/monthly', methods=['GET', 'POST'])
def monthly():
    if 'user_id' not in session:
        flash('Please login first','danger')
        return redirect(url_for('auth_bp.login'))
    
    user_id = session['user_id']
    form = BudgetForm()

    if form.validate_on_submit():
        category = form.category.data
        amount = form.amount.data

        existing = Budget.query.filter_by(user_id=user_id, category=category).first()
        if existing:
            existing.amount = amount
            flash(f'Budget for {category} updated!', 'success')
        else:
            new_budget = Budget(user_id=user_id, category=category, amount=amount)
            db.session.add(new_budget)
            flash(f'Budget for {category} set!', 'success')

        db.session.commit()
        return redirect(url_for('monthly_bp.monthly'))
    



     # Fetch all budgets for this user
    budgets = Budget.query.filter_by(user_id=user_id).all()
    budget_data=[]

    for b in budgets:
         # Total spent for this category in current month
         total_used=db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.category == b.category,
            Transaction.type == 'expense',
            func.extract('month', Transaction.date) == datetime.now().month,
            func.extract('year', Transaction.date) == datetime.now().year
         ).scalar() or 0

         budget_data.append({
             "category": b.category,
            "budget": b.amount,
            "spent": total_used,
            "remaining": b.amount - total_used
         })


    return render_template('monthly_budget.html', form=form, budget_data=budget_data)
