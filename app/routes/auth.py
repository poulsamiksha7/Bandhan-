from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import CoupleProfile

auth=Blueprint('auth',__name__)

@auth.route('/')
def home():
    return render_template('home.html')

@auth.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        #Get data from form
        bride_name=request.form.get('bride_name')
        groom_name=request.form.get('groom_name')
        email=request.form.get('email')
        password=request.form.get('password')
        wedding_date=request.form.get('wedding_date')
        their_story=request.form.get('their_story')
        language=request.form.get('language')
        city=request.form.get('city')

        #check if email already exists

        exisiting=CoupleProfile.query.filter_by(email=email).first()
        if exisiting:
            flash('This email is already registered.','error')
            return redirect(url_for('auth.register'))
        #hash the password

        hashed_password=generate_password_hash(password)

        #create couple object
        couple=CoupleProfile(
            bride_name=bride_name,
            groom_name=groom_name,
            email=email,
            password=hashed_password,
            their_story=their_story,
            language=language,
            city=city
        )

        #handle wedding date
        if wedding_date:
            from datetime import datetime
            couple.wedding_date=datetime.strptime(wedding_date,'%Y-%m-%d')

        #Save database

        try:
            db.session.add(couple)
            db.session.commit()
            flash('Your love story begins. Please login.🌙','success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            print("DATABASE ERROR:", str(e))
            flash('Something went wrong. Please try again.', 'error')
            return redirect(url_for('auth.register'))
    
    #GET request= just to show form
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET','POST'])
def login():
    # if already logged in send to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('memory.dashboard'))
    
    if request.method=='POST':
        email= request.form.get('email')
        password=request.form.get('password')
        #find couple by email
        couple=CoupleProfile.query.filter_by(email=email).first()
        #Wrong email
        if not couple:
            flash('No account found with this email.','error')
            return redirect(url_for('auth.login'))
        
        # wrong password
        if not check_password_hash(couple.password,password):
            flash('Incorrect passoword. Try again','error')
            return redirect(url_for('auth.login'))
        
        #correct- log them in

        login_user(couple)
        flash(f'Welcome back, {couple.bride_name} & {couple.groom_name} 🌙','success')
        return redirect(url_for('memory.dashboard'))
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out','success')
    return redirect(url_for('auth.login'))