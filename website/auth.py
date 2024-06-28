# import modules to handle user authentication
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

# logout
@auth.route('/logout')
@login_required # makes it so that you have to be logged in first
def logout():
    logout_user()
    return redirect(url_for('auth.login')) # go back to login

#login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email') # get the email
        password = request.form.get('password') # get the password

        # check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, str(password)):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.add_expense')) # go to the home page
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    # return back to login if any of the above fail
    return render_template("auth/login.html", user=current_user)

# sign up
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # get info from the html form
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        monthly = int(request.form['monthly'])
        yearly = int(request.form['yearly'])

        # error checks
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        elif len(str(email)) < 5:
            flash('Invalid email', category='error')
        elif len(str(first_name)) <= 1:
            flash('Invalid first name', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        elif len(str(password1)) < 7:
            flash('Password must be at least 7 characters', category='error')
        elif monthly < 0:
            flash('Invalid monthly salary', category='error')
        elif yearly < 0:
            flash('Invalid yearly salary', category='error')
        else:
            # everything is good so add user to database
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha512'), monthly=monthly, yearly=yearly)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True) # log the user in automatically after making account
            flash('Account created', category='success')
            return redirect(url_for('views.add_expense')) # go to home

    # something went wrong so go back to sign up
    return render_template("auth/sign_up.html", user=current_user)
