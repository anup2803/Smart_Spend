from flask import render_template,redirect,url_for,session,flash,Blueprint
from app import db
from app.models import User
from werkzeug.security import generate_password_hash,check_password_hash
from app.forms import ChangePasswordForm,UpdateprofileForm


settings_bp=Blueprint('settings_bp',__name__)

#setting route
@settings_bp.route('/settings',methods=['GET','POST'])
def settings():
    if 'user_id' not in session:
        flash(f'Please Login first','danger')
        return redirect(url_for('auth_bp.login'))
    return render_template('setting.html')




#edit information for settings
@settings_bp.route('/edit_informations',methods=['GET','POST'])
def edit_informations():
    if 'user_id' not in session:
        flash(f'Please Login first','danger')
        return redirect(url_for('auth_bp.login'))
    

    user = User.query.get(session['user_id'])
    form=UpdateprofileForm(obj=user)


    if form.validate_on_submit():
        try:
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data

            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('settings_bp.edit_informations'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {e}", "danger")


    return render_template('edit_information.html', form=form, user=user)



    

#Change password informations
@settings_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
      flash("Please login first", "danger")
      return redirect(url_for('auth_bp.login'))
    

    user=User.query.get(session['user_id'])
    form=ChangePasswordForm()


    if form.validate_on_submit():
        if not check_password_hash(user.password,form.old_password.data):
            flash("Old password is incorrect", "danger")

        else:
            user.password=generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Password changed successfully!", "success")
            return redirect(url_for('settings_bp.change_password'))
        
    return render_template("change_password.html",form=form)