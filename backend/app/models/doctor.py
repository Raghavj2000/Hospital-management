from datetime import datetime
from app import db

class Doctor(db.Model):
    """Doctor profile model"""
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(150), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    qualification = db.Column(db.String(200), nullable=True)
    experience_years = db.Column(db.Integer, default=0)
    consultation_fee = db.Column(db.Float, default=0.0)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic', cascade='all, delete-orphan')
    availability_slots = db.relationship('DoctorAvailability', backref='doctor', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_user=False):
        """Convert doctor to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'phone': self.phone,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'qualification': self.qualification,
            'experience_years': self.experience_years,
            'consultation_fee': self.consultation_fee,
            'is_available': self.is_available,
            'bio': self.bio,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_user and self.user:
            data['user'] = self.user.to_dict()
        return data

    def __repr__(self):
        return f'<Doctor {self.full_name}>'


class DoctorAvailability(db.Model):
    """Doctor availability schedule"""
    __tablename__ = 'doctor_availability'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Unique constraint to prevent duplicate slots
    __table_args__ = (db.UniqueConstraint('doctor_id', 'date', 'start_time', name='_doctor_date_time_uc'),)

    def to_dict(self):
        """Convert availability to dictionary"""
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'date': self.date.isoformat(),
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<DoctorAvailability Doctor:{self.doctor_id} Date:{self.date}>'
