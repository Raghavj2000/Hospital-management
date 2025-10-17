"""
Celery configuration and initialization
"""
from celery import Celery
from celery.schedules import crontab


def make_celery(app):
    """Create Celery instance and configure it from Flask app"""
    celery = Celery(
        app.import_name,
        backend='redis://localhost:6379/1',
        broker='redis://localhost:6379/0'
    )

    celery.conf.update(app.config)
    celery.conf.timezone = 'UTC'

    # Configure periodic tasks
    celery.conf.beat_schedule = {
        'send-daily-reminders': {
            'task': 'app.tasks.send_daily_reminders',
            'schedule': crontab(hour=8, minute=0),  # Run every day at 8 AM
        },
        'send-monthly-reports': {
            'task': 'app.tasks.send_monthly_reports',
            'schedule': crontab(day_of_month=1, hour=9, minute=0),  # Run on 1st of every month at 9 AM
        },
    }

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
