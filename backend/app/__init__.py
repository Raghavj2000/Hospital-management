from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from redis import Redis
from config.config import config

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
redis_client = None
celery = None

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    # Initialize Redis
    global redis_client
    try:
        redis_client = Redis.from_url(app.config['REDIS_URL'], decode_responses=True)
        redis_client.ping()
        print("Redis connected successfully")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        redis_client = None

    # Initialize Celery
    global celery
    from app.celery_app import make_celery
    celery = make_celery(app)

    # Register blueprints
    from app.routes import auth, admin, doctor, patient
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(doctor.bp)
    app.register_blueprint(patient.bp)

    # Create database tables
    with app.app_context():
        db.create_all()
        # Create default admin user
        from app.models.user import User
        admin_exists = User.query.filter_by(role='admin').first()
        if not admin_exists:
            admin_user = User(
                username='admin',
                email='admin@hospital.com',
                role='admin',
                is_active=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: username='admin', password='admin123'")

    return app
