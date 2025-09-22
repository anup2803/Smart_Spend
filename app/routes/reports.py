from flask import jsonify,flash,Blueprint,render_template,redirect,url_for,session,make_response,request
from sqlalchemy import func,desc
from app import db
from app.models import Transaction,User,Budget
from io import BytesIO,StringIO
import csv
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from datetime import datetime


#blueprint for the reports
report_bp=Blueprint('report_bp',__name__)




#report route
@report_bp.route('/report_analysis')
def report_analysis():
    if 'user_id' not in session:
        flash("Please Login first","danger")
        return redirect(url_for('auth_bp.login'))
    

    try:
      user_id=session.get('user_id')


      user = User.query.filter_by(id=user_id).first()


      today = datetime.now()
      if today.month == 1:
       prev_month = 12
       prev_year = today.year - 1
      else:
        prev_month = today.month - 1
        prev_year = today.year

    #total income 
      Total_Income = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id, type='income').scalar() or 0




   #total expense
      Total_expense=db.session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id,type='expense').scalar() or 0


    #Net income 
      Net_income = max(Total_Income - Total_expense, 0)

    
    #past budget reports
      past_budget = Budget.query.filter_by(user_id=user_id,month=prev_month,year=prev_year).limit(5).all()

      
   # Recent transactions (last 5)
      recent_trans = Transaction.query.filter_by(user_id=user_id).order_by(desc(Transaction.date)).limit(5).all()




      return render_template('reports.html',Total_Income=Total_Income,Total_expense=Total_expense,Net_income=Net_income,recent_trans=recent_trans,user=user,past_budget=past_budget,page_title="Reports & Analysis")

    except Exception as e:
          flash(f"Error generating report: {e}", "danger")
          return redirect(url_for('report_bp.report_analysis'))





#export pdf of transactions
@report_bp.route('/export_pdf')
def export_pdf():
    #only login user can access and export all user transactions as pdf file .
    if 'user_id' not in session:
        flash("Please login first","danger")
        return  redirect(url_for('auth_bp.login'))
    

    try:
        user_id=session['user_id']

        today = datetime.now()
        
        #get all user transactions by user_id 
        transactions=Transaction.query.filter_by(user_id=user_id).all()


        #if no transactions
        if not transactions:
            flash("No transactions found to export","danger")
            return redirect(url_for('report_bp.report_analysis'))
        
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
        data=[["#", "Category","Type","Date", "Amount"]]
        for idx, t in enumerate(transactions, start=1):
            data.append([idx, t.category, t.type,t.date.strftime('%Y-%m-%d'),f"Rs {t.amount}"])


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
        response.headers['Content-Disposition'] = 'attachment; filename=transactions.pdf'
        return response
    

    except Exception as e:
        flash(f"Error Occurred: {str(e)}", "danger")
        return redirect(url_for('report_bp.report_analysis'))



#download csv 
@report_bp.route('/download_csv')
def download_csv():
    #Export all user transactions as CSV file.
    if 'user_id' not in session:
        flash("Please login first","danger")
        return redirect(url_for('auth_bp.login'))
    

    user_id=session['user_id']

    try: 
     transactions=Transaction.query.filter_by(user_id=user_id).all()

     if not transactions:
            flash("No transactions to export", "danger")
            return redirect(url_for('report_bp.report_analysis'))
    

     # Write CSV to memory
     output=StringIO()
     writer=csv.writer(output)

     # Header row
     writer.writerow(["ID", "Type", "Category", "Amount", "Date"])
    

     # Data rows
     for t in transactions:
        writer.writerow([
            t.id,
            t.type,
            t.category,
            t.amount,
            t.date.strftime('%Y-%m-%d')

        ])


     # Build response
     response=make_response(output.getvalue())
     response.headers['Content-Disposition'] = 'attachment; filename=transactions.csv'
     response.headers['Content-Type'] = 'text/csv'
     return response


    except Exception as e:
        flash(f"Error Occurred: {str(e)}", "danger")
        return redirect(url_for('report_bp.report_analysis'))
    



    
#export pdf of Past Monthly Budgets reports
@report_bp.route('/past_monthly_budgets')
def past_monthly_budgets():
    #only login user can access and export all user transactions as pdf file .
    if 'user_id' not in session:
        flash("Please login first","danger")
        return  redirect(url_for('auth_bp.login'))
    

    try:
        user_id=session['user_id']

        today = datetime.now()
        if today.month == 1:
          prev_month = 12
          prev_year = today.year - 1
        else:
          prev_month = today.month - 1
          prev_year = today.year
        
        #past budget reports
        past_budget = Budget.query.filter_by(user_id=user_id,month=prev_month,year=prev_year).all()


        #if no transactions
        if not past_budget:
            flash("No Past Monthly Budgets To Export","danger")
            return redirect(url_for('report_bp.report_analysis'))
        
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
        for idx, t in enumerate(past_budget, start=1):
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
        return redirect(url_for('report_bp.report_analysis'))



#download csv 
@report_bp.route('/monthly_budgets_csv')
def monthly_budgets_csv():
    #Export all user transactions as CSV file.
    if 'user_id' not in session:
        flash("Please login first","danger")
        return redirect(url_for('auth_bp.login'))
    

    user_id=session['user_id']

    try: 
      
      today = datetime.now()
      if today.month == 1:
          prev_month = 12
          prev_year = today.year - 1
      else:
          prev_month = today.month - 1
          prev_year = today.year

     #past budget reports
      past_budget = Budget.query.filter_by(user_id=user_id,month=prev_month,year=prev_year).all()

      if not past_budget:
            flash("No Past Monthly Budgets To Export", "danger")
            return redirect(url_for('report_bp.report_analysis'))
    

     # Write CSV to memory
      output=StringIO()
      writer=csv.writer(output)
      
     # Header row
      writer.writerow(["ID", "Category", "Amount", "Month","Year"])
    

     # Data rows
      for t in past_budget:
        writer.writerow([
            t.id,
            t.category,
            t.amount,
            t.month,
            t.year

        ])


     # Build response
      response=make_response(output.getvalue())
      response.headers['Content-Disposition'] = 'attachment; filename=Monthly_Budget.csv'
      response.headers['Content-Type'] = 'text/csv'
      return response


    except Exception as e:
        flash(f"Error Occurred: {str(e)}", "danger")
        return redirect(url_for('report_bp.report_analysis'))



@report_bp.route('/expense_data')
def expense_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 403

    user_id = session.get('user_id')

    # Optionally accept month/year from query params
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    query = db.session.query(Transaction.category, func.sum(Transaction.amount)).filter_by(user_id=user_id, type='expense')

    # Filter by month/year if provided
    if month and year:
        query = query.filter(
            func.extract('month', Transaction.date) == month,
            func.extract('year', Transaction.date) == year
        )

    results = query.group_by(Transaction.category).all()

    data = {
        "labels": [r[0] for r in results],
        "values": [float(r[1]) for r in results]
    }

    return jsonify(data)



#expenses_chart
@report_bp.route('/expenses_chart')
def expenses_chart():
    if 'user_id' not in session:
        flash('please login first','danger')
        return redirect(url_for('auth_bp.login'))
    return render_template('reports.html')

        


@report_bp.route('/summary_data')
def summary_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 403

    user_id = session.get('user_id')

    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    income_query = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id, type='income')
    expense_query = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id, type='expense')

    if month and year:
        income_query = income_query.filter(func.extract('month', Transaction.date) == month,
                                           func.extract('year', Transaction.date) == year)
        expense_query = expense_query.filter(func.extract('month', Transaction.date) == month,
                                             func.extract('year', Transaction.date) == year)

    Total_income = income_query.scalar() or 0
    Total_expense = expense_query.scalar() or 0
    Net_saving = max(Total_income - Total_expense, 0)

    data = {
        "labels": ['Income', 'Expense', 'Net Saving'],
        "values": [Total_income, Total_expense, Net_saving]
    }

    return jsonify(data)



