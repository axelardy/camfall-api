from flask import Blueprint, render_template, redirect, url_for, request,flash,make_response
from .login_script.db_engine import *

contact = Blueprint('contact', __name__)

@contact.route('/contact', methods=['POST'])
def contact_post():
    username = request.form.get('username')
    email = request.form.get('email')
    lineid = request.form.get('lineid')
    line_notif = request.form.get('line_notif')
    line_notif = True if line_notif == 'on' else False
    contact_logic(username,email,lineid,line_notif)
    flash('Email/LineID  updated')
    return redirect(url_for('profile'))

