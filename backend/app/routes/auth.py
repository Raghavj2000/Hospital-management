from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.patient import Patient

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """Register a new patient"""
    data = request.get_json()

    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409

    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409

    try:
        # Create user account
        user = User(
            username=data['username'],
            email=data['email'],
            role='patient',
            is_active=True
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()

        # Create patient profile
        patient = Patient(
            user_id=user.id,
            full_name=data['full_name'],
            phone=data.get('phone'),
            gender=data.get('gender'),
            date_of_birth=data.get('date_of_birth'),
            blood_group=data.get('blood_group'),
            address=data.get('address')
        )
        db.session.add(patient)
        db.session.commit()

        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict(),
            'patient': patient.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """Login user (admin, doctor, or patient)"""
    data = request.get_json()

    # Find user
    user = User.query.filter_by(username=data['username']).first()
    print(user)
    print(data['password'])

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 403

    if user.is_blacklisted:
        return jsonify({'error': 'Account is blacklisted'}), 403

    # Create access tokens
    access_token = create_access_token(identity=str(user.id))

    # Get profile data based on role
    profile = None
    if user.role == 'doctor' and user.doctor_profile:
        profile = user.doctor_profile.to_dict()
    elif user.role == 'patient' and user.patient_profile:
        profile = user.patient_profile.to_dict()

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict(),
        'profile': profile
    }), 200


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current logged-in user details"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get profile data based on role
    profile = None
    if user.role == 'doctor' and user.doctor_profile:
        profile = user.doctor_profile.to_dict()
    elif user.role == 'patient' and user.patient_profile:
        profile = user.patient_profile.to_dict()

    return jsonify({
        'user': user.to_dict(),
        'profile': profile
    }), 200
