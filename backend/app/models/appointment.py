from datetime import datetime
from app import db

class Appointment(db.Model):
    """Appointment model"""
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, index=True)
    appointment_date = db.Column(db.Date, nullable=False, index=True)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Booked', nullable=False, index=True)  # 'Booked', 'Completed', 'Cancelled'
    reason = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    treatment = db.relationship('Treatment', backref='appointment', uselist=False, cascade='all, delete-orphan')

    # Unique constraint to prevent double booking
    __table_args__ = (db.UniqueConstraint('doctor_id', 'appointment_date', 'appointment_time', name='_doctor_datetime_uc'),)

    def to_dict(self, include_details=False):
        """Convert appointment to dictionary"""
        data = {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'appointment_date': self.appointment_date.isoformat(),
            'appointment_time': self.appointment_time.strftime('%H:%M'),
            'status': self.status,
            'reason': self.reason,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_details:
            if self.patient:
                data['patient_name'] = self.patient.full_name
                data['patient_phone'] = self.patient.phone
            if self.doctor:
                data['doctor_name'] = self.doctor.full_name
                data['department_name'] = self.doctor.department.name if self.doctor.department else None
            if self.treatment:
                data['treatment'] = self.treatment.to_dict()

        return data

    def __repr__(self):
        return f'<Appointment {self.id} - Patient:{self.patient_id} Doctor:{self.doctor_id}>'
