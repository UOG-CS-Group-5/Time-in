from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db, bcrypt
from app.models.user import User
from app.extensions import admin_required

# Blueprint for admin routes prefixed with /admin
bp = Blueprint('admin', __name__, url_prefix='/admin')

# must be logged in and an admin
@bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    users = User.query.all()
    user_list = [{'id': user.id, 'username': user.username, 
                  'is_admin': user.is_admin, 'salary': user.salary} 
                 for user in users]
    return jsonify(user_list)

@bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    data = request.json
    user = User.query.get_or_404(user_id)

    new_salary = float(data.get('salary', user.salary))
    if new_salary < 0:
        return jsonify({'error': 'Salary cannot be negative'}), 400
    
    user.username = data.get('username', user.username)
    # if no uploaded password, keep existing one
    user.password = (bcrypt.generate_password_hash(data['password']).decode('utf-8') 
                     if ('password' in data and data['password']) else user.password)
    user.is_admin = data.get('is_admin', user.is_admin)
    user.salary = new_salary
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@bp.route('/users', methods=['POST'])
@login_required
@admin_required
def add_user():
    data = request.json
    # salted automatically. default not admin
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password, 
                    is_admin=data.get('is_admin', False), 
                    salary=data.get('salary', 0.0))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully'})

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    # prevent deletion of default admin user or self-deletion
    if user_id == 1:
        return jsonify({'error': 'Cannot delete the default admin user'}), 403
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete your own user account'}), 403

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})