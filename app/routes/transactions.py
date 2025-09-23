from flask import Blueprint,flash,render_template,url_for,redirect,session
from app.models import Transaction,Budget,User
from sqlalchemy import desc,func
from app import db
from app.forms import TransactionForm
from datetime import datetime
from datetime import date

# Blueprint for all transaction routes
transaction_bp=Blueprint('transaction_bp',__name__)

#transcations route
@transaction_bp.route('/transaction')
def transaction():
    # Only logged-in users can access
    if 'user_id' not in session:
        flash('Please Login first','danger')
        return redirect(url_for('auth_bp.login'))
    

    user_id=session['user_id']

    # Fetch all user transactions
    transaction=Transaction.query.filter_by(user_id=user_id).all()
    user = User.query.filter_by(id=user_id).first()


    #recent transaction of recent transactioons 
    recent_trans = Transaction.query.filter_by(user_id=user_id).order_by(desc(Transaction.date)).limit(5).all()

    return render_template('transaction.html',transaction=transaction,recent_trans=recent_trans,user=user,page_title="Transactions")








#for add expenses and income
@transaction_bp.route('/add_Transaction',methods=['GET','POST'])
def add_transaction():
    if 'user_id' not in session:
        flash(f'please login first','danger')
        return redirect(url_for('auth_bp.login'))
    
    user_id = session['user_id']   
    user = User.query.get(user_id)

    form=TransactionForm()
    if form.validate_on_submit():
        try:
            user_id=session['user_id']
            amount=float(form.amount.data)
            category=form.category.data
            description=form.description.data
            date=form.date.data
            T_type=form.type.data



            # Fetch only future reminders
            now = datetime.now().date()
            transaction_date = date
      

             # Ensure the reminder is in the future
            if transaction_date > now:
             flash("Cannot set a transactions in future!", "danger")
             return redirect(url_for('transaction_bp.add_transaction'))

            # check budget only for expenses
            if T_type=='expense':
                budget=Budget.query.filter_by(user_id=user_id,category=category).first()
                if budget:
                    # calculate total spent in this category for the same month
                    total_used=db.session.query(func.sum(Transaction.amount)).filter(
                        Transaction.user_id==user_id,
                        Transaction.category==category,
                        Transaction.type=='expense',
                        func.MONTH(Transaction.date) == date.month,
                        func.YEAR(Transaction.date) == date.year
                    ).scalar() or 0
                     
                    # if expense exceeds budget → prevent saving
                    if total_used +amount >budget.amount:
                        flash(f"⚠️ Cannot add expense! It exceeds your monthly budget of {budget.amount} for {category}.", 'danger')
                        return redirect(url_for('transaction_bp.add_transaction'))  
            

            #save new transactions
            new_transaction=Transaction(user_id=user_id,amount=amount,category=category,description=description,date=date,type=T_type)
            db.session.add(new_transaction)
            db.session.commit()
            flash(f'{form.type.data.capitalize()} added successfully!', 'success')
            return redirect(url_for('transaction_bp.transaction'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
    return render_template('add_transaction.html',form=form,user=user,page_title="Add Transactions")
    






#Edit the income and expenses


@transaction_bp.route('/edit_transaction/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id) 

    # fetch transaction by ID
    transaction = Transaction.query.filter_by(id=id, user_id=user_id).first()
    if not transaction:
        flash('Transaction not found', 'danger')
        return redirect(url_for('transaction_bp.transaction'))  

    # Pre-fill form with current values
    form = TransactionForm(obj=transaction)

    if form.validate_on_submit():
        try:
            new_amount = float(form.amount.data)
            new_category = form.category.data
            new_date = form.date.data
            new_type = form.type.data

            # Prevent future dates
            if new_date > date.today():
                flash("Cannot set transaction date in the future.", "danger")
                return redirect(url_for('transaction_bp.edit_transaction', id=id))

            # --- Only enforce budget check for expenses ---
            if new_type == "expense":
                current_month = new_date.month
                current_year = new_date.year

                budget = Budget.query.filter_by(
                    user_id=user_id,
                    category=new_category,
                    month=current_month,
                    year=current_year
                ).first()

                if budget:
                    total_spent = db.session.query(func.sum(Transaction.amount)).filter(
                        Transaction.user_id == user_id,
                        Transaction.category == new_category,
                        Transaction.type == 'expense',
                        func.extract('month', Transaction.date) == current_month,
                        func.extract('year', Transaction.date) == current_year
                    ).scalar() or 0

                    # Adjust total by removing old transaction and adding new
                    adjusted_spent = total_spent - transaction.amount + new_amount

                    if adjusted_spent > budget.amount:
                        flash(f"Cannot update. This would exceed your budget of Rs {budget.amount} for {budget.category}.", "danger")
                        return redirect(url_for('transaction_bp.edit_transaction', id=id))

            # Update transaction fields
            transaction.amount = new_amount
            transaction.category = new_category
            transaction.date = new_date
            transaction.description = form.description.data
            transaction.type = new_type  

            db.session.commit()
            flash(f'{transaction.type.capitalize()} updated successfully!', 'success')
            return redirect(url_for('transaction_bp.transaction'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating transaction: {e}', 'danger')

    return render_template(
        'edit_transaction.html',
        form=form,
        transaction=transaction,
        user=user,
        page_title="Edit Transactions"
    )



             

#delete transaction
@transaction_bp.route('/delete_transaction/<int:id>', methods=['POST'])
def delete_transaction(id):
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('auth_bp.login'))

    try:
        # fetch transactions by ID
        transaction = Transaction.query.filter_by(id=id, user_id=session['user_id']).first()
        if not transaction:
            flash('Transaction not found', 'danger')
            return redirect(url_for('transaction_bp.transaction'))
        
        # delete transaction
        db.session.delete(transaction)
        db.session.commit()
        flash(f'{transaction.type.capitalize()} deleted successfully!', 'success')
        
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting transaction: {e}', 'danger')
        
    return redirect(url_for('transaction_bp.transaction'))
