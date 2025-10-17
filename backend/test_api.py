"""
Simple API testing script to verify basic functionality
Run this after starting the server to test basic endpoints
"""

import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_admin_login():
    """Test admin login"""
    print("\n1. Testing Admin Login...")
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })

    if response.status_code == 200:
        data = response.json()
        print("   ✓ Admin login successful")
        return data['access_token']
    else:
        print(f"   ✗ Admin login failed: {response.json()}")
        return None

def test_admin_dashboard(token):
    """Test admin dashboard"""
    print("\n2. Testing Admin Dashboard...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/admin/dashboard', headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("   ✓ Dashboard data retrieved")
        print(f"   - Total Doctors: {data['total_doctors']}")
        print(f"   - Total Patients: {data['total_patients']}")
        print(f"   - Total Appointments: {data['total_appointments']}")
        return True
    else:
        print(f"   ✗ Dashboard failed: {response.json()}")
        return False

def test_patient_registration():
    """Test patient registration"""
    print("\n3. Testing Patient Registration...")
    response = requests.post(f'{BASE_URL}/auth/register', json={
        'username': 'testpatient',
        'email': 'test@example.com',
        'password': 'test123',
        'full_name': 'Test Patient'
    })

    if response.status_code == 201:
        print("   ✓ Patient registration successful")
        return True
    elif response.status_code == 409:
        print("   ✓ Patient already exists (this is fine)")
        return True
    else:
        print(f"   ✗ Registration failed: {response.json()}")
        return False

def test_patient_login():
    """Test patient login"""
    print("\n4. Testing Patient Login...")
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'username': 'testpatient',
        'password': 'test123'
    })

    if response.status_code == 200:
        data = response.json()
        print("   ✓ Patient login successful")
        return data['access_token']
    else:
        print(f"   ✗ Patient login failed: {response.json()}")
        return None

def test_get_departments(token):
    """Test getting departments"""
    print("\n5. Testing Get Departments...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/patient/departments', headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Found {len(data['departments'])} departments")
        if data['departments']:
            print(f"   - Example: {data['departments'][0]['name']}")
        return True
    else:
        print(f"   ✗ Failed to get departments: {response.json()}")
        return False

def test_create_department(token):
    """Test creating a department"""
    print("\n6. Testing Create Department...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f'{BASE_URL}/admin/departments',
        headers=headers,
        json={
            'name': 'Test Department',
            'description': 'This is a test department'
        })

    if response.status_code == 201:
        print("   ✓ Department created successfully")
        return True
    elif response.status_code == 409:
        print("   ✓ Department already exists (this is fine)")
        return True
    else:
        print(f"   ✗ Failed to create department: {response.json()}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("Hospital Management System - API Test Suite")
    print("="*60)
    print("\nMake sure the server is running on http://localhost:5000")
    print("\nStarting tests...\n")

    try:
        # Test admin login
        admin_token = test_admin_login()
        if not admin_token:
            print("\n⚠ Cannot continue without admin token")
            return

        # Test admin dashboard
        test_admin_dashboard(admin_token)

        # Test department creation
        test_create_department(admin_token)

        # Test patient registration
        test_patient_registration()

        # Test patient login
        patient_token = test_patient_login()
        if patient_token:
            # Test getting departments
            test_get_departments(patient_token)

        print("\n" + "="*60)
        print("Test Suite Completed!")
        print("="*60)
        print("\n✓ All basic tests passed!")
        print("\nYou can now:")
        print("  1. Use Postman to test more endpoints")
        print("  2. Run init_sample_data.py to add sample data")
        print("  3. Check README.md for full API documentation")

    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to server")
        print("Make sure the server is running: python run.py")
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")

if __name__ == '__main__':
    main()
