"""
Celery tasks for background jobs
"""
from datetime import datetime, timedelta
from celery import shared_task
from app.models import Appointment, Doctor, Patient, Treatment, User
from app import db
import csv
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import os


# Email configuration - Use environment variables for production
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('SMTP_USERNAME', 'projectaaron11@gmail.com')
EMAIL_PASSWORD = os.getenv('SMTP_PASSWORD', 'xypc lhco tpoq bvza')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'hospitalmanagement913@gmail.com')


def send_email(to_email, subject, html_content, attachment=None, attachment_name=None):
    """
    Send email with optional attachment
    """
    try:        
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        if attachment and attachment_name:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={attachment_name}')
            msg.attach(part)

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


@shared_task(name='app.tasks.send_daily_reminders')
def send_daily_reminders():
    """
    Daily job to send appointment reminders
    Runs every day at 8 AM
    """
    try:
        today = datetime.now().date()

        # Get all appointments scheduled for today with status 'Booked'
        appointments = Appointment.query.filter(
            Appointment.appointment_date == today,
            Appointment.status == 'Booked'
        ).all()

        sent_count = 0
        for apt in appointments:
            patient = Patient.query.get(apt.patient_id)
            doctor = Doctor.query.get(apt.doctor_id)

            if not patient or not doctor:
                continue

            patient_user = User.query.get(patient.user_id)
            if not patient_user or not patient_user.email:
                continue

            # Create reminder email
            subject = f"Appointment Reminder - {apt.appointment_date}"
            html_content = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                        .content {{ padding: 20px; background-color: #f8f9fa; }}
                        .info {{ background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🏥 Appointment Reminder</h1>
                        </div>
                        <div class="content">
                            <p>Dear {patient.full_name},</p>
                            <p>This is a friendly reminder about your appointment scheduled for today.</p>

                            <div class="info">
                                <h3>Appointment Details:</h3>
                                <p><strong>Doctor:</strong> {doctor.full_name}</p>
                                <p><strong>Department:</strong> {doctor.department.name if doctor.department else 'N/A'}</p>
                                <p><strong>Date:</strong> {apt.appointment_date.strftime('%B %d, %Y')}</p>
                                <p><strong>Time:</strong> {apt.appointment_time}</p>
                            </div>

                            <p>Please arrive 10 minutes before your scheduled time.</p>
                            <p>If you need to reschedule, please contact us as soon as possible.</p>
                        </div>
                        <div class="footer">
                            <p>Hospital Management System</p>
                            <p>This is an automated message, please do not reply.</p>
                        </div>
                    </div>
                </body>
            </html>
            """

            if send_email(patient_user.email, subject, html_content):
                sent_count += 1

        print(f"Daily reminders sent: {sent_count} reminders for {len(appointments)} appointments")
        return {'status': 'success', 'sent': sent_count, 'total': len(appointments)}

    except Exception as e:
        print(f"Error in send_daily_reminders: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task(name='app.tasks.send_monthly_reports')
def send_monthly_reports():
    """
    Monthly job to send activity reports to doctors
    Runs on the 1st of every month at 9 AM
    """
    try:
        # Get last month's date range
        today = datetime.now()
        first_day_current_month = today.replace(day=1)
        last_day_prev_month = first_day_current_month - timedelta(days=1)
        first_day_prev_month = last_day_prev_month.replace(day=1)

        month_name = last_day_prev_month.strftime('%B %Y')

        # Get all active doctors
        doctors = Doctor.query.filter_by(is_available=True).all()

        sent_count = 0
        for doctor in doctors:
            # Get appointments for this doctor in the last month
            appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date >= first_day_prev_month.date(),
                Appointment.appointment_date <= last_day_prev_month.date()
            ).all()

            if not appointments:
                continue  # Skip if no appointments

            doctor_user = User.query.get(doctor.user_id)
            if not doctor_user or not doctor_user.email:
                continue

            # Calculate statistics
            total_appointments = len(appointments)
            completed = len([a for a in appointments if a.status == 'Completed'])
            cancelled = len([a for a in appointments if a.status == 'Cancelled'])

            # Generate appointment details HTML
            appointment_rows = ""
            for apt in appointments:
                patient = Patient.query.get(apt.patient_id)
                treatment = Treatment.query.filter_by(appointment_id=apt.id).first()

                appointment_rows += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{apt.appointment_date.strftime('%d/%m/%Y')}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{patient.full_name if patient else 'N/A'}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{apt.status}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{treatment.diagnosis if treatment else 'N/A'}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{treatment.prescription if treatment else 'N/A'}</td>
                </tr>
                """

            # Create report email
            subject = f"Monthly Activity Report - {month_name}"
            html_content = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
                        .content {{ padding: 20px; background-color: #f8f9fa; }}
                        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                        .stat-box {{ background-color: white; padding: 20px; border-radius: 5px; text-align: center; flex: 1; margin: 0 10px; }}
                        .stat-number {{ font-size: 36px; font-weight: bold; color: #007bff; }}
                        table {{ width: 100%; border-collapse: collapse; background-color: white; margin: 20px 0; }}
                        th {{ background-color: #007bff; color: white; padding: 12px; text-align: left; }}
                        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>📊 Monthly Activity Report</h1>
                            <h2>{month_name}</h2>
                        </div>
                        <div class="content">
                            <p>Dear Dr. {doctor.full_name},</p>
                            <p>Here is your activity summary for {month_name}:</p>

                            <div class="stats">
                                <div class="stat-box">
                                    <div class="stat-number">{total_appointments}</div>
                                    <div>Total Appointments</div>
                                </div>
                                <div class="stat-box">
                                    <div class="stat-number">{completed}</div>
                                    <div>Completed</div>
                                </div>
                                <div class="stat-box">
                                    <div class="stat-number">{cancelled}</div>
                                    <div>Cancelled</div>
                                </div>
                            </div>

                            <h3>Appointment Details:</h3>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Patient</th>
                                        <th>Status</th>
                                        <th>Diagnosis</th>
                                        <th>Treatment</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {appointment_rows}
                                </tbody>
                            </table>
                        </div>
                        <div class="footer">
                            <p>Hospital Management System</p>
                            <p>This is an automated monthly report.</p>
                        </div>
                    </div>
                </body>
            </html>
            """

            if send_email(doctor_user.email, subject, html_content):
                sent_count += 1

        print(f"Monthly reports sent: {sent_count} reports to {len(doctors)} doctors")
        return {'status': 'success', 'sent': sent_count, 'total': len(doctors)}

    except Exception as e:
        print(f"Error in send_monthly_reports: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task(name='app.tasks.export_patient_treatments')
def export_patient_treatments(patient_id):
    """
    Async job to export patient treatment history as CSV
    Triggered by user action
    """
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return {'status': 'error', 'message': 'Patient not found'}

        patient_user = User.query.get(patient.user_id)

        # Get all appointments with treatments for this patient
        appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(
            Appointment.appointment_date.desc()
        ).all()

        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Appointment ID',
            'Patient ID',
            'Patient Name',
            'Doctor Name',
            'Department',
            'Appointment Date',
            'Appointment Time',
            'Status',
            'Diagnosis',
            'Treatment/Prescription',
            'Notes',
            'Next Visit Date'
        ])

        # Write data rows
        for apt in appointments:
            doctor = Doctor.query.get(apt.doctor_id)
            treatment = Treatment.query.filter_by(appointment_id=apt.id).first()

            writer.writerow([
                apt.id,
                patient.id,
                patient.full_name,
                doctor.full_name if doctor else 'N/A',
                doctor.department.name if doctor and doctor.department else 'N/A',
                apt.appointment_date.strftime('%Y-%m-%d'),
                apt.appointment_time,
                apt.status,
                treatment.diagnosis if treatment else 'N/A',
                treatment.prescription if treatment else 'N/A',
                treatment.notes if treatment else 'N/A',
                treatment.next_visit_date.strftime('%Y-%m-%d') if treatment and treatment.next_visit_date else 'N/A'
            ])

        csv_content = output.getvalue()
        output.close()

        # Send email with CSV attachment
        if patient_user and patient_user.email:
            subject = "Treatment History Export"
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Treatment History Export</h2>
                    <p>Dear {patient.full_name},</p>
                    <p>Your treatment history export is ready!</p>
                    <p>Please find attached the CSV file containing all your treatment records.</p>
                    <p><strong>Total Records:</strong> {len(appointments)}</p>
                    <p>Thank you for using our Hospital Management System.</p>
                    <hr>
                    <p style="font-size: 12px; color: #666;">This is an automated message.</p>
                </body>
            </html>
            """

            filename = f"treatment_history_{patient_id}_{datetime.now().strftime('%Y%m%d')}.csv"
            send_email(patient_user.email, subject, html_content, csv_content.encode(), filename)

        # Also save to temporary location for download
        export_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')
        os.makedirs(export_dir, exist_ok=True)

        export_path = os.path.join(export_dir, f"treatment_history_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            f.write(csv_content)

        return {
            'status': 'success',
            'message': 'Export completed successfully',
            'records': len(appointments),
            'file_path': export_path
        }

    except Exception as e:
        print(f"Error in export_patient_treatments: {str(e)}")
        return {'status': 'error', 'message': str(e)}
