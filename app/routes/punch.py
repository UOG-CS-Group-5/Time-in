from flask import Blueprint, request
from flask_login import login_required, current_user
from app.models.punch import Punch
from app.extensions import db
from app.services.punch_service import punch_clock, get_last_punch, insert_punches
from app.models.user import User
from datetime import datetime

bp = Blueprint('punch', __name__)

@bp.route('/punch', methods=['POST'])
@login_required
def punch_clock_route():
    """Endpoint to punch clock in/out for an employee.
    if user_id provided and is admin, punch for that user
    if datetime provided, use that timestamp as the punch time
    if datetime_end provided, use that timestamp as the end time
    """
    # logic for punching clock in/out
    user_id = int(request.args.get('user_id', current_user.id))
    date_str = request.args.get('datetime', None)
    date_end_str = request.args.get('datetime_end', None)

    if (not current_user.is_admin) and user_id != current_user.id:
        return 'Forbidden', 403
    
    if (not current_user.is_admin) and (
            date_str is not None or date_end_str is not None):
        return 'Forbidden to set datetime', 403
    
    if date_end_str is not None and date_str is None:
        return 'datetime must be provided if datetime_end is provided', 400

    # do I need to mess with UTC here?
    dt = datetime.fromisoformat(date_str) if date_str else None
    end_dt = datetime.fromtimestamp(date_end_str) if date_end_str else None
    
    user = User.query.get(user_id)
    
    last_punch = get_last_punch(user)

    if last_punch and last_punch.timestamp_utc >= dt:
        return 'Cannot punch with earlier timestamp than last punch', 400

    ret = {
        'new_punches': []
    }
    try:
        if end_dt is not None:
            ret['new_punches'] = [*insert_punches(user, dt, end_dt)]
        else:
            ret['new_punches'].append(punch_clock(user, dt))
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