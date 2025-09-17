from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, RadioField,TimeField,SelectField,FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length,NumberRange


#Form for new user registration
class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

#Form for login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

#form for rest request password reset link (via email)
class ResetRequestForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email()])
    submit=SubmitField('Send Rest Link')

#form for reset password after email verification
class ResetPasswordForm(FlaskForm):
    password=PasswordField('Password',validators=[DataRequired(),Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit=SubmitField('Update password')

#form for add/edit income and expenses
class TransactionForm(FlaskForm):
    amount = StringField('Amount', validators=[DataRequired()])
    category = SelectField('Category', choices=[('food', 'Food'),('transport', 'Transport'),('shopping', 'Shopping'),('rent', 'Rent'),('other', 'Other'),('salary','Salary')],validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    type = RadioField('Transaction Type',choices=[('expense', 'Expense'), ('income', 'Income')],default='expense',validators=[DataRequired()])
    submit = SubmitField('Submit')


#form for set monthly budget for each category
class BudgetForm(FlaskForm):
    category = SelectField('Category', choices=[('food', 'Food'),('transport', 'Transport'),('shopping', 'Shopping'),('rent', 'Rent'),('other', 'Other')],validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Set Budget')




#form for set payable/receivable reminders
class RemindersForm(FlaskForm):
    reminder_type=SelectField('Reminder_type',choices=[('payable','Payable'),('recivedable','Recivedable')],validators=[DataRequired()])
    category=SelectField('Category', choices=[('food', 'Food'),('internet', 'Internet'),('shopping', 'Shopping'),('rent', 'Rent'),('electricity','Electricity'),('salary','Salary'),('other', 'Other')],validators=[DataRequired()])
    due_date=DateField('Due Date',format='%Y-%m-%d',validators=[DataRequired()])
    time=TimeField('Time',format='%H:%M',validators=[DataRequired()])
    amount = StringField('Amount', validators=[DataRequired()])
    submit=SubmitField('Set Reminders')


#form for update profile info
class UpdateprofileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')

#form for change account password
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Change Password")
