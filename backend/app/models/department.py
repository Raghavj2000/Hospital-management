from datetime import datetime
from app import db

class Department(db.Model):
    """Department/Specialization model"""
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    doctors = db.relationship('Doctor', backref='department', lazy='dynamic')

    @property
    def doctors_count(self):
        """Count of registered doctors in this department"""
        return self.doctors.filter_by(is_available=True).count()

    def to_dict(self):
        """Convert department to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'doctors_count': self.doctors_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Department {self.name}>'
