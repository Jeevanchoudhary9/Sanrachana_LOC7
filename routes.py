import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import distinct
from app import app
from functools import wraps
from models import db, User, Profile
import random
import razorpay
from auth import auth_required, admin_required

@app.route('/')
def index():
    return render_template('landing.html',nav="landing")

@app.route('/ngo_dashboard')
def ngo_dashboard():
    return render_template('NGO_dashboard.html',nav="ngo_dashboard")



@app.route('/profile',methods=["GET","POST"])
@auth_required
def profile():
    if request.method == "GET":

        profile=(User.query.filter_by(userid=session['user_id']).first()).profileid
        return render_template('profile.html',profile=Profile.query.filter_by(profileid=profile).first(),user=User.query.filter_by(userid=session['user_id']).first(),nav="profile")
    
    elif request.method == "POST":

        user=User.query.filter_by(userid=session['user_id']).first()
        address=request.form.get('address')
        cpassword=request.form.get('cpassword')
        npassword=request.form.get('npassword')
        profile=Profile.query.filter_by(profileid=user.profileid).first()

        if address is None :
            flash('Please fill the required fields')
            return redirect(url_for('profile'))
        elif address!='' and cpassword=='' and npassword=='':
            profile.address=address
            db.session.commit()
        elif address!='' or cpassword!='' or npassword!='':
            if not user.check_password(cpassword):
                flash('Please check your password and try again.')
                return redirect(url_for('profile'))
            if npassword == cpassword:
                flash('New password cannot be same as old password')
                return redirect(url_for('profile'))
            else:
                user.password=npassword
                profile.address=address
                db.session.commit()
        flash(['Profile updated successfully','success'])
        return redirect(url_for('profile'))
