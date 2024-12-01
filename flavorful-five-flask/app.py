from flask import Flask, render_template, url_for, redirect, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import pyotp
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os


app = Flask(__name__)

#loads env variables
load_dotenv()
#set up app and email sending parameters
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  
mail = Mail(app)
key = os.getenv('key') #key for otp
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


#FOR RUNNING LOCALLY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#FOR USE WHEN HOSTING
# app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database.db')}"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    '''
    used to return user, based on the userID
    '''
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    '''
    structure of user in database for sql-lite
    id (int): Primary key for the user.
        username (str): The username of the user.
        password (str): The hashed password of the user.
        email (str): The email address of the user. (added using migration)
    '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)  


class RegisterForm(FlaskForm):
    '''
    utilize flasks built in forms for authentication
     username (StringField): Field for the username.
    password (PasswordField): Field for the password.
    email (EmailField): Field for the email address.
    submit (SubmitField): Submit button for the form.
    '''
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    
    email = EmailField(validators=[
        InputRequired(), Length(min=6, max=120)], render_kw={"placeholder": "Email"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        '''
        verifies username is unique, or else sends a message
        '''
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')
        
    def validate_email(self, email):
        '''
        verifies email is unique, or else sends a message
        '''
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                'That email already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    '''
    A login form for existing users.

        username (StringField): Field for the username.
        password (PasswordField): Field for the password.
        submit (SubmitField): Submit button for the form.
    '''
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


@app.route('/')
def home():
    '''
    syntax for defining a route, in this case home
    '''
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    route for login, compares hashed password to database
    '''
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                # return redirect(url_for('home'))
                return redirect(url_for('send_2fa_code'))  # Redirect to send the 2FA code
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    '''
    logout route clears logged in and 2fa status
    '''
    session.pop('2fa_verified', None)
    logout_user()
    return redirect(url_for('home'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    route to create new user and add to db
    '''
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/recipes')
def recipes():
    return render_template('recipes.html') 

@app.route('/saved')
def saved():
    username = current_user.username if current_user.is_authenticated else "Guest"
    return render_template('saved.html',username=username)  

@app.route('/myrecipes')
def my_recipes():
    username = current_user.username if current_user.is_authenticated else "Guest"
    return render_template('myrecipes.html',username=username)  

@app.route('/contactus')
def contact_us():
    return render_template('contactus.html')  

@app.route('/recipesfolder')
def recipes_folder():
    return render_template('recipesfolder.html')  



@app.route('/verify-2fa', methods=['GET', 'POST'])
@login_required
def verify_2fa():
    '''
    check to verify 2fa code
    '''
    if request.method == 'POST':
        entered_code = request.form.get('2fa_code')
        if str(session.get('2fa_code')) == entered_code:
            # 2FA successful
            session.pop('2fa_code', None)  # Clear the code from the session
            session['2fa_verified'] = True #add session for 2FA
            return redirect(url_for('home'))
        else:
            flash('Invalid 2FA code. Please try again.', 'danger')
    
    return render_template('verify_2fa.html')



@app.route('/send-2fa-code', methods=['GET', 'POST'])
@login_required
def send_2fa_code():
    # Generate time-sensitive 2FA code
    totp = pyotp.TOTP(key, interval=90)
    code = pyotp.TOTP(key).now()
    session['2fa_code'] = code

    # Send the 2FA code via email
    msg = Message('Your 2FA Code', sender=app.config['MAIL_USERNAME'], recipients=[current_user.email])
    msg.body = f'Your 2FA code is: {code}'
    msg.html = f"""
    <html>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f9f9f9;">
        <table role="presentation" cellspacing="0" cellpadding="0" style="width: 100%; background-color: #f9f9f9; padding: 20px;">
            <tr>
                <td align="center">
                    <table role="presentation" cellspacing="0" cellpadding="0" style="max-width: 600px; width: 100%; background-color: #f5daf2; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <tr>
                            <td style="text-align: center;">
                                <h2 style="color: #333; font-size: 24px; margin: 0;">Your 2FA Code</h2>
                            </td>
                        </tr>
                        <tr>
                            <td style="font-size: 16px; color: #555; line-height: 1.5; margin: 15px 0;">
                                Hi <strong>{current_user.username}<strong>,
                            </td>
                        </tr>
                        <tr>
                            <td style="font-size: 16px; color: #555; line-height: 1.5; margin: 15px 0;">
                                Here is your 2FA code:
                            </td>
                        </tr>
                        <tr>
                            <td style="text-align: center; margin: 20px 0;">
                                <span style="font-size: 24px; color: #333; font-weight: bold; background-color: #f2f2f2; padding: 10px 20px; border-radius: 5px; display: inline-block;">{code}</span>
                            </td>
                        </tr>
                        <tr>
                            <td style="font-size: 16px; color: #555; line-height: 1.5; margin: 15px 0;">
                                This code is valid for <strong>90 seconds</strong>. Please do not share this code with anyone.
                            </td>
                        </tr>
                        <tr>
                            <td style="font-size: 16px; color: #555; line-height: 1.5; margin: 15px 0;">
                                If you did not request this code, please contact our support team immediately.
                            </td>
                        </tr>
                        <tr>
                            <td style="font-size: 14px; color: #aaa; text-align: center; margin-top: 20px;">
                                &copy; 2024 FlavorfulFive. All rights reserved.
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    mail.send(msg)

    flash('A 2FA code has been sent to your email.', 'info')
    return redirect(url_for('verify_2fa'))



if __name__ == "__main__":
    with app.app_context():
        db.create_all()


    #FOR RUNNING LOCALLY   
    app.run(debug=True, port=8000)

    #FOR USE WHEN HOSTING
    #app.run()
