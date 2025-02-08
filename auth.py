from app import app
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from models import db, User
from sqlalchemy.exc import SQLAlchemyError
import datetime

# authentication decorators
def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner

def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('login'))
        if User.query.filter_by(userid=session['user_id']).first().role!="admin":
            flash('You are not authorized to access this page as you are not an admin')
            return redirect(url_for('ngo_dashboard'))
        return func(*args, **kwargs)
    return inner


# user login page
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if 'user_id' in session:
            return redirect(url_for('ngo_dashboard'))
        return render_template('login.html',nav="login")
    
    elif request.method == "POST":
        username=request.form.get('username')
        password=request.form.get('password')

        if username=='' or password=='':
            flash('Please fill the required fields')
            return redirect(url_for('login'))
        
        user=None
        
        if User.query.filter_by(username=username).first():
            user=User.query.filter_by(username=username).first()
            
        elif User.query.filter_by(email=username).first():
            user=User.query.filter_by(email=username).first()
        

        print(user)
        
        if not user:
            flash('Please check your username and try again.')
            return redirect(url_for('login'))
        if not user.check_password(password):
            flash('Please check your password and try again.')
            return redirect(url_for('login'))
        #after successful login   
        session['user_id']=user.userid
        if user.account_type=="NGO":
            return redirect(url_for('ngo_dashboard'))
        elif user.account_type=="Corporate":
            return redirect(url_for('corporate_dashboard'))



@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect(url_for('login'))

# new user registration
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        organization_name = request.form.get('organization_name')
        motto = request.form.get('motto')
        date_of_creation = request.form.get('date_of_creation')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        location=latitude+','+longitude
        domain = request.form.get('domain')
        account_type = request.form.get('account_type')
        logo = request.files['logo']
        logo = logo.read()

        date_of_creation = datetime.datetime.strptime(date_of_creation, '%Y-%m-%d')


        if username=='' or full_name=='' or email=='' or password=='' or confirm_password=='' or organization_name=='' or motto=='' or date_of_creation=='' or latitude=='' or longitude=='' or domain=='' or account_type=='' or logo=='':
            flash('Please fill the required fields')
            return redirect(url_for('register'))
        if password!=confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        if User.query.filter_by(organization_name=organization_name).first():
            flash('Organization name already exists')
            return redirect(url_for('register'))
        
        try:
            user=User(username=username, full_name=full_name, email=email, password=password, organization_name=organization_name, motto=motto, date_of_creation=date_of_creation, location=location, domain=domain, account_type=account_type, logo=logo)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful','success')
            return redirect(url_for('login'))
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            flash('An error occurred. Please try again.')
            return redirect(url_for('register'))
        
    
    elif request.method == "GET":
        return render_template('register.html', nav="register")
    
    else:
        return redirect(url_for('login'))
