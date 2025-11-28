from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_
from app import db
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor, DoctorAvailability
from app.models.department import Department
from app.models.appointment import Appointment
from app.models.treatment import Treatment
from app.utils.decorators import role_required
from app.utils.validators import parse_date, parse_time
from app.utils.cache import cache_response, invalidate_cache
from config.config import config

bp = Blueprint('patient', __name__, url_prefix='/api/patient')

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('patient')
def dashboard():
    """Get patient dashboard with departments and statistics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = user.patient_profile

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Get all departments
        departments = Department.query.all()

        # Count upcoming appointments
        today = date.today()
        upcoming_appointments = Appointment.query.filter(
            and_(
                Appointment.patient_id == patient.id,
                Appointment.appointment_date >= today,
                Appointment.status == 'Booked'
            )
        ).count()

        # Count total appointments
        total_appointments = Appointment.query.filter_by(
            patient_id=patient.id
        ).count()

        return jsonify({
            'departments': [dept.to_dict() for dept in departments],
            'upcoming_appointments': upcoming_appointments,
            'total_appointments': total_appointments
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch dashboard data: {str(e)}'}), 500


# ============= Department & Doctor Browsing =============

@bp.route('/departments', methods=['GET'])
@jwt_required()
@role_required('patient')
@cache_response('patient_departments', timeout=600)
def get_departments():
    """Get all departments/specializations"""
    try:
        departments = Department.query.all()

        return jsonify({
            'departments': [dept.to_dict() for dept in departments]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch departments: {str(e)}'}), 500


@bp.route('/departments/<int:dept_id>/doctors', methods=['GET'])
@jwt_required()
@role_required('patient')
def get_department_doctors(dept_id):
    """Get all doctors in a specific department"""
    try:
        department = Department.query.get(dept_id)
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        doctors = Doctor.query.filter_by(
            department_id=dept_id,
            is_available=True
        ).all()

        return jsonify({
            'department': department.to_dict(),
            'doctors': [doctor.to_dict() for doctor in doctors]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch doctors: {str(e)}'}), 500


@bp.route('/doctors', methods=['GET'])
@jwt_required()
@role_required('patient')
def get_doctors():
    """Get all available doctors with optional filters"""
    try:
        query = Doctor.query.filter_by(is_available=True)

        # Filter by department
        dept_id = request.args.get('department_id')
        if dept_id:
            query = query.filter_by(department_id=dept_id)

        doctors = query.all()

        return jsonify({
            'doctors': [doctor.to_dict() for doctor in doctors]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch doctors: {str(e)}'}), 500


@bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@jwt_required()
@role_required('patient')
def get_doctor(doctor_id):
    """Get doctor details and availability"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        # Get availability for next 7 days
        today = date.today()
        week_from_now = today + timedelta(days=7)

        availability = DoctorAvailability.query.filter(
            and_(
                DoctorAvailability.doctor_id == doctor_id,
                DoctorAvailability.date >= today,
                DoctorAvailability.date <= week_from_now,
                DoctorAvailability.is_available == True
            )
        ).order_by(DoctorAvailability.date.asc()).all()

        return jsonify({
            'doctor': doctor.to_dict(),
            'availability': [slot.to_dict() for slot in availability]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch doctor details: {str(e)}'}), 500


# ============= Appointment Management =============

@bp.route('/appointments', methods=['GET'])
@jwt_required()
@role_required('patient')
def get_appointments():
    """Get patient's appointments"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = user.patient_profile

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        query = Appointment.query.filter_by(patient_id=patient.id)

        # Filter by status
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)

        # Filter upcoming appointments
        if request.args.get('upcoming') == 'true':
            today = date.today()
            query = query.filter(Appointment.appointment_date >= today)

        # Filter past appointments
        if request.args.get('past') == 'true':
            today = date.today()
            query = query.filter(Appointment.appointment_date < today)

        appointments = query.order_by(Appointment.appointment_date.desc()).all()

        return jsonify({
            'appointments': [apt.to_dict(include_details=True) for apt in appointments]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch appointments: {str(e)}'}), 500


@bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
@role_required('patient')
def get_appointment(appointment_id):
    """Get a specific appointment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = user.patient_profile

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        appointment = Appointment.query.filter_by(
            id=appointment_id,
            patient_id=patient.id
        ).first()

        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        return jsonify({
            'appointment': appointment.to_dict(include_details=True)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch appointment: {str(e)}'}), 500


@bp.route('/appointments', methods=['POST'])
@jwt_required()
@role_required('patient')
def book_appointment():
    """Book a new appointment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = user.patient_profile

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        data = request.get_json()

        # Validate doctor exists
        doctor = Doctor.query.get(data['doctor_id'])
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        if not doctor.is_available:
            return jsonify({'error': 'Doctor is not available'}), 400

        # Parse and validate date and time
        appointment_date = parse_date(data['appointment_date'])
        appointment_time = parse_time(data['appointment_time'])

        if not appointment_date or not appointment_time:
            return jsonify({'error': 'Invalid date or time format'}), 400

        # Check if date is in the future
        if appointment_date < date.today():
            return jsonify({'error': 'Cannot book appointments for past dates'}), 400

        # Check for duplicate booking (same doctor, date, time)
        existing = Appointment.query.filter_by(
            doctor_id=data['doctor_id'],
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).filter(Appointment.status != 'Cancelled').first()

        if existing:
            return jsonify({'error': 'This time slot is already booked'}), 409

        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=data['doctor_id'],
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='Booked',
            reason=data.get('reason'),
            notes=data.get('notes')
        )
        db.session.add(appointment)
        db.session.commit()

        invalidate_cache('appointments')

        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment': appointment.to_dict(include_details=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to book appointment: {str(e)}'}), 500


@bp.route('/appointments/<int:appointment_id>/reschedule', methods=['PUT'])
@jwt_required()
@role_required('patient')
def reschedule_appointment(appointment_id):
    """Reschedule an existing appointment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = user.patient_profile

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        appointment = Appointment.query.filter_by(
            id=appointment_id,
            patient_id=patient.id
        ).first()

        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        if appointment.status == 'Completed':
            return jsonify({'error': 'Cannot reschedule a completed appointment'}), 400

        if appointment.status == 'Cancelled':
            return jsonify({'error': 'Cannot reschedule a cancelled appointment'}), 400

        data = request.get_json()

        # Parse new date and time
        new_date = parse_date(data['appointment_date'])
        new_time = parse_time(data['appointment_time'])

        if not new_date or not new_time:
            return jsonify({'error': 'Invalid date or time format'}), 400

        if new_date < date.today():
            return jsonify({'error': 'Cannot reschedule to past dates'}), 400

        # Check if new slot is available
        existing = Appointment.query.filter_by(
            doctor_id=appointment.doctor_id,
            appointment_date=new_date,
            appointment_time=new_time
        ).filter(
            Appointment.status != 'Cancelled',
            Appointment.id != appointment_id
        ).first()

        if existing:
            return jsonify({'error': 'This time slot is already booked'}), 409

        # Update appointment
        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        if 'reason' in data:
            appointment.reason = data['reason']
        if 'notes' in data:
            appointment.notes = data['notes']

        db.session.commit()
        invalidate_cache('appointments')

        return jsonify({
            'message': 'Appointment rescheduled successfully',
            'appointment': appointment.to_dict(include_details=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to reschedule appointment: {str(e)}'}), 500


@bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@jwt_required()
@role_required('patient')
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = user.patient_profile

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        appointment = Appointment.query.filter_by(
            id=appointment_id,
            patient_id=patient.id
        ).first()

        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        if appointment.status == 'Cancelled':
            return jsonify({'error': 'Appointment already cancelled'}), 400

        if appointment.status == 'Completed':
            return jsonify({'error': 'Cannot cancel a completed appointment'}), 400

        appointment.status = 'Cancelled'
        db.session.commit()
        invalidate_cache('appointments')

        return jsonify({
            'message': 'Appointment cancelled successfully',
            'appointment': appointment.to_dict(include_details=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to cancel appointment: {str(e)}'}), 500


# ============= Treatment History =============

@bp.route('/treatments', methods=['GET'])
@jwt_required()
@role_required('patient')
def get_treatment_history():
    """Get patient's treatment history"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = user.patient_profile

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Get all appointments for this patient
        appointment_ids = db.session.query(Appointment.id).filter_by(
            patient_id=patient.id
        ).all()
        appointment_ids = [aid[0] for aid in appointment_ids]

        # Get all treatments
        treatments = Treatment.query.filter(
            Treatment.appointment_id.in_(appointment_ids)
        ).all()

        return jsonify({
            'treatments': [treatment.to_dict(include_appointment=True) for treatment in treatments]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch treatment history: {str(e)}'}), 500


@bp.route('/treatments/<int:treatment_id>', methods=['GET'])
@jwt_required()
@role_required('patient')
def get_treatment(treatment_id):
    """Get a specific treatment record"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = user.patient_profile

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        treatment = Treatment.query.join(Appointment).filter(
            Treatment.id == treatment_id,
            Appointment.patient_id == patient.id
        ).first()

        if not treatment:
            return jsonify({'error': 'Treatment record not found'}), 404

        return jsonify({
            'treatment': treatment.to_dict(include_appointment=True)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch treatment: {str(e)}'}), 500


# ============= Profile Management =============

@bp.route('/profile', methods=['GET'])
@jwt_required()
@role_required('patient')
def get_profile():
    """Get patient's own profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = user.patient_profile

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        return jsonify({
            'profile': patient.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch profile: {str(e)}'}), 500


@bp.route('/profile', methods=['PUT'])
@jwt_required()
@role_required('patient')
def update_profile():
    """Update patient's own profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = user.patient_profile

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        data = request.get_json()

        # Update patient fields
        if 'full_name' in data:
            patient.full_name = data['full_name']
        if 'phone' in data:
            patient.phone = data['phone']
        if 'date_of_birth' in data:
            patient.date_of_birth = parse_date(data['date_of_birth'])
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

        db.session.commit()

        return jsonify({
            'message': 'Profile updated successfully',
            'profile': patient.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500


# ============= CSV Export =============

@bp.route('/export/treatments', methods=['POST'])
@jwt_required()
@role_required('patient')
def export_treatments():
    """Trigger async job to export treatment history as CSV"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = user.patient_profile

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Import task here to avoid circular imports
        from app.tasks import export_patient_treatments

        # Trigger async task
        task = export_patient_treatments.delay(patient.id)

        return jsonify({
            'message': 'Export job started. You will receive an email when it\'s ready.',
            'task_id': task.id,
            'status': 'processing'
        }), 202

    except Exception as e:
        return jsonify({'error': f'Failed to start export: {str(e)}'}), 500


@bp.route('/export/status/<task_id>', methods=['GET'])
@jwt_required()
@role_required('patient')
def get_export_status(task_id):
    """Check status of export job"""
    try:
        from app.tasks import export_patient_treatments
        from celery.result import AsyncResult

        task = AsyncResult(task_id)

        if task.state == 'PENDING':
            response = {
                'status': 'pending',
                'message': 'Export is queued'
            }
        elif task.state == 'PROGRESS':
            response = {
                'status': 'processing',
                'message': 'Export is in progress'
            }
        elif task.state == 'SUCCESS':
            response = {
                'status': 'completed',
                'message': 'Export completed successfully',
                'result': task.result
            }
        else:
            response = {
                'status': 'failed',
                'message': str(task.info)
            }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': f'Failed to check export status: {str(e)}'}), 500
