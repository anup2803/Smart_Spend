from flask import Blueprint, render_template, redirect, url_for, flash, session,current_app
from app.models import User
from app.forms import Registerform, LoginForm,ResetPasswordForm,ResetRequestForm
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask_mail import Message
from app import mail
from itsdangerous import URLSafeTimedSerializer,BadSignature,SignatureExpired

# Create  Blueprint for authentication routes
auth_bp = Blueprint('auth_bp', __name__)



#Index route
@auth_bp.route('/')
def index():
    #Redirect logged-in users to the dashboard 
    if 'user_id' in session:
        return redirect(url_for('dashboard_bp.dashboard'))
    #if not then return to index
    return render_template('index.html')

#terms
@auth_bp.route("/terms")
def terms():
    return render_template("terms.html")

#privacy
@auth_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")

#compliance
@auth_bp.route("/compliance")
def compliance():
    return render_template("compliance.html")

#read_more
@auth_bp.route("/read_more")
def read_more():
    return render_template('readmore.html')



#email verifications helper
def generate_email_token(user_data, expires_sec=3600):
    #generate a secure token for email verification
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(user_data)



def verify_email_token(token, max_age=3600):
    
    #verify the email verification token.
    #  returns user data if valid  or returns None if token is invalid/expired
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        user_data = s.loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    return user_data



#register route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect logged-in users to the dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard_bp.dashboard'))

    form = Registerform()
    if form.validate_on_submit():
        try:
            # User details for registration
            first_name = form.first_name.data
            last_name = form.last_name.data
            username = form.username.data
            email = form.email.data
            # Generated hashed password
            password = generate_password_hash(form.password.data)

            # Checking if the username or email is already registered
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return redirect(url_for('auth_bp.register'))
            if User.query.filter_by(email=email).first():
                flash('Email already exists', 'danger')
                return redirect(url_for('auth_bp.register'))

            # Prepare data for token
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "email": email,
                "password": password
            }

            # Generating email verification token
            token = generate_email_token(user_data)
            verify_url = url_for('auth_bp.verify_email', token=token, _external=True)

            # Send verification email
            # CHANGE: Flask-Mail 'sender' must be a string, not a list
            # Old: sender=["SmartSpend", "Kumalanup555@gmail.com"]
            # Fixed:
            msg = Message(
                subject="Verify Your Account",
                sender="SmartSpend <Kumalanup555@gmail.com>", 
                recipients=[email]
            )
            msg.body = f"Welcome {first_name}, Please verify your account {verify_url}"
            msg.html = render_template('verify_email.html', user=user_data, verify_url=verify_url)
            mail.send(msg)

            flash('Registration successful! Check your email to verify your account.', 'success')
            return redirect(url_for('auth_bp.login'))

        except Exception as e:
            # Rollback on error
            db.session.rollback()
            flash(f'Error: {e}', 'danger')

    return render_template('register.html', form=form)





#verify email route
@auth_bp.route('/verify_email/<token>')
def verify_email(token):
    user_data=verify_email_token(token)
    if not user_data:
        flash('Verification link is invalid or expired.', 'danger')
        return redirect(url_for('auth_bp.login'))
    

     # check again to avoid duplicates
    if User.query.filter_by(email=user_data['email']).first():
        flash('Your account is already verified. Please log in.', 'info')
        return redirect(url_for('auth_bp.login'))
    
  # create user db
    new_user = User(
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password'],
        is_verified=True
    )
    db.session.add(new_user)
    db.session.commit()
    

    flash('Your email has been verified! You can now log in.', 'success')
    return redirect(url_for('auth_bp.login'))




#login route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard_bp.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            username = form.username.data
            password = form.password.data

            #Look the user by username
            user = User.query.filter_by(username=username).first()

            # Check password hash
            if user and check_password_hash(user.password, password):
                if not user.is_verified:
                    flash('Please verify your email before logging in.', 'danger')
                    return redirect(url_for('auth_bp.login'))

                # Save login state in session
                session['user_id'] = user.id
                session['username'] = user.username
                flash(f"Welcome back, {user.first_name}!", 'success')
                return redirect(url_for('dashboard_bp.dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
    return render_template('login.html', form=form)





#password reset helper
def generate_reset_token(user_id,expires_sec=3600):
    #generate a token for password reset.
    s=URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(user_id)


def verify_reset_token(token,max_age=3600):
    #verify a password reset token and return user_id if valid.
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        user_id=s.loads(token,max_age=max_age)
    except (BadSignature,SignatureExpired):
      return None
    return user_id









#reset password request to the user route
@auth_bp.route('/reset_password_request',methods=['GET','POST'])
def reset_password_request():
    form=ResetRequestForm()
    if form.validate_on_submit():
        email=form.email.data
        user=User.query.filter_by(email=email).first()
        if user:
            # Generate reset token
            token=generate_reset_token(user.id)
            reset_url = url_for('auth_bp.reset_password', token=token, _external=True)

            # Send reset email
            msg = Message(subject=f"Password Reset Request",sender=["SmartSpend", "Kumalanup555@gmail.com"], recipients=[user.email])
            msg.body = f"Click here to reset your password: {reset_url}"
            mail.send(msg)

            flash('Reset email sent! Check your inbox.', 'success')
            return redirect(url_for('auth_bp.login'))
        else:
             flash('Email not found!', 'danger')

    return render_template('Reset_request.html',form=form)
   


#Reset password route
@auth_bp.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    user_id=verify_reset_token(token)
    if not user_id:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('auth_bp.reset_password_request'))
    

    user=User.query.get(user_id)
    form=ResetPasswordForm()
    if form.validate_on_submit():

        # Update password
        new_password=generate_password_hash(form.password.data)
        user.password=new_password
        db.session.commit()
        flash('Password updated! You can now log in.', 'success')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('reset_password.html', form=form)



#logout route
@auth_bp.route('/logout')
def logout():
    # Clear all session data
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth_bp.index'))
