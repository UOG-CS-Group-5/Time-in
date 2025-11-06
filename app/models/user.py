from app.extensions import db, bcrypt
from flask_login import UserMixin

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
        hashed_password = bcrypt.generate_password_hash(default_password).decode('utf-8')
        admin_user = User(username=default_username, password=hashed_password, 
                          is_admin=True, salary=0.0)
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created.")
    else:
        print("Admin user already exists.")