from app import app
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from models import db, User, Profile
from sqlalchemy.exc import SQLAlchemyError

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
            return redirect(url_for('user_dashboard'))
        return func(*args, **kwargs)
    return inner


# user login page
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if 'user_id' in session:
            return redirect(url_for('user_dashboard'))
        return render_template('login.html',nav="login")
    
    elif request.method == "POST":
        username=request.form.get('username')
        password=request.form.get('password')

        if username=='' or password=='':
            flash('Please fill the required fields')
            return redirect(url_for('login'))
        
        user=User.query.filter_by(uname=username).first()
        if not user:
            flash('Please check your username and try again.')
            return redirect(url_for('login'))
        if not user.check_password(password):
            flash('Please check your password and try again.')
            return redirect(url_for('login'))
        #after successful login   
        session['user_id']=user.userid
        return redirect(url_for('user_dashboard'))



@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect(url_for('login'))

# new user registration
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')

        if not username or not password or not email:
            flash('Please fill the required fields')
        elif len(phone) != 10:
            flash('Please check your phone number')
        elif User.query.filter_by(uname=username).first():
            flash('Username already exists')
        else:
            try:
                profile = Profile(firstname=firstname, lastname=lastname, email=email, phone=phone, address=address)
                db.session.add(profile)
                db.session.commit()

                pid = profile.profileid
                new_user = User(uname=username, password=password, profileid=pid, role="user")
                db.session.add(new_user)
                db.session.commit()
                
                flash(['You have successfully registered', 'success'])
                return redirect(url_for('login'))
            except SQLAlchemyError:
                db.session.rollback()
                flash('Registration failed. Please try again.', 'error')
                
        return redirect(url_for('register'))
    
    elif request.method == "GET":
        return render_template('login_register/register.html', nav="register")
    
    else:
        return redirect(url_for('login'))
