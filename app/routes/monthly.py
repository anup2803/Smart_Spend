from flask import render_template,session,url_for,redirect,flash,Blueprint,make_response,request
from app.models import Budget, Transaction,User
from app.forms import BudgetForm
from sqlalchemy import func
from app import db
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from io import BytesIO

#blueprint object created
monthly_bp=Blueprint('monthly_bp',__name__)



#monthly routes
@monthly_bp.route('/monthly', methods=['GET', 'POST'])
def monthly():
    if 'user_id' not in session:
        flash('Please login first','danger')
        return redirect(url_for('auth_bp.login'))
    
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)  # Get current page
    per_page = 2  # Show 2 budgets per page
    form = BudgetForm()
    user = User.query.filter_by(id=user_id).first()

    current_month = datetime.now().month
    current_year = datetime.now().year

    # --- Handle Form Submission ---
    if form.validate_on_submit():
        category = form.category.data
        amount = form.amount.data
        
        existing = Budget.query.filter_by(user_id=user_id, category=category).first()
        if existing:
            existing.amount = amount
            flash(f'Budget for {category} updated!', 'success')
        else:
            new_budget = Budget(
                user_id=user_id,
                category=category,
                amount=amount,
                month=current_month,
                year=current_year
            )
            db.session.add(new_budget)
            flash(f'Budget for {category} set!', 'success')

        db.session.commit()
        return redirect(url_for('monthly_bp.monthly'))

    # --- Fetch Budgets with Pagination ---
    budgets = Budget.query.filter_by(user_id=user_id).paginate(page=page, per_page=2)

    budget_data = []
    for b in budgets.items:  # Only fetch budgets for current page
        total_used = db.session.query(func.sum(Transaction.amount)).filter(
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
            "remaining": b.amount - total_used,
            "month": b.month,
            "year": b.year,
            "date_str": f"{b.month}/{b.year}"
        })

    return render_template(
        'monthly_budget.html',
        form=form,
        budget_data=budget_data,
        user=user,
        budgets=budgets  # Pass pagination object
    )





    
#export pdf of Past Monthly Budgets reports
@monthly_bp.route('/current_monthly_budgets')
def current_monthly_budgets():
    #only login user can access and export all user current monthly budgets as pdf file .
    if 'user_id' not in session:
        flash("Please login first","danger")
        return  redirect(url_for('auth_bp.login'))
    

    try:
        user_id=session['user_id']

        today = datetime.now()
        current_month = today.month
        current_year = today.year
        
        #past budget reports
        current_budget = Budget.query.filter_by(user_id=user_id,month=current_month,year=current_year).all()


        #if no transactions
        if not current_budget:
            flash("No Past Monthly Budget found to export","danger")
            return redirect(url_for('monthly_bp.monthly'))
        
        # Prepare PDF in memory
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer,pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        #title
        elements.append(Paragraph('Monthly Budget Report', styles['Title']))
        elements.append(Paragraph(f"{today.strftime('%B %Y')}",styles['Heading2']))
        elements.append(Spacer(1,12))



        #table header+data
        data=[["#", "Category", "Amount"]]
        for idx, t in enumerate(current_budget, start=1):
            data.append([idx, t.category, f"Rs {t.amount}"])


         # Table style
        table = Table(data, colWidths=[40, 200, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        # Footer
        elements.append(Paragraph(
            f"Generated on {today.strftime('%d %B %Y, %I:%M %p')}",
            styles['Normal']
        ))


        doc.build(elements)

        # Send as response
        pdf=buffer.getvalue()
        buffer.close()
        response= make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=Monthly_Budget.pdf'
        return response
    

    except Exception as e:
        flash(f"Error Occurred: {str(e)}", "danger")
        return redirect(url_for('monthly_bp.monthly'))


