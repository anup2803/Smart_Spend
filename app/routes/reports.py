from flask import jsonify,flash,Blueprint,render_template,redirect,url_for,session,make_response
from sqlalchemy import func,desc
from app import db
from app.models import Transaction
from io import BytesIO,StringIO
import csv
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter



report_bp=Blueprint('report_bp',__name__)





#report route
@report_bp.route('/report_analysis')
def report_analysis():
    if 'user_id' not in session:
        flash("Please Login first","danger")
        return redirect(url_for('auth_bp.login'))
    

    try:
      user_id=session.get('user_id')

    #total income 
      Total_Income = db.session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id, type='income').scalar()




   #total expense
      Total_expense=db.session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id,type='expense').scalar()


    #Net income 
      Total_Income = Total_Income or 0
      Total_expense = Total_expense or 0
      Net_income = Total_Income - Total_expense


      
   # Recent transactions (last 5)
      recent_trans = Transaction.query.filter_by(user_id=user_id).order_by(desc(Transaction.date)).limit(5).all()




      return render_template('reports.html',Total_Income=Total_Income,Total_expense=Total_expense,Net_income=Net_income,recent_trans=recent_trans)

    except Exception as e:
          flash(f"Error generating report: {e}", "danger")
          return redirect(url_for('dashboard_bp.dashboard'))




#export pdf of transactions
@report_bp.route('/export_pdf')
def export_pdf():
    if 'user_id' not in session:
        flash("Please login first","danger")
        return  redirect(url_for('auth_bp.login'))
    

    try:
        user_id=session['user_id']
        
        #get all user transactions by user_id 
        transactions=Transaction.query.filter_by(user_id=user_id).all()


        #if no transactions
        if not transactions:
            flash("No transactions found to export","danger")
            return redirect(url_for('dashboard_bp.dashboard'))
        
        # Prepare PDF in memory
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer,pagesize=letter)


        #table header+data
        data=[["ID", "Type", "Category", "Amount", "Date"]]
        for t in transactions:
            data.append([
                t.id,
                t.type,
                t.category,
                t.amount,
                t.date.strftime('%Y-%m-%d')

            ])

        table=Table(data)
        table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),  # thinner grid
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), # bold header
         ]))



        doc.build([table])


        pdf=buffer.getvalue()
        buffer.close()



        response= make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=transactions.pdf'


        return response
    

    except Exception as e:
        flash(f"Error Occurred: {str(e)}", "danger")
        return redirect(url_for('dashboard_bp.dashboard'))



#download csv 
@report_bp.route('/download_csv')
def download_csv():
    if 'user_id' not in session:
        flash("Please login first","danger")
        return redirect(url_for('auth_bp.login'))
    

    user_id=session['user_id']

    try: 
     transactions=Transaction.query.filter_by(user_id=user_id).all()

     if not transactions:
            flash("No transactions to export", "danger")
            return redirect(url_for('dashboard_bp.dashboard'))
    

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
        return redirect(url_for('dashboard_bp.dashboard'))
    


#create the expense data and convert into chart.js

@report_bp.route('/expense_data')
def expense_data():
    if 'user_id' not in session:
        return jsonify({'error','Pleases Login First'}),403
        
    user_id=session.get('user_id')

    results=db.session.query(Transaction.category,func.sum(Transaction.amount)).filter_by(user_id=user_id,type='expense').group_by(Transaction.category).all()


    #convert json format to chart.js
    data={
        "labels":[r[0] for r in results],
        "values":[float(r[1]) for r in results]
    }

    return  jsonify(data)



#expenses_chart
@report_bp.route('/expenses_chart')
def expenses_chart():
    if 'user_id' not in session:
        flash('please login first','danger')
        return redirect(url_for('auth_bp.login'))
    return render_template('reports.html')

        



#summary_data for the bar graph
@report_bp.route('/summary_data')
def summary_data():
    if 'user_id' not in session:
        return jsonify({'error','Please Login First'})
    
    user_id=session.get('user_id')

    #total income query from the transactions
    Total_income=db.session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id,type='income').scalar() or 0


    #total expense query from the transactions
    Total_expense=db.session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id,type='expense').scalar() or 0

    #net saving of the transactions 
    Net_saving=max(Total_income - Total_expense, 0)

    data={
        "labels":['Income','Expense','Net Saving'],
        "values":[Total_income,Total_expense,Net_saving]
    }

    return jsonify(data)


