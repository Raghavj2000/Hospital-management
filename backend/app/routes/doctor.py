from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from sqlalchemy import and_
from app import db
from app.models.user import User
from app.models.doctor import Doctor, DoctorAvailability
from app.models.appointment import Appointment
from app.models.treatment import Treatment
from app.models.patient import Patient
from app.utils.decorators import role_required
from app.utils.validators import parse_date, parse_time
from app.utils.cache import invalidate_cache

bp = Blueprint('doctor', __name__, url_prefix='/api/doctor')

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('doctor')
def dashboard():
    """Get doctor dashboard statistics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        # Get today's date
        today = date.today()
        week_from_now = today + timedelta(days=7)

        # Count appointments for today
        today_appointments = Appointment.query.filter(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == today,
                Appointment.status == 'Booked'
            )
        ).count()

        # Count appointments for this week
        week_appointments = Appointment.query.filter(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date >= today,
                Appointment.appointment_date <= week_from_now,
                Appointment.status == 'Booked'
            )
        ).count()

        # Total patients assigned
        total_patients = db.session.query(Appointment.patient_id).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().count()

        # Completed appointments
        completed_appointments = Appointment.query.filter(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.status == 'Completed'
            )
        ).count()

        return jsonify({
            'today_appointments': today_appointments,
            'week_appointments': week_appointments,
            'total_patients': total_patients,
            'completed_appointments': completed_appointments
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch dashboard data: {str(e)}'}), 500


@bp.route('/appointments', methods=['GET'])
@jwt_required()
@role_required('doctor')
def get_appointments():
    """Get doctor's appointments with optional filters"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        query = Appointment.query.filter_by(doctor_id=doctor.id)

        # Filter by status
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)

        # Filter by date
        date_str = request.args.get('date')
        if date_str:
            query = query.filter_by(appointment_date=date_str)

        # Filter by date range (upcoming appointments)
        if request.args.get('upcoming') == 'true':
            today = date.today()
            query = query.filter(Appointment.appointment_date >= today)

        appointments = query.order_by(
            Appointment.appointment_date.asc(),
            Appointment.appointment_time.asc()
        ).all()

        return jsonify({
            'appointments': [apt.to_dict(include_details=True) for apt in appointments]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch appointments: {str(e)}'}), 500


@bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
@role_required('doctor')
def get_appointment(appointment_id):
    """Get a specific appointment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        appointment = Appointment.query.filter_by(
            id=appointment_id,
            doctor_id=doctor.id
        ).first()

        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        return jsonify({
            'appointment': appointment.to_dict(include_details=True)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch appointment: {str(e)}'}), 500


@bp.route('/appointments/<int:appointment_id>/complete', methods=['POST'])
@jwt_required()
@role_required('doctor')
def complete_appointment(appointment_id):
    """Mark appointment as completed and add treatment details"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        appointment = Appointment.query.filter_by(
            id=appointment_id,
            doctor_id=doctor.id
        ).first()

        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        if appointment.status == 'Completed':
            return jsonify({'error': 'Appointment already completed'}), 400

        if appointment.status == 'Cancelled':
            return jsonify({'error': 'Cannot complete a cancelled appointment'}), 400

        data = request.get_json()

        # Update appointment status
        appointment.status = 'Completed'

        # Create or update treatment record
        treatment = Treatment.query.filter_by(appointment_id=appointment_id).first()

        if treatment:
            # Update existing treatment
            treatment.diagnosis = data['diagnosis']
            treatment.prescription = data.get('prescription')
            treatment.treatment_notes = data.get('treatment_notes')
            treatment.next_visit_date = parse_date(data['next_visit_date']) if data.get('next_visit_date') else None
            treatment.follow_up_required = data.get('follow_up_required', False)
        else:
            # Create new treatment
            treatment = Treatment(
                appointment_id=appointment_id,
                diagnosis=data['diagnosis'],
                prescription=data.get('prescription'),
                treatment_notes=data.get('treatment_notes'),
                next_visit_date=parse_date(data['next_visit_date']) if data.get('next_visit_date') else None,
                follow_up_required=data.get('follow_up_required', False)
            )
            db.session.add(treatment)

        db.session.commit()
        invalidate_cache('appointments')
        invalidate_cache('treatments')

        return jsonify({
            'message': 'Appointment completed successfully',
            'appointment': appointment.to_dict(include_details=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to complete appointment: {str(e)}'}), 500


@bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@jwt_required()
@role_required('doctor')
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        appointment = Appointment.query.filter_by(
            id=appointment_id,
            doctor_id=doctor.id
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


# ============= Patient Management =============

@bp.route('/patients', methods=['GET'])
@jwt_required()
@role_required('doctor')
def get_patients():
    """Get all patients assigned to this doctor"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        # Get distinct patients who have appointments with this doctor
        patient_ids = db.session.query(Appointment.patient_id).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().all()

        patient_ids = [pid[0] for pid in patient_ids]
        patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()

        return jsonify({
            'patients': [patient.to_dict() for patient in patients]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch patients: {str(e)}'}), 500


@bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@jwt_required()
@role_required('doctor')
def get_patient_history(patient_id):
    """Get patient's treatment history with this doctor"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404

        # Get all appointments for this patient with this doctor
        appointments = Appointment.query.filter_by(
            patient_id=patient_id,
            doctor_id=doctor.id
        ).order_by(Appointment.appointment_date.desc()).all()

        # Get treatment records
        appointment_ids = [apt.id for apt in appointments]
        treatments = Treatment.query.filter(
            Treatment.appointment_id.in_(appointment_ids)
        ).all()

        return jsonify({
            'patient': patient.to_dict(),
            'appointments': [apt.to_dict(include_details=True) for apt in appointments],
            'treatments': [treatment.to_dict(include_appointment=True) for treatment in treatments]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch patient history: {str(e)}'}), 500


@bp.route('/patients/<int:patient_id>/treatment', methods=['POST'])
@jwt_required()
@role_required('doctor')
def update_patient_treatment(patient_id):
    """Update patient treatment/medical notes"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        data = request.get_json()

        # Verify appointment belongs to this doctor and patient
        appointment = Appointment.query.filter_by(
            id=data['appointment_id'],
            patient_id=patient_id,
            doctor_id=doctor.id
        ).first()

        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        # Update or create treatment
        treatment = Treatment.query.filter_by(appointment_id=appointment.id).first()

        if treatment:
            treatment.diagnosis = data['diagnosis']
            treatment.prescription = data.get('prescription')
            treatment.treatment_notes = data.get('treatment_notes')
            treatment.next_visit_date = parse_date(data['next_visit_date']) if data.get('next_visit_date') else None
            treatment.follow_up_required = data.get('follow_up_required', False)
        else:
            treatment = Treatment(
                appointment_id=appointment.id,
                diagnosis=data['diagnosis'],
                prescription=data.get('prescription'),
                treatment_notes=data.get('treatment_notes'),
                next_visit_date=parse_date(data['next_visit_date']) if data.get('next_visit_date') else None,
                follow_up_required=data.get('follow_up_required', False)
            )
            db.session.add(treatment)

        db.session.commit()
        invalidate_cache('treatments')

        return jsonify({
            'message': 'Treatment updated successfully',
            'treatment': treatment.to_dict(include_appointment=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update treatment: {str(e)}'}), 500


# ============= Availability Management =============

@bp.route('/availability', methods=['GET'])
@jwt_required()
@role_required('doctor')
def get_availability():
    """Get doctor's availability schedule"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        # Get availability for next 7 days
        today = date.today()
        week_from_now = today + timedelta(days=7)

        availability = DoctorAvailability.query.filter(
            and_(
                DoctorAvailability.doctor_id == doctor.id,
                DoctorAvailability.date >= today,
                DoctorAvailability.date <= week_from_now
            )
        ).order_by(DoctorAvailability.date.asc()).all()

        return jsonify({
            'availability': [slot.to_dict() for slot in availability]
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch availability: {str(e)}'}), 500


@bp.route('/availability', methods=['POST'])
@jwt_required()
@role_required('doctor')
def set_availability():
    """Set doctor's availability for specific dates"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        data = request.get_json()

        availability_date = parse_date(data['date'])
        start_time = parse_time(data['start_time'])
        end_time = parse_time(data['end_time'])

        if not availability_date or not start_time or not end_time:
            return jsonify({'error': 'Invalid date or time format'}), 400

        if availability_date < date.today():
            return jsonify({'error': 'Cannot set availability for past dates'}), 400

        if start_time >= end_time:
            return jsonify({'error': 'Start time must be before end time'}), 400

        # Check if availability already exists
        existing = DoctorAvailability.query.filter_by(
            doctor_id=doctor.id,
            date=availability_date,
            start_time=start_time
        ).first()

        if existing:
            return jsonify({'error': 'Availability slot already exists'}), 409

        # Create availability slot
        availability = DoctorAvailability(
            doctor_id=doctor.id,
            date=availability_date,
            start_time=start_time,
            end_time=end_time,
            is_available=True
        )
        db.session.add(availability)
        db.session.commit()

        invalidate_cache('availability')

        return jsonify({
            'message': 'Availability set successfully',
            'availability': availability.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to set availability: {str(e)}'}), 500


@bp.route('/availability/<int:availability_id>', methods=['DELETE'])
@jwt_required()
@role_required('doctor')
def delete_availability(availability_id):
    """Delete an availability slot"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        availability = DoctorAvailability.query.filter_by(
            id=availability_id,
            doctor_id=doctor.id
        ).first()

        if not availability:
            return jsonify({'error': 'Availability slot not found'}), 404

        db.session.delete(availability)
        db.session.commit()
        invalidate_cache('availability')

        return jsonify({'message': 'Availability slot deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete availability: {str(e)}'}), 500


@bp.route('/profile', methods=['GET'])
@jwt_required()
@role_required('doctor')
def get_profile():
    """Get doctor's own profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        return jsonify({
            'profile': doctor.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch profile: {str(e)}'}), 500


@bp.route('/profile', methods=['PUT'])
@jwt_required()
@role_required('doctor')
def update_profile():
    """Update doctor's own profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        doctor = user.doctor_profile

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        data = request.get_json()

        # Update allowed fields
        if 'phone' in data:
            doctor.phone = data['phone']
        if 'bio' in data:
            doctor.bio = data['bio']

        db.session.commit()

        return jsonify({
            'message': 'Profile updated successfully',
            'profile': doctor.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500
