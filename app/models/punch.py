from app.extensions import db
import enum
from datetime import timezone

class PunchType(enum.Enum):
    IN = "IN"
    OUT = "OUT"

class Punch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # timezone-aware doesn't work with sqlite, so store as UTC and convert on access
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    # enum for punch type in/out
    type = db.Column(db.Enum(PunchType), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('punches', lazy=True))
    # save salary at time of punch
    salary_at_time = db.Column(db.Float, nullable=False)

    @property
    def timestamp_utc(self):
        # Always return UTC-aware datetime so we can do
        # operations on it with other timestamps
        if self.timestamp.tzinfo is None:
            return self.timestamp.replace(tzinfo=timezone.utc)
        return self.timestamp

    def __repr__(self):
        return f'<Punch {self.id} - {self.type} at {self.timestamp_utc} for User {self.user_id}>'