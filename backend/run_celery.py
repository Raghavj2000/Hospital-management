"""
Script to run Celery worker and beat scheduler
"""
from app import create_app, celery

# Create Flask app to initialize Celery
flask_app = create_app()

if __name__ == '__main__':
    print("Starting Celery worker with beat scheduler...")
    print("Celery tasks available:")
    print("  - app.tasks.send_daily_reminders (scheduled: daily at 8 AM)")
    print("  - app.tasks.send_monthly_reports (scheduled: 1st of month at 9 AM)")
    print("  - app.tasks.export_patient_treatments (async)")
    print("\nTo run worker: celery -A run_celery.celery worker --loglevel=info --pool=solo")
    print("To run beat: celery -A run_celery.celery beat --loglevel=info")
    print("To run both: celery -A run_celery.celery worker --beat --loglevel=info --pool=solo")
