"""
Celery configuration and initialization
"""
from celery import Celery
from celery.schedules import crontab
from config.config import config
from app import create_app

flask_app = create_app()

def make_celery(flask_app):
    """Create Celery instance and configure it from Flask app"""
    celery = Celery(
        flask_app.import_name,
        backend='redis://localhost:6379/0',
        broker='redis://localhost:6379/0'
    )

    celery.conf.update(flask_app.config)
    celery.conf.timezone = 'Asia/Kolkata'

    # Import tasks to ensure they are registered
    import app.tasks

    # Configure periodic tasks
    celery.conf.beat_schedule = {
        'send-daily-reminders': {
            'task': 'app.tasks.send_daily_reminders',
            'schedule': crontab(hour=00, minute=55),
        },
        'send-monthly-reports': {
            'task': 'app.tasks.send_monthly_reports',
            'schedule': crontab(day_of_month=30, hour=00, minute=55),
        },
    }

    class ContextTask(celery.Task):
        """Custom Celery Task to use Flask app context"""
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():  # Use the Flask app instance
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(flask_app)