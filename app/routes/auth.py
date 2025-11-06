from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required
from app.models.user import User
from app.extensions import bcrypt

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # user exists and password matches
        if user and bcrypt.check_password_hash(user.password, raw_password):
            login_user(user)
            return redirect(url_for('general.home'))
        return 'Invalid credentials', 401
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))