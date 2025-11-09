from app.models.punch import Punch, PunchType
from app.extensions import db
from datetime import datetime, timezone


def get_last_punch(user):
    return Punch.query \
        .filter(Punch.user_id == user.id) \
        .order_by(Punch.timestamp.desc()) \
        .first()

# get the most recent punch before date_time
# or most recent punch if date_time is None
def get_prev_punch(user, date_time=None):
    date_time = date_time or datetime.now(timezone.utc)
    return Punch.query \
        .filter(
            Punch.user_id == user.id, 
            Punch.timestamp < date_time) \
        .order_by(Punch.timestamp.desc()) \
        .first()

# get the next punch after date_time
def get_next_punch(user, date_time):
    return Punch.query \
        .filter(
            Punch.user_id == user.id, 
            Punch.timestamp > date_time) \
        .order_by(Punch.timestamp.asc()) \
        .first()

# get all punches in a datetime range
def get_punches_in_range(user, start_datetime, end_datetime):
    if start_datetime >= end_datetime:
        end_datetime, start_datetime = start_datetime, end_datetime
    
    return Punch.query \
        .filter(
            Punch.user_id == user.id,
            Punch.timestamp >= start_datetime,
            Punch.timestamp <= end_datetime) \
        .order_by(Punch.timestamp.asc()) \
        .all()

# calculate total salary for punches in a datetime range
# account for salary changes over punches
def get_salary_for_range(user, start_datetime, end_datetime):
    punches = get_punches_in_range(user, start_datetime, end_datetime)
    total_salary = 0.0

    for i in range(0, len(punches), 2):
        if i + 1 < len(punches):
            in_punch = punches[i]
            out_punch = punches[i + 1]
            time_worked = (out_punch.timestamp_utc - in_punch.timestamp_utc).total_seconds() / 3600.0
            total_salary += time_worked * in_punch.salary_at_time

    return total_salary

# insert a pair of punches at specified datetimes
def insert_punches(user, first_datetime, second_datetime, salary=None):
    if first_datetime >= second_datetime:
        raise ValueError("First datetime must be earlier than second datetime.")
    
    punch_after_prev = get_next_punch(user, first_datetime)
    if punch_after_prev is not None and punch_after_prev.timestamp_utc < second_datetime:
        raise ValueError("Inserted punches overlap with existing punches.")
    

    # don't commit after first punch so both are added in one transaction
    # and can be rolled back together on error 
    p1 = save_punch(user, first_datetime, do_commit=False, salary=salary)
    p2 = save_punch(user, second_datetime, salary=salary)
    return [p1, p2]

# punch clock in/out at specified datetime (or now)
def punch_clock(user, date_time=None, salary=None):
    last = get_last_punch(user)
    if last and date_time is not None and last.timestamp_utc >= date_time:
        raise ValueError("Cannot punch with earlier timestamp than last punch.")
    return save_punch(user, date_time, salary=salary)

# create a new punch record optionally with specified salary
def save_punch(user, date_time=None, do_commit=True, salary=None):
    # standard to use UTC 
    date_time = date_time or datetime.now(timezone.utc)
    # logic for punching clock in/out
    last = get_prev_punch(user, date_time)

    punch_type = (
        PunchType.IN 
        if last is None or last.type == PunchType.OUT 
        else PunchType.OUT
    )

    salary = salary if salary is not None else user.salary
    if salary < 0:
        raise ValueError("Salary cannot be negative.")

    new_punch = Punch(
        user_id=user.id,
        timestamp=date_time,
        type=punch_type,
        salary_at_time=salary
    )

    db.session.add(new_punch)
    if do_commit:
        db.session.commit()

    return new_punch
