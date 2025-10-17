"""
Test script for CSV export functionality
Tests the export_patient_treatments task directly
"""
from app import create_app, db
from app.tasks import export_patient_treatments
from app.models import Patient

# Create Flask app context
app = create_app()

with app.app_context():
    print("Testing CSV Export...")
    print("=" * 80)

    # Get first patient
    patient = Patient.query.first()

    if not patient:
        print("No patients found in database. Please create a patient first.")
    else:
        print(f"Testing export for patient: {patient.full_name} (ID: {patient.id})")
        print("-" * 80)

        # Run export task directly (not async)
        result = export_patient_treatments(patient.id)

        print("\nExport Result:")
        print(f"Status: {result['status']}")
        print(f"Message: {result.get('message', 'N/A')}")

        if result['status'] == 'success':
            print(f"Records exported: {result['records']}")
            print(f"File saved to: {result['file_path']}")
            print("\nExport completed successfully!")
        else:
            print(f"\nExport failed!")

        print("=" * 80)
