"""
Script to initialize the database with sample data
Run this after starting the application for the first time
"""

from app import create_app, db
from app.models.user import User
from app.models.department import Department
from app.models.doctor import Doctor, DoctorAvailability
from app.models.patient import Patient
from datetime import date, time, timedelta

def init_sample_data():
    """Initialize database with sample data"""
    app = create_app('development')

    with app.app_context():
        print("Starting database initialization...")

        # Create departments
        print("\nCreating departments...")
        departments = [
            Department(name='Cardiology', description='Heart and cardiovascular care'),
            Department(name='Orthopedics', description='Bone and joint care'),
            Department(name='Pediatrics', description='Child healthcare'),
            Department(name='Dermatology', description='Skin care'),
            Department(name='Neurology', description='Brain and nervous system'),
        ]

        for dept in departments:
            existing = Department.query.filter_by(name=dept.name).first()
            if not existing:
                db.session.add(dept)
                print(f"  - Created department: {dept.name}")
            else:
                print(f"  - Department already exists: {dept.name}")

        db.session.commit()

        # Create sample doctors
        print("\nCreating sample doctors...")
        doctors_data = [
            {
                'username': 'dr_heart',
                'email': 'heart@hospital.com',
                'password': 'doctor123',
                'full_name': 'Dr. Sarah Johnson',
                'phone': '+1234567001',
                'department': 'Cardiology',
                'qualification': 'MD, Cardiology',
                'experience_years': 15,
                'consultation_fee': 150.0,
                'bio': 'Experienced cardiologist specializing in heart disease prevention'
            },
            {
                'username': 'dr_bones',
                'email': 'bones@hospital.com',
                'password': 'doctor123',
                'full_name': 'Dr. Michael Chen',
                'phone': '+1234567002',
                'department': 'Orthopedics',
                'qualification': 'MD, Orthopedic Surgery',
                'experience_years': 12,
                'consultation_fee': 140.0,
                'bio': 'Specialist in sports injuries and joint replacement'
            },
            {
                'username': 'dr_kids',
                'email': 'kids@hospital.com',
                'password': 'doctor123',
                'full_name': 'Dr. Emily Williams',
                'phone': '+1234567003',
                'department': 'Pediatrics',
                'qualification': 'MD, Pediatrics',
                'experience_years': 10,
                'consultation_fee': 120.0,
                'bio': 'Dedicated to providing comprehensive care for children'
            },
        ]

        for doc_data in doctors_data:
            existing_user = User.query.filter_by(username=doc_data['username']).first()
            if not existing_user:
                # Create user
                user = User(
                    username=doc_data['username'],
                    email=doc_data['email'],
                    role='doctor',
                    is_active=True
                )
                user.set_password(doc_data['password'])
                db.session.add(user)
                db.session.flush()

                # Create doctor profile
                dept = Department.query.filter_by(name=doc_data['department']).first()
                doctor = Doctor(
                    user_id=user.id,
                    full_name=doc_data['full_name'],
                    phone=doc_data['phone'],
                    department_id=dept.id,
                    qualification=doc_data['qualification'],
                    experience_years=doc_data['experience_years'],
                    consultation_fee=doc_data['consultation_fee'],
                    bio=doc_data['bio'],
                    is_available=True
                )
                db.session.add(doctor)
                db.session.flush()

                # Add availability for next 7 days
                today = date.today()
                for i in range(1, 8):
                    avail_date = today + timedelta(days=i)
                    availability = DoctorAvailability(
                        doctor_id=doctor.id,
                        date=avail_date,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        is_available=True
                    )
                    db.session.add(availability)

                print(f"  - Created doctor: {doc_data['full_name']}")
            else:
                print(f"  - Doctor already exists: {doc_data['username']}")

        db.session.commit()

        # Create sample patient
        print("\nCreating sample patient...")
        patient_user = User.query.filter_by(username='patient1').first()
        if not patient_user:
            patient_user = User(
                username='patient1',
                email='patient1@example.com',
                role='patient',
                is_active=True
            )
            patient_user.set_password('patient123')
            db.session.add(patient_user)
            db.session.flush()

            patient = Patient(
                user_id=patient_user.id,
                full_name='John Doe',
                phone='+1234567890',
                date_of_birth=date(1990, 1, 1),
                gender='Male',
                blood_group='O+',
                address='123 Main Street, City',
                emergency_contact='+0987654321'
            )
            db.session.add(patient)
            db.session.commit()
            print("  - Created patient: John Doe (username: patient1, password: patient123)")
        else:
            print("  - Sample patient already exists")

        print("\n" + "="*50)
        print("Database initialization completed!")
        print("="*50)
        print("\nDefault Credentials:")
        print("-" * 50)
        print("Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nSample Doctors:")
        print("  Username: dr_heart, dr_bones, dr_kids")
        print("  Password: doctor123")
        print("\nSample Patient:")
        print("  Username: patient1")
        print("  Password: patient123")
        print("-" * 50)

if __name__ == '__main__':
    init_sample_data()
