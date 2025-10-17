/**
 * API Service Layer for Hospital Management System
 * Handles all HTTP requests to the backend API
 */

const API_BASE_URL = 'http://localhost:5000/api';

// Axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
    config => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => Promise.reject(error)
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.location.reload();
        }
        return Promise.reject(error);
    }
);

// API Service Object
const API = {
    // ============ Authentication ============
    auth: {
        login: (credentials) =>
            apiClient.post('/auth/login', credentials),

        register: (userData) =>
            apiClient.post('/auth/register', userData),

        getCurrentUser: () =>
            apiClient.get('/auth/me'),

        refreshToken: () =>
            apiClient.post('/auth/refresh')
    },

    // ============ Admin APIs ============
    admin: {
        getDashboard: () =>
            apiClient.get('/admin/dashboard'),

        // Departments
        getDepartments: () =>
            apiClient.get('/admin/departments'),

        createDepartment: (data) =>
            apiClient.post('/admin/departments', data),

        updateDepartment: (id, data) =>
            apiClient.put(`/admin/departments/${id}`, data),

        deleteDepartment: (id) =>
            apiClient.delete(`/admin/departments/${id}`),

        // Doctors
        getDoctors: (params) =>
            apiClient.get('/admin/doctors', { params }),

        getDoctor: (id) =>
            apiClient.get(`/admin/doctors/${id}`),

        createDoctor: (data) =>
            apiClient.post('/admin/doctors', data),

        updateDoctor: (id, data) =>
            apiClient.put(`/admin/doctors/${id}`, data),

        deleteDoctor: (id) =>
            apiClient.delete(`/admin/doctors/${id}`),

        // Patients
        getPatients: () =>
            apiClient.get('/admin/patients'),

        getPatient: (id) =>
            apiClient.get(`/admin/patients/${id}`),

        updatePatient: (id, data) =>
            apiClient.put(`/admin/patients/${id}`, data),

        blacklistPatient: (id) =>
            apiClient.post(`/admin/patients/${id}/blacklist`),

        // Appointments
        getAppointments: (params) =>
            apiClient.get('/admin/appointments', { params }),

        // Search
        searchDoctors: (query) =>
            apiClient.get('/admin/search/doctors', { params: { q: query } }),

        searchPatients: (query) =>
            apiClient.get('/admin/search/patients', { params: { q: query } })
    },

    // ============ Doctor APIs ============
    doctor: {
        getDashboard: () =>
            apiClient.get('/doctor/dashboard'),

        // Appointments
        getAppointments: (params) =>
            apiClient.get('/doctor/appointments', { params }),

        getAppointment: (id) =>
            apiClient.get(`/doctor/appointments/${id}`),

        completeAppointment: (id, data) =>
            apiClient.post(`/doctor/appointments/${id}/complete`, data),

        cancelAppointment: (id) =>
            apiClient.post(`/doctor/appointments/${id}/cancel`),

        // Patients
        getPatients: () =>
            apiClient.get('/doctor/patients'),

        getPatientHistory: (patientId) =>
            apiClient.get(`/doctor/patients/${patientId}/history`),

        updatePatientTreatment: (patientId, data) =>
            apiClient.post(`/doctor/patients/${patientId}/treatment`, data),

        // Availability
        getAvailability: () =>
            apiClient.get('/doctor/availability'),

        setAvailability: (data) =>
            apiClient.post('/doctor/availability', data),

        deleteAvailability: (id) =>
            apiClient.delete(`/doctor/availability/${id}`),

        // Profile
        getProfile: () =>
            apiClient.get('/doctor/profile'),

        updateProfile: (data) =>
            apiClient.put('/doctor/profile', data)
    },

    // ============ Patient APIs ============
    patient: {
        getDashboard: () =>
            apiClient.get('/patient/dashboard'),

        // Departments & Doctors
        getDepartments: () =>
            apiClient.get('/patient/departments'),

        getDepartmentDoctors: (deptId) =>
            apiClient.get(`/patient/departments/${deptId}/doctors`),

        getDoctors: (params) =>
            apiClient.get('/patient/doctors', { params }),

        getDoctor: (id) =>
            apiClient.get(`/patient/doctors/${id}`),

        searchDoctors: (query) =>
            apiClient.get('/patient/search/doctors', { params: { q: query } }),

        // Appointments
        getAppointments: (params) =>
            apiClient.get('/patient/appointments', { params }),

        getAppointment: (id) =>
            apiClient.get(`/patient/appointments/${id}`),

        bookAppointment: (data) =>
            apiClient.post('/patient/appointments', data),

        rescheduleAppointment: (id, data) =>
            apiClient.put(`/patient/appointments/${id}/reschedule`, data),

        cancelAppointment: (id) =>
            apiClient.post(`/patient/appointments/${id}/cancel`),

        // Treatments
        getTreatments: () =>
            apiClient.get('/patient/treatments'),

        getTreatment: (id) =>
            apiClient.get(`/patient/treatments/${id}`),

        // Profile
        getProfile: () =>
            apiClient.get('/patient/profile'),

        updateProfile: (data) =>
            apiClient.put('/patient/profile', data),

        // Export
        exportTreatments: () =>
            apiClient.post('/patient/export/treatments'),

        getExportStatus: (taskId) =>
            apiClient.get(`/patient/export/status/${taskId}`)
    }
};
