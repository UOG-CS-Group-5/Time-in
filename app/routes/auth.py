from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required
from app.models.user import User
from app.extensions import bcrypt
from app.services.punch_service import punch_clock

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
            # if isn't admin, punch clock
            if not user.is_admin:
                punch_clock(user)
            # redirect to home
            return redirect(url_for('general.home'))
        # if missing user or password incorrect
        return 'Invalid credentials', 401
    # GET request
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))