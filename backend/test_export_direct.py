"""
Test script for CSV export functionality - Direct function call
Tests export without Celery
"""
from app import create_app, db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.treatment import Treatment
from datetime import datetime
import csv
import io
import os

# Create Flask app context
app = create_app()

with app.app_context():
    print("Testing CSV Export (Direct Function Call)...")
    print("=" * 80)

    # Get first patient
    patient = Patient.query.first()

    if not patient:
        print("No patients found in database. Please create a patient first.")
    else:
        print(f"Testing export for patient: {patient.full_name} (ID: {patient.id})")
        print("-" * 80)

        # Get all appointments with treatments for this patient
        appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(
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

        # Save to file
        export_dir = os.path.join(os.path.dirname(__file__), 'exports')
        os.makedirs(export_dir, exist_ok=True)

        export_path = os.path.join(export_dir, f"treatment_history_{patient.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            f.write(csv_content)

        print(f"\n[SUCCESS] Export completed successfully!")
        print(f"[SUCCESS] Records exported: {len(appointments)}")
        print(f"[SUCCESS] File saved to: {export_path}")

        # Show first few lines
        print("\nPreview of exported data:")
        print("-" * 80)
        lines = csv_content.split('\n')
        for line in lines[:5]:  # Show first 5 lines
            print(line)
        if len(lines) > 5:
            print(f"... and {len(lines) - 5} more lines")

        print("=" * 80)
