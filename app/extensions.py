from functools import wraps
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    # delay import till after db is initialized
    from app.models.user import User
    return User.query.get(int(user_id))

def admin_required(view_function):
    # use wraps to preserve its original name so that 
    # flask can route properly
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)  # Return a 403 Forbidden error
        return view_function(*args, **kwargs)
    return wrapper