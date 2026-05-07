# memory.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

memory = Blueprint('memory', __name__)
@memory.route('/dashboard')
@login_required
def dashboard():
    return render_template('memory/dashboard.html',couple=current_user)
