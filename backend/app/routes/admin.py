from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, func
from app import db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.department import Department
from app.utils.decorators import role_required
from app.utils.validators import validate_email, validate_required_fields
from app.utils.cache import invalidate_cache, cache_response

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('admin')
@cache_response('admin_dashboard', timeout=300)
def dashboard():
    """Get admin dashboard statistics"""
    try:
        total_doctors = Doctor.query.filter_by(is_available=True).count()
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        booked_appointments = Appointment.query.filter_by(status='Booked').count()
        completed_appointments = Appointment.query.filter_by(status='Completed').count()
        cancelled_appointments = Appointment.query.filter_by(status='Cancelled').count()
        total_departments = Department.query.count()

        return jsonify({
            'total_doctors': total_doctors,
            'total_patients': total_patients,
            'total_appointments': total_appointments,
            'booked_appointments': booked_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'total_departments': total_departments
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch dashboard data: {str(e)}'}), 500


#Department Management Routes

"""Get all departments"""
@bp.route('/departments', methods=['GET'])
@jwt_required()
@role_required('admin')
@cache_response('admin_departments', timeout=600)
def get_departments():
    try:
        departments = Department.query.all()
        return jsonify({
            'departments': [dept.to_dict() for dept in departments]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch departments: {str(e)}'}), 500


"""Create a new department"""
@bp.route('/departments', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_department():
    data = request.get_json()

    required_fields = ['name']
    missing_fields = validate_required_fields(data, required_fields)
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    if Department.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Department already exists'}), 409

    try:
        department = Department(
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(department)
        db.session.commit()

        invalidate_cache('departments')

        return jsonify({
            'message': 'Department created successfully',
            'department': department.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create department: {str(e)}'}), 500


"""Update a department"""
@bp.route('/departments/<int:dept_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_department(dept_id):
    
    department = Department.query.get(dept_id)
    if not department:
        return jsonify({'error': 'Department not found'}), 404

    data = request.get_json()

    try:
        if 'name' in data:
            # Check if new name already exists
            existing = Department.query.filter_by(name=data['name']).first()
            if existing and existing.id != dept_id:
                return jsonify({'error': 'Department name already exists'}), 409
            department.name = data['name']

        if 'description' in data:
            department.description = data['description']

        db.session.commit()
        invalidate_cache('departments')

        return jsonify({
            'message': 'Department updated successfully',
            'department': department.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update department: {str(e)}'}), 500


"""Delete a department"""
@bp.route('/departments/<int:dept_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_department(dept_id):
   
    department = Department.query.get(dept_id)
    if not department:
        return jsonify({'error': 'Department not found'}), 404

    # Check if department has doctors
    if department.doctors.count() > 0:
        return jsonify({'error': 'Cannot delete department with existing doctors'}), 400

    try:
        db.session.delete(department)
        db.session.commit()
        invalidate_cache('departments')

        return jsonify({'message': 'Department deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete department: {str(e)}'}), 500


#Doctor Management Routes

@bp.route('/doctors', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_doctors():
    """Get all doctors with optional filters"""
    try:
        query = Doctor.query

        # Filter by department
        dept_id = request.args.get('department_id')
        if dept_id:
            query = query.filter_by(department_id=dept_id)

        # Filter by availability
        is_available = request.args.get('is_available')
        if is_available is not None:
            query = query.filter_by(is_available=is_available.lower() == 'true')

        doctors = query.all()

        return jsonify({
            'doctors': [doctor.to_dict(include_user=True) for doctor in doctors]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch doctors: {str(e)}'}), 500


"""Get a specific doctor"""
@bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_doctor(doctor_id):
    
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404

    return jsonify({'doctor': doctor.to_dict(include_user=True)}), 200


"""Create a new doctor account"""
@bp.route('/doctors', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_doctor():
    
    data = request.get_json()

    required_fields = ['username', 'email', 'password', 'full_name', 'department_id']
    missing_fields = validate_required_fields(data, required_fields)
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400

    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409

    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409

    # Verify department exists
    department = Department.query.get(data['department_id'])
    if not department:
        return jsonify({'error': 'Department not found'}), 404

    try:
        # Create user account
        user = User(
            username=data['username'],
            email=data['email'],
            role='doctor',
            is_active=True
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()

        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            full_name=data['full_name'],
            phone=data.get('phone'),
            department_id=data['department_id'],
            qualification=data.get('qualification'),
            experience_years=data.get('experience_years', 0),
            consultation_fee=data.get('consultation_fee', 0.0),
            bio=data.get('bio'),
            is_available=data.get('is_available', True)
        )
        db.session.add(doctor)
        db.session.commit()

        invalidate_cache('doctors')

        return jsonify({
            'message': 'Doctor created successfully',
            'doctor': doctor.to_dict(include_user=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create doctor: {str(e)}'}), 500


"""Update doctor profile"""
@bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_doctor(doctor_id):
    
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404

    data = request.get_json()

    try:
        # Update doctor fields
        if 'full_name' in data:
            doctor.full_name = data['full_name']
        if 'phone' in data:
            doctor.phone = data['phone']
        if 'department_id' in data:
            department = Department.query.get(data['department_id'])
            if not department:
                return jsonify({'error': 'Department not found'}), 404
            doctor.department_id = data['department_id']
        if 'qualification' in data:
            doctor.qualification = data['qualification']
        if 'experience_years' in data:
            doctor.experience_years = data['experience_years']
        if 'consultation_fee' in data:
            doctor.consultation_fee = data['consultation_fee']
        if 'bio' in data:
            doctor.bio = data['bio']
        if 'is_available' in data:
            doctor.is_available = data['is_available']

        # Update user fields if provided
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != doctor.user_id:
                return jsonify({'error': 'Email already exists'}), 409
            doctor.user.email = data['email']

        db.session.commit()
        invalidate_cache('doctors')

        return jsonify({
            'message': 'Doctor updated successfully',
            'doctor': doctor.to_dict(include_user=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update doctor: {str(e)}'}), 500


@bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_doctor(doctor_id):
    """Delete/Blacklist a doctor"""
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404

    # Check for pending appointments
    pending_appointments = Appointment.query.filter_by(
        doctor_id=doctor_id,
        status='Booked'
    ).count()

    if pending_appointments > 0:
        return jsonify({'error': f'Cannot delete doctor with {pending_appointments} pending appointments'}), 400

    try:
        # Blacklist the user instead of deleting
        doctor.user.is_blacklisted = True
        doctor.is_available = False
        db.session.commit()
        invalidate_cache('doctors')

        return jsonify({'message': 'Doctor blacklisted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to blacklist doctor: {str(e)}'}), 500


# ============= Patient Management =============

@bp.route('/patients', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_patients():
    """Get all patients"""
    try:
        patients = Patient.query.all()

        return jsonify({
            'patients': [patient.to_dict(include_user=True) for patient in patients]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch patients: {str(e)}'}), 500


@bp.route('/patients/<int:patient_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_patient(patient_id):
    """Get a specific patient"""
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    return jsonify({'patient': patient.to_dict(include_user=True)}), 200


@bp.route('/patients/<int:patient_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_patient(patient_id):
    """Update patient profile"""
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    data = request.get_json()

    try:
        # Update patient fields
        if 'full_name' in data:
            patient.full_name = data['full_name']
        if 'phone' in data:
            patient.phone = data['phone']
        if 'date_of_birth' in data:
            patient.date_of_birth = data['date_of_birth']
        if 'gender' in data:
            patient.gender = data['gender']
        if 'blood_group' in data:
            patient.blood_group = data['blood_group']
        if 'address' in data:
            patient.address = data['address']
        if 'emergency_contact' in data:
            patient.emergency_contact = data['emergency_contact']
        if 'medical_history' in data:
            patient.medical_history = data['medical_history']
        if 'allergies' in data:
            patient.allergies = data['allergies']

        # Update user fields if provided
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != patient.user_id:
                return jsonify({'error': 'Email already exists'}), 409
            patient.user.email = data['email']

        db.session.commit()

        return jsonify({
            'message': 'Patient updated successfully',
            'patient': patient.to_dict(include_user=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update patient: {str(e)}'}), 500


@bp.route('/patients/<int:patient_id>/blacklist', methods=['POST'])
@jwt_required()
@role_required('admin')
def blacklist_patient(patient_id):
    """Blacklist a patient"""
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    try:
        patient.user.is_blacklisted = True
        db.session.commit()

        return jsonify({'message': 'Patient blacklisted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to blacklist patient: {str(e)}'}), 500


# ============= Appointment Management =============

@bp.route('/appointments', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_appointments():
    """Get all appointments with optional filters"""
    try:
        query = Appointment.query

        # Filter by status
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)

        # Filter by date
        date = request.args.get('date')
        if date:
            query = query.filter_by(appointment_date=date)

        # Filter by doctor
        doctor_id = request.args.get('doctor_id')
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)

        # Filter by patient
        patient_id = request.args.get('patient_id')
        if patient_id:
            query = query.filter_by(patient_id=patient_id)

        appointments = query.order_by(Appointment.appointment_date.desc()).all()

        return jsonify({
            'appointments': [apt.to_dict(include_details=True) for apt in appointments]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch appointments: {str(e)}'}), 500


# ============= Search Functionality =============

@bp.route('/search/doctors', methods=['GET'])
@jwt_required()
@role_required('admin')
def search_doctors():
    """Search doctors by name or specialization"""
    query_str = request.args.get('q', '').strip()

    if not query_str:
        return jsonify({'error': 'Search query is required'}), 400

    try:
        # Search in doctor name and department name
        doctors = Doctor.query.join(Department).filter(
            or_(
                Doctor.full_name.ilike(f'%{query_str}%'),
                Department.name.ilike(f'%{query_str}%')
            )
        ).all()

        return jsonify({
            'doctors': [doctor.to_dict(include_user=True) for doctor in doctors]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


@bp.route('/search/patients', methods=['GET'])
@jwt_required()
@role_required('admin')
def search_patients():
    """Search patients by name, ID, or contact"""
    query_str = request.args.get('q', '').strip()

    if not query_str:
        return jsonify({'error': 'Search query is required'}), 400

    try:
        # Search in patient name, phone
        patients = Patient.query.filter(
            or_(
                Patient.full_name.ilike(f'%{query_str}%'),
                Patient.phone.ilike(f'%{query_str}%'),
                Patient.id == int(query_str) if query_str.isdigit() else False
            )
        ).all()

        return jsonify({
            'patients': [patient.to_dict(include_user=True) for patient in patients]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500
