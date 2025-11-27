from app.extensions import db, bcrypt
from flask_login import UserMixin
from datetime import datetime, timedelta, timezone
import random

# Define the User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    # bcrypt salted hashed password is 60 chars long
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    salary = db.Column(db.Float, nullable=False)


# make sure a default admin user exists
def create_default_admin(default_username, default_password):
    if not User.query.filter_by(username=default_username).first():
        # already salts the password
        hashed_password = bcrypt.generate_password_hash(default_password).decode('utf-8')
        admin_user = User(username=default_username, password=hashed_password, 
                          is_admin=True, salary=0.0)
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created.")
    else:
        print("Admin user already exists.")


# make an example employee user
def create_example_employee():
    if not User.query.filter_by(username="bob").first():
        hashed_password = bcrypt.generate_password_hash("123").decode('utf-8')
        employee_user = User(username="bob", password=hashed_password, 
                             is_admin=False, salary=9)
        db.session.add(employee_user)
        db.session.commit()

        # add some example punches
        from app.services.punch_service import punch_clock
        last_week = datetime.now(timezone.utc) - timedelta(days=7)
        last_week = last_week.replace(hour=0, minute=0)
        # week worth of punches
        for i in range(7):
            # -10 for chst
            in_time = last_week + timedelta(days=i, hours=9-10, minutes=random.randint(0,60))
            out_time = last_week + timedelta(days=i, hours=17-10, minutes=random.randint(0,60))
            punch_clock(employee_user, in_time)
            punch_clock(employee_user, out_time)
        print("Example employee user created.")
    else:
        print("Example employee user already exists.")