# Hospital Management System

A complete web-based Hospital Management System with role-based access control for Admin, Doctors, and Patients.

![Status](https://img.shields.io/badge/Status-Complete-success)
![Backend](https://img.shields.io/badge/Backend-Flask-blue)
![Frontend](https://img.shields.io/badge/Frontend-Vue.js%203-green)
![Database](https://img.shields.io/badge/Database-SQLite-orange)

---

## Overview

This project is a comprehensive hospital management solution built as part of the IIT Madras BS Degree Program - Modern Application Development course (MAD-2).

### Key Features

- **3 User Roles**: Admin, Doctor, Patient with distinct interfaces
- **50+ API Endpoints**: RESTful API with Flask
- **Complete CRUD**: All operations for doctors, patients, appointments, departments
- **JWT Authentication**: Secure token-based authentication
- **Real-time Data**: Live updates across all dashboards
- **Responsive Design**: Works on desktop and mobile

---

## Quick Start

### Prerequisites

- Python 3.8+
- Redis (optional but recommended)
- Modern web browser

### Installation Steps

```bash
# 1. Navigate to project directory
cd "hospital managment"

# 2. Install backend dependencies
cd backend
pip install -r requirements.txt

# 3. Start Redis (optional)
redis-server

# 4. Start backend server
python run.py

# 5. Add sample data (optional)
python init_sample_data.py

# 6. Open frontend
# Open: frontend/templates/index.html in browser
```

### Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Doctor | dr_heart | doctor123 |
| Patient | patient1 | patient123 |

---

## Project Structure

```
hospital managment/
│
├── backend/                     # Flask REST API
│   ├── app/
│   │   ├── models/             # Database models (7 files)
│   │   ├── routes/             # API endpoints (4 files)
│   │   └── utils/              # Utilities (3 files)
│   ├── config/                 # Configuration
│   ├── run.py                  # Start server
│   └── requirements.txt        # Dependencies
│
├── frontend/                    # Vue.js Frontend
│   ├── templates/
│   │   └── index.html          # Entry point
│   ├── components/             # Vue components (5 files)
│   │   ├── AuthComponent.js    # Login/Register
│   │   ├── NavbarComponent.js  # Navigation
│   │   ├── AdminDashboard.js   # Admin interface
│   │   ├── DoctorDashboard.js  # Doctor interface
│   │   └── PatientDashboard.js # Patient interface
│   └── static/
│       ├── css/style.css       # Custom styles
│       └── js/
│           ├── api.js          # API service
│           └── app.js          # Main app
│
└── README.md                   # This file
```

---

## Features

### Admin Features

- Dashboard with statistics
- Manage departments (CRUD)
- Manage doctors (create, edit, blacklist)
- Manage patients (view, history, blacklist)
- View all appointments
- Search doctors and patients

### Doctor Features

- Dashboard with appointments
- View assigned patients
- Complete appointments with diagnoses
- Set availability schedule
- View patient medical history
- Update treatment records

### Patient Features

- Browse departments and doctors
- Book appointments with time slots
- View appointment history
- View treatment records
- Update profile
- Cancel/reschedule appointments

---

## Technology Stack

### Backend

- **Framework**: Flask 3.0.0
- **Database**: SQLite
- **ORM**: SQLAlchemy 3.1.1
- **Auth**: JWT (Flask-JWT-Extended 4.6.0)
- **Cache**: Redis 5.0.1
- **Security**: Bcrypt 1.0.1

### Frontend

- **Framework**: Vue.js 3 (CDN)
- **CSS**: Bootstrap 5.3.0
- **Icons**: Bootstrap Icons
- **HTTP**: Axios
- **Template**: Jinja2 (entry point)

---

## Backend API

### Base URL

```
http://localhost:5000/api
```

### Authentication

All endpoints (except registration and login) require JWT authentication:

```
Authorization: Bearer <your-access-token>
```

### Main Endpoints

#### Authentication (`/api/auth`)

- `POST /auth/register` - Register new patient
- `POST /auth/login` - Login (all roles)
- `GET /auth/me` - Get current user
- `POST /auth/refresh` - Refresh token

#### Admin (`/api/admin`)

- `GET /admin/dashboard` - Get statistics
- `GET /admin/departments` - List departments
- `POST /admin/departments` - Create department
- `PUT /admin/departments/{id}` - Update department
- `DELETE /admin/departments/{id}` - Delete department
- `GET /admin/doctors` - List doctors
- `POST /admin/doctors` - Create doctor
- `PUT /admin/doctors/{id}` - Update doctor
- `DELETE /admin/doctors/{id}` - Delete doctor
- `GET /admin/patients` - List patients
- `POST /admin/patients/{id}/blacklist` - Blacklist patient
- `GET /admin/appointments` - List appointments
- `GET /admin/search/doctors?q=query` - Search doctors
- `GET /admin/search/patients?q=query` - Search patients

#### Doctor (`/api/doctor`)

- `GET /doctor/dashboard` - Get statistics
- `GET /doctor/appointments` - List appointments
- `POST /doctor/appointments/{id}/complete` - Complete appointment
- `POST /doctor/appointments/{id}/cancel` - Cancel appointment
- `GET /doctor/patients` - List patients
- `GET /doctor/patients/{id}/history` - Get patient history
- `GET /doctor/availability` - Get availability
- `POST /doctor/availability` - Set availability
- `DELETE /doctor/availability/{id}` - Delete availability
- `GET /doctor/profile` - Get profile
- `PUT /doctor/profile` - Update profile

#### Patient (`/api/patient`)

- `GET /patient/dashboard` - Get dashboard
- `GET /patient/departments` - List departments
- `GET /patient/departments/{id}/doctors` - Get department doctors
- `GET /patient/doctors` - List all doctors
- `GET /patient/doctors/{id}` - Get doctor details
- `GET /patient/search/doctors?q=query` - Search doctors
- `GET /patient/appointments` - List appointments
- `POST /patient/appointments` - Book appointment
- `PUT /patient/appointments/{id}/reschedule` - Reschedule appointment
- `POST /patient/appointments/{id}/cancel` - Cancel appointment
- `GET /patient/treatments` - Get treatment history
- `GET /patient/profile` - Get profile
- `PUT /patient/profile` - Update profile

---

## Frontend Guide

### Architecture

The frontend uses **Vue.js 3 via CDN** - a lightweight, no-build approach:

- Vue loaded directly from CDN in index.html
- Components defined as plain JavaScript objects
- No webpack, npm, or build tools required
- Just copy files and they work

### Components

1. **AuthComponent.js** (11 KB)
   - Login and registration forms
   - JWT token management
   - Form validation

2. **NavbarComponent.js** (3 KB)
   - Top navigation bar
   - User info display
   - Logout functionality

3. **AdminDashboard.js** (32 KB)
   - Full admin interface
   - Department management
   - Doctor and patient management
   - Appointment viewing
   - Search functionality

4. **DoctorDashboard.js** (23 KB)
   - Appointment management
   - Patient history
   - Availability calendar
   - Treatment completion

5. **PatientDashboard.js** (30 KB)
   - Department browsing
   - Doctor search
   - Appointment booking
   - Medical history viewing

### API Service

The `api.js` file provides organized API access:

```javascript
// Authentication
API.auth.login({ username, password })
API.auth.register({ ... })

// Admin operations
API.admin.getDashboard()
API.admin.getDoctors()
API.admin.createDoctor(data)

// Doctor operations
API.doctor.getAppointments()
API.doctor.completeAppointment(id, data)

// Patient operations
API.patient.getDepartments()
API.patient.bookAppointment(data)
```

### Configuration

Update API base URL in `frontend/static/js/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

---

## Database Schema

### Tables

1. **users** - Base user accounts (all roles)
2. **departments** - Medical departments/specializations
3. **doctors** - Doctor profiles and information
4. **doctor_availability** - Doctor time slots
5. **patients** - Patient profiles and medical info
6. **appointments** - Appointment bookings
7. **treatments** - Medical records and diagnoses

---

## Testing

### Backend Testing

```bash
cd backend
python test_api.py
```

### Manual Testing

1. Start backend: `python run.py`
2. Open frontend: `frontend/templates/index.html`
3. Login as admin/doctor/patient
4. Test all CRUD operations
5. Verify data persistence
6. Check role-based access

---

## Security Features

- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- Account blacklisting
- Input validation
- SQL injection prevention
- CORS configuration

---

## Performance

- Redis caching layer
- Efficient database queries
- Lazy loading
- Optimized API responses
- CDN resources
- Minimal dependencies

---

## Troubleshooting

### Backend won't start

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Can't login

- Verify backend is running on port 5000
- Use default admin credentials
- Clear browser cache

### CORS errors

- Ensure Flask-CORS is installed
- Restart backend server
- Check API_BASE_URL in frontend

### Database errors

```bash
cd backend
rm hospital.db
python run.py
```

### Redis connection failed

The application will work without Redis, but caching features will be disabled. To fix:

```bash
# Start Redis server
redis-server

# Or install Redis:
# Ubuntu/Debian: sudo apt-get install redis-server
# Mac: brew install redis
```

---

## Project Statistics

| Metric | Count |
|--------|-------|
| Total Files | 40+ |
| Python Files | 20 |
| JavaScript Files | 7 |
| Database Tables | 7 |
| API Endpoints | 55+ |
| Vue Components | 5 |
| Lines of Code | 6,000+ |

---

## Academic Information

**Course**: Modern Application Development - 2 (MAD-2)
**Program**: IIT Madras BS Degree
**Term**: January 2025
**Project**: Hospital Management System V2

---

## Known Limitations

- Backend jobs (reminders, reports, CSV export) not implemented as instructed
- Reschedule feature uses cancel + rebook flow
- Demo credentials shown on login page

---

## License

This project is for educational purposes as part of the IIT Madras BS Degree Program.

---

## Project Status

**Status**: Complete
**Version**: 1.0
**Last Updated**: January 2025
**Ready for**: Submission & Presentation

---

Built with care for Modern Application Development Course
