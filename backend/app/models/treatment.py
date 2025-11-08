from datetime import datetime
from app import db

class Treatment(db.Model):
    __tablename__ = 'treatments'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False, unique=True, index=True)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=True)
    treatment_notes = db.Column(db.Text, nullable=True)
    next_visit_date = db.Column(db.Date, nullable=True)
    follow_up_required = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self, include_appointment=False):
        """Convert treatment to dictionary"""
        data = {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'treatment_notes': self.treatment_notes,
            'next_visit_date': self.next_visit_date.isoformat() if self.next_visit_date else None,
            'follow_up_required': self.follow_up_required,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_appointment and self.appointment:
            data['appointment_date'] = self.appointment.appointment_date.isoformat()
            data['appointment_time'] = self.appointment.appointment_time.strftime('%H:%M')
            data['doctor_name'] = self.appointment.doctor.full_name if self.appointment.doctor else None
            data['department'] = self.appointment.doctor.department.name if self.appointment.doctor and self.appointment.doctor.department else None

        return data

    def __repr__(self):
        return f'<Treatment {self.id} for Appointment:{self.appointment_id}>'
