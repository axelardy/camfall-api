from flask import Blueprint, render_template, redirect, url_for, request,flash,make_response
from .login_script.db_engine import *

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = user_exist(username)

    if not user or not login_db(username,hash_password(password)):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    resp = make_response(redirect(url_for('Main')))
    if remember:
        resp.set_cookie('username', username)
    return resp


@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    password = request.form.get('password')
    repassword = request.form.get('re-pass')

    if user_exist(username): # if user already exists
        flash('0')
        return redirect(url_for('auth.signup'))
    if password != repassword:
        flash('1')
        return redirect(url_for('auth.signup'))

    print(username,password)
    signup_db(username,hash_password(password))
    return redirect(url_for('auth.login'))



@auth.route('/logout')
def logout():
    return 'Logout'