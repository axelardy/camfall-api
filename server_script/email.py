from flask import Blueprint, render_template, redirect, url_for, request,flash,make_response
from .login_script.db_engine import *

email = Blueprint('email', __name__)

@email.route('/email', methods=['POST'])
def email_post():
    username = request.form.get('username')
    email = request.form.get('email')
    email_logic(username,email)
    flash('Email updated')
    return redirect(url_for('profile'))

