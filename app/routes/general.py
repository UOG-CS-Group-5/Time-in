from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import admin_required

bp = Blueprint('general', __name__)

@bp.route('/')
@login_required
def home():
    if current_user.is_admin:
        return redirect(url_for('general.admin_dashboard'))
    else:
        return redirect(url_for('general.employee_dashboard'))
    
@bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin.html')

@bp.route('/dashboard')
@login_required
def employee_dashboard():
    return render_template('employee.html')