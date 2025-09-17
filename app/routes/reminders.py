from flask import render_template,session,url_for,redirect,flash,Blueprint,current_app,make_response
from app.models import Reminder
from app.forms import RemindersForm
from app import db,mail,scheduler
from datetime import datetime
from flask_mail import Message
from app.models import User
from apscheduler.jobstores.base import JobLookupError
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter


#blueprint for the reminders
reminders_bp=Blueprint('reminders_bp',__name__)




#reminders routes
@reminders_bp.route('/reminders',methods=['GET','POST'])
def reminders():
 #Only accessible if logged in.
 if 'user_id' not in session:
  flash('Please login first','danger')
  return redirect(url_for('auth_bp.login'))
 

 user_id=session.get('user_id')
 user = User.query.get(user_id)

 if not user:
    flash("User not found!", "danger")
    return redirect(url_for('auth_bp.login'))

 form = RemindersForm()
 
 if form.validate_on_submit():
    try:  
      # Collect reminder form data
      reminder_type=form.reminder_type.data
      category=form.category.data
      due_date=form.due_date.data
      time=form.time.data
      amount=form.amount.data
      
      
    # Fetch only future reminders
      now = datetime.now()
      reminder_datetime = datetime.combine(due_date, time)
      

      # Ensure the reminder is in the future
      if reminder_datetime <= now:
        flash("Cannot set a reminder in the past!", "danger")
        return redirect(url_for('reminders_bp.reminders'))
      
      
      # Create and save new reminder
      new_reminder=Reminder(reminder_type=reminder_type,category=category,due_date=due_date,time=time,user_id=user_id,amount=amount)
      


      db.session.add(new_reminder)
      db.session.commit()


       # Inside edit_reminder after commit:
      job_id = f"reminder_{new_reminder.id}"
      try:
        scheduler.remove_job(job_id)
      except JobLookupError:
         pass



      # schedule reminder job
      reminder_datetime = datetime.combine(new_reminder.due_date, new_reminder.time)
      scheduler.add_job(
        id=job_id,
        func=send_reminder_email,
        trigger='date',
        run_date=reminder_datetime,
        args=[current_app._get_current_object(),new_reminder.id]
      )
      
      flash(f"Reminder set successfully! Email sent to {user.email} at {reminder_datetime}.", "success")
      return redirect(url_for('reminders_bp.reminders'))
    

    except Exception as e:
        db.session.rollback()
        flash(f'Error Occur {e}','danger')
        return redirect(url_for('dashboard_bp.dashboard'))
    

 #fetch all the reminders
 reminders = Reminder.query.filter_by(user_id=user_id).all()
 user = User.query.filter_by(id=user_id).first()

 return render_template("reminders.html", reminders=reminders,form=form,user=user)






#functions email sender
#Helper function (called by APScheduler) to send reminder emails.


def send_reminder_email(app,reminder_id):
  with app.app_context():
   reminder = Reminder.query.get(reminder_id)
   if not reminder:
        return
  
   user = User.query.get(reminder.user_id)
   if not user:
        return
  

   msg = Message(
        subject=f"Reminder: {reminder.reminder_type}",
        sender="SmartSpend <smartspend94@gmail.com>",
        recipients=[user.email],
        body=f"""
        Hi {user.first_name},

        This is a reminder for your {reminder.reminder_type}:
        Category: {reminder.category}
        Amount: {reminder.amount}
        Due Date & Time: {reminder.due_date} {reminder.time}

        Thank you.
        """
    )
   mail.send(msg)




# Edit reminders
@reminders_bp.route('/edit_reminders/<int:id>', methods=['GET', 'POST'])
def edit_reminder(id):
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('auth_bp.login'))

    reminder = Reminder.query.filter_by(id=id, user_id=session['user_id']).first()
    if not reminder:
        flash('Reminder not found', 'danger')
        return redirect(url_for('reminders_bp.reminders'))  

    form = RemindersForm(obj=reminder)

    if form.validate_on_submit():
        try:
            reminder.reminder_type = form.reminder_type.data
            reminder.category = form.category.data
            reminder.due_date = form.due_date.data
            reminder.time = form.time.data
            reminder.amount = form.amount.data
            db.session.commit()

            flash(f'{reminder.reminder_type.capitalize()} updated successfully!', 'success')
            return redirect(url_for('reminders_bp.reminders'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating reminder: {e}', 'danger')

    return render_template('edit_reminders.html', form=form, reminder=reminder)






# Delete reminders
@reminders_bp.route('/delete_reminders/<int:id>', methods=['POST'])
def delete_reminder(id):
    if 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('auth_bp.login'))

    try:
        reminder = Reminder.query.filter_by(id=id, user_id=session['user_id']).first()
        if not reminder:
            flash('Reminder not found', 'danger')
            return redirect(url_for('reminders_bp.reminders'))

        db.session.delete(reminder)
        db.session.commit()
        flash(f'{reminder.reminder_type.capitalize()} deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting reminder: {e}', 'danger')
        
    return redirect(url_for('reminders_bp.reminders'))




# export pdf of reminders
@reminders_bp.route('/export_reminder_pdf')
def export_pdf():
    # Only logged-in users can export reminders
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('auth_bp.login'))

    try:
        user_id = session['user_id']

        # Get all reminders for this user
        reminders = Reminder.query.filter_by(user_id=user_id).all()

        # If no reminders
        if not reminders:
            flash("No reminders found to export", "danger")
            return redirect(url_for('reminders_bp.reminders'))

        # Prepare PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Table header + data
        data = [["ID", "Type", "Category", "Due Date", "Amount", "Time"]]
        for r in reminders:
            data.append([
                r.id,
                r.reminder_type,
                r.category,
                r.due_date.strftime('%Y-%m-%d') if r.due_date else "",
                r.amount,
                r.time.strftime('%H:%M') if r.time else ""
            ])

        # Table style
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ]))

        # Build PDF
        doc.build([table])

        # Send as response
        pdf = buffer.getvalue()
        buffer.close()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=reminders.pdf'
        return response

    except Exception as e:
        flash(f"Error Occurred: {str(e)}", "danger")
        return redirect(url_for('reminders_bp.reminders'))



#to clear routes
@reminders_bp.route('/clear_all', methods=['POST'])
def clear_all():
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('auth_bp.login'))
    
    user_id = session['user_id']
    Reminder.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    flash("All reminders cleared!", "success")
    return redirect(url_for('reminders_bp.reminders'))
