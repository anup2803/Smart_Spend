from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app
from app.models import User
from app.forms import RegisterForm, LoginForm, ResetPasswordForm, ResetRequestForm
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

auth_bp = Blueprint('auth_bp', __name__)

# --- Index route ---
@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard_bp.dashboard'))
    return render_template('index.html')


# --- Static pages ---
@auth_bp.route("/terms")
def terms(): return render_template("terms.html")

@auth_bp.route("/privacy")
def privacy(): return render_template("privacy.html")

@auth_bp.route("/compliance")
def compliance(): return render_template("compliance.html")

@auth_bp.route("/read_more")
def read_more(): return render_template('readmore.html')


# --- Email token helpers ---
def generate_email_token(user_data):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(user_data)

def verify_email_token(token, max_age=600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return s.loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None


# --- Register route ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard_bp.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        phonenumber=form.phonenumber.data
        password = generate_password_hash(form.password.data)

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth_bp.register'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('auth_bp.register'))

        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "email": email,
            "phonenumber":phonenumber,
            "password": password
        }

        token = generate_email_token(user_data)
        verify_url = url_for('auth_bp.verify_email', token=token, _external=True)

        # Send verification email
        msg = Message(
                subject=" Account Verification",
                sender="SmartSpend <smartspend94@gmail.com>",
                recipients=[email]
            )
        msg.body = f"Click here to verify your account: {verify_url}"
        

        mail.send(msg)

        flash('Registration successful! Check your email to verify your account.', 'success')
        return redirect(url_for('auth_bp.login'))

    return render_template('register.html', form=form)


# --- Verify email ---
@auth_bp.route('/verify_email/<token>')
def verify_email(token):
    user_data = verify_email_token(token)
    if not user_data:
        flash('Verification link is invalid or expired.', 'danger')
        return redirect(url_for('auth_bp.login'))

    # Check if user already exists
    existing_user = User.query.filter_by(email=user_data['email']).first()
    if existing_user:
        if existing_user.is_verified:
            flash('Your account is already verified. Please log in.', 'info')
        else:
            existing_user.is_verified = True
            db.session.commit()
            flash('Your email has been verified! You can now log in.', 'success')
        return redirect(url_for('auth_bp.login'))

    # Create new verified user
    new_user = User(
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        username=user_data['username'],
        email=user_data['email'],
        phonenumber=user_data['phonenumber'],
        password=user_data['password'],
        is_verified=True
    )
    db.session.add(new_user)
    db.session.commit()

    flash('Your email has been verified! You can now log in.', 'success')
    return redirect(url_for('auth_bp.login'))



# --- Login route ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard_bp.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if not user.is_verified:
                flash('Please verify your email before logging in.', 'danger')
                return redirect(url_for('auth_bp.login'))

            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Welcome back, {user.first_name}!", 'success')
            return redirect(url_for('dashboard_bp.dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)


# --- Password reset helpers ---
def generate_reset_token(user_id):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(user_id)

def verify_reset_token(token, max_age=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return s.loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None


# --- Reset password request ---
@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.id)
            reset_url = url_for('auth_bp.reset_password', token=token, _external=True)

            msg = Message(
                subject="Password Reset Request",
                sender="SmartSpend <smartspend94@gmail.com>",
                recipients=[user.email]
            )
            msg.body = f"Click here to reset your password: {reset_url}"
            mail.send(msg)

            flash('Reset email sent! Check your inbox.', 'success')
            return redirect(url_for('auth_bp.login'))
        else:
            flash('Email not found!', 'danger')

    return render_template('reset_request.html', form=form)


# --- Reset password ---
@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user_id = verify_reset_token(token)
    if not user_id:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('auth_bp.reset_password_request'))

    user = User.query.get(user_id)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Password updated! You can now log in.', 'success')
        return redirect(url_for('auth_bp.login'))

    return render_template('reset_password.html', form=form)


# --- Logout ---
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth_bp.index'))
