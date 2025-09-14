from flask import Blueprint,flash,render_template,url_for,redirect,session
from app.models import Transaction,Budget
from sqlalchemy import desc,func
from app import db
from app.forms import TransactionForm
from datetime import datetime

# Blueprint for all transaction routes
transaction_bp=Blueprint('transaction_bp',__name__)

#transcations route
@transaction_bp.route('/Transaction')
def transaction():
    # Only logged-in users can access
    if 'user_id' not in session:
        flash('Please Login first','danger')
        return redirect(url_for('auth_bp.login'))
    

    user_id=session['user_id']

    # Fetch all user transactions
    transaction=Transaction.query.filter_by(user_id=user_id).all()


    #recent transaction of recent transactioons 
    recent_trans = Transaction.query.filter_by(user_id=user_id).order_by(desc(Transaction.date)).limit(5).all()

    return render_template('transaction.html',transaction=transaction,recent_trans=recent_trans)








#for add expenses and income
@transaction_bp.route('/ADD_Transaction',methods=['GET','POST'])
def add_transaction():
    if 'user_id' not in session:
        flash(f'please login first','danger')
        return redirect(url_for('auth_bp.login'))
    
    form=TransactionForm()
    if form.validate_on_submit():
        try:
            user_id=session['user_id']
            amount=float(form.amount.data)
            category=form.category.data
            description=form.description.data
            date=form.date.data
            T_type=form.type.data

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
    return render_template('add_transaction.html',form=form)







#Edit the income and expenses
@transaction_bp.route('/edit_transaction/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('auth_bp.login'))

    # fetch transactions by ID
    transaction = Transaction.query.filter_by(id=id, user_id=session['user_id']).first()
    if not transaction:
        flash('Transaction not found', 'danger')
        return redirect(url_for('transaction_bp.transaction'))  

    # Pre-fill form with current values
    form = TransactionForm(obj=transaction)

    if form.validate_on_submit():
        try:
            # Update transaction fields
            transaction.amount = float(form.amount.data)
            transaction.category = form.category.data
            transaction.date = form.date.data
            transaction.description = form.description.data
            transaction.type = form.type.data  # allow changing type if needed
            db.session.commit()

            flash(f'{transaction.type.capitalize()} updated successfully!', 'success')

            # Redirect based on type
            if transaction.type == 'expense':
                return redirect(url_for('transaction_bp.transaction'))
            else:
                return redirect(url_for('transaction_bp.transaction'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating transaction: {e}', 'danger')

    return render_template('edit_transaction.html', form=form, transaction=transaction)




             

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
