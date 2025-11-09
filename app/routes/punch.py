from flask import Blueprint, request
from flask_login import login_required, current_user
from app.models.punch import Punch
from app.extensions import db, admin_required
from app.services.punch_service import punch_clock, get_last_punch, get_prev_punch, get_next_punch, insert_punches
from app.models.user import User
from datetime import datetime

bp = Blueprint('punch', __name__)

@bp.route('/punch/closest_salary', methods=['GET'])
@login_required
@admin_required
def get_closest_salary():
    """Endpoint to get the closest salary for a specified user
    at a given datetime (past punch preferred)."""
    user_id = request.args.get('user_id', None)
    date_str = request.args.get('datetime', None)
    if date_str is None:
        return 'before parameter is required', 400
    
    date = datetime.fromisoformat(date_str)

    # if None or invalid user_id
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return 'user_id parameter is required', 400

    user = User.query.get(user_id)
    if user is None:
        return 'User not found', 404

    # check prev punch first then next punch
    try:
        closest_punch = get_prev_punch(user, date)
        if closest_punch is None:
            closest_punch = get_next_punch(user, date)
            if closest_punch is None:
                return 'No punches found for user', 404
    except ValueError as ve:
        return str(ve), 400

    return { 'salary': closest_punch.salary_at_time }, 200

@bp.route('/punch', methods=['POST'])
@login_required
def punch_clock_route():
    """Endpoint to punch clock in/out for an employee.
    if user_id provided and is admin, punch for that user
    if datetime provided, use that timestamp as the punch time
    if datetime_end provided, use that timestamp as the end time (2 punches)
    if salary provided, use that salary for the punch(es) (if admin)
    """
    user_id = int(request.args.get('user_id', current_user.id))
    date_str = request.args.get('datetime', None)
    date_end_str = request.args.get('datetime_end', None)
    # errors out if float(None), but we'll ignore for now 
    # since I don't want to do the default
    salary = float(request.args.get('salary', None))

    if (not current_user.is_admin) and user_id != current_user.id:
        return 'Forbidden', 403
    
    if (not current_user.is_admin) and (
            date_str is not None or date_end_str is not None):
        return 'Forbidden to set datetime', 403
    
    if (not current_user.is_admin) and salary is not None:
        return 'Forbidden to set salary', 403
    
    if date_end_str is not None and date_str is None:
        return 'datetime must be provided if datetime_end is provided', 400

    dt = datetime.fromisoformat(date_str) if date_str else None
    end_dt = datetime.fromisoformat(date_end_str) if date_end_str else None
    
    user = User.query.get(user_id)
    
    last_punch = get_last_punch(user)

    # if only a single date was given (which would mean a single 
    # punch is wanted) ensure it's after the last punch
    if end_dt is None and last_punch and last_punch.timestamp_utc >= dt:
        return 'Cannot punch with earlier timestamp than last punch', 400

    ret = {
        'new_punches': []
    }
    try:
        if end_dt is not None:
            ret['new_punches'] = [*insert_punches(user, dt, end_dt, salary)]
        else:
            ret['new_punches'].append(punch_clock(user, dt, salary))
    except ValueError as ve:
        return str(ve), 400
    
    ret['new_punches'] = [
        {
            'id': p.id,
            'timestamp': p.timestamp_utc.isoformat(),
            'type': p.type.value,
            'salary_at_time': p.salary_at_time  
        }
        for p in ret['new_punches']
    ]
    return ret, 201

@bp.route('/punch', methods=['GET'])
@login_required
def get_punches_route():
    """Endpoint to get all punches for the current user 
    (or specified user if admin)."""
    user_id = request.args.get('user_id', current_user.id)
    if (not current_user.is_admin) and user_id != current_user.id:
        return 'Forbidden', 403

    user = User.query.get(user_id)
    # better to do paging but we'll keep it simple
    punches = Punch.query.filter_by(user_id=user.id).order_by(Punch.timestamp.asc()).all()

    punch_list = [{
        'id': punch.id,
        'timestamp': punch.timestamp_utc.isoformat(),
        'type': punch.type.value,
        'salary_at_time': punch.salary_at_time
    } for punch in punches]
    return {'punches': punch_list}, 200

@bp.route('/punch', methods=['DELETE'])
@login_required
@admin_required
def delete_punch_route():
    """Endpoint to delete a specific punch by ID."""
    punch_id = request.args.get('punch_id', None)
    punch_end_id = request.args.get('punch_end_id', None)

    if punch_id is None:
        return 'punch_id parameter is required', 400

    punch = Punch.query.get(int(punch_id))
    if punch is None:
        return 'Punch not found', 404
    
    if punch_end_id is not None:
        punch_end = Punch.query.get(int(punch_end_id))
        if punch_end is None:
            return 'Punch end not found', 404
        if punch.user_id != punch_end.user_id:
            return 'Both punches must belong to the same user', 400
        if punch.timestamp_utc >= punch_end.timestamp_utc:
            return 'punch_id must be earlier than punch_end_id', 400
    
    last = get_last_punch(punch.user)
    # if only deleting one punch, ensure it's the last punch
    if punch_end_id is None and last and last.id != int(punch_id):
        return 'Can only delete the last punch when providing only one punch id', 400

    db.session.delete(punch)
    if punch_end_id:
        db.session.delete(punch_end)
    db.session.commit()
    return 'Punch deleted successfully', 200