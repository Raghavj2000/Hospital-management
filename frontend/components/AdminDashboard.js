/**
 * Admin Dashboard Component
 * Complete admin interface with all management features
 */

const AdminDashboard = {
    template: `
        <div class="dashboard-container">
            <!-- Welcome Header -->
            <div class="dashboard-header">
                <h1>Welcome Admin</h1>
                <p class="welcome-text">Manage hospital operations from your dashboard</p>
            </div>

            <!-- Statistics Cards -->
            <div class="row mb-4">
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card primary">
                        <div class="stat-card-icon text-primary">
                            <i class="bi bi-people-fill"></i>
                        </div>
                        <div class="stat-card-title">Total Doctors</div>
                        <div class="stat-card-value">{{ stats.total_doctors }}</div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card success">
                        <div class="stat-card-icon text-success">
                            <i class="bi bi-person-check-fill"></i>
                        </div>
                        <div class="stat-card-title">Total Patients</div>
                        <div class="stat-card-value">{{ stats.total_patients }}</div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card info">
                        <div class="stat-card-icon text-info">
                            <i class="bi bi-calendar-check-fill"></i>
                        </div>
                        <div class="stat-card-title">Total Appointments</div>
                        <div class="stat-card-value">{{ stats.total_appointments }}</div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card warning">
                        <div class="stat-card-icon text-warning">
                            <i class="bi bi-building-fill"></i>
                        </div>
                        <div class="stat-card-title">Departments</div>
                        <div class="stat-card-value">{{ stats.total_departments }}</div>
                    </div>
                </div>
            </div>

            <!-- Tab Navigation -->
            <ul class="nav nav-tabs mb-4" role="tablist">
                <li class="nav-item">
                    <button class="nav-link" :class="{active: activeTab === 'doctors'}"
                            @click="activeTab = 'doctors'">
                        <i class="bi bi-person-badge"></i> Registered Doctors
                    </button>
                </li>
                <li class="nav-item">
                    <button class="nav-link" :class="{active: activeTab === 'patients'}"
                            @click="activeTab = 'patients'">
                        <i class="bi bi-people"></i> Registered Patients
                    </button>
                </li>
                <li class="nav-item">
                    <button class="nav-link" :class="{active: activeTab === 'appointments'}"
                            @click="activeTab = 'appointments'">
                        <i class="bi bi-calendar3"></i> Appointments
                    </button>
                </li>
                <li class="nav-item">
                    <button class="nav-link" :class="{active: activeTab === 'departments'}"
                            @click="activeTab = 'departments'">
                        <i class="bi bi-building"></i> Departments
                    </button>
                </li>
            </ul>

            <!-- Tab Content -->
            <div class="tab-content">
                <!-- Doctors Tab -->
                <div v-show="activeTab === 'doctors'">
                    <div class="data-table-container">
                        <div class="data-table-header">
                            <h3>Registered Doctors</h3>
                            <div class="table-actions">
                                <div class="search-box">
                                    <i class="bi bi-search"></i>
                                    <input type="text" class="form-control"
                                           v-model="searchQuery"
                                           placeholder="Search doctors...">
                                </div>
                                <button class="btn btn-primary" @click="showAddDoctorModal = true">
                                    <i class="bi bi-plus-circle"></i> Add Doctor
                                </button>
                            </div>
                        </div>

                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Department</th>
                                    <th>Qualification</th>
                                    <th>Experience</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="doctor in filteredDoctors" :key="doctor.id">
                                    <td>{{ doctor.full_name }}</td>
                                    <td>{{ doctor.department_name }}</td>
                                    <td>{{ doctor.qualification || 'N/A' }}</td>
                                    <td>{{ doctor.experience_years }} years</td>
                                    <td>
                                        <span class="badge" :class="doctor.is_available ? 'bg-success' : 'bg-secondary'">
                                            {{ doctor.is_available ? 'Available' : 'Unavailable' }}
                                        </span>
                                    </td>
                                    <td>
                                        <button class="btn btn-sm btn-info btn-action"
                                                @click="viewDoctorDetails(doctor)">
                                            Details
                                        </button>
                                        <button class="btn btn-sm btn-warning btn-action"
                                                @click="editDoctor(doctor)">
                                            Edit
                                        </button>
                                        <button class="btn btn-sm btn-danger btn-action"
                                                @click="blacklistDoctor(doctor)">
                                            Blacklist
                                        </button>
                                    </td>
                                </tr>
                                <tr v-if="doctors.length === 0">
                                    <td colspan="6" class="text-center">No doctors found</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Patients Tab -->
                <div v-show="activeTab === 'patients'">
                    <div class="data-table-container">
                        <div class="data-table-header">
                            <h3>Registered Patients</h3>
                            <div class="search-box">
                                <i class="bi bi-search"></i>
                                <input type="text" class="form-control"
                                       v-model="searchQuery"
                                       placeholder="Search patients...">
                            </div>
                        </div>

                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Phone</th>
                                    <th>Gender</th>
                                    <th>Blood Group</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="patient in filteredPatients" :key="patient.id">
                                    <td>{{ patient.full_name }}</td>
                                    <td>{{ patient.phone || 'N/A' }}</td>
                                    <td>{{ patient.gender || 'N/A' }}</td>
                                    <td>{{ patient.blood_group || 'N/A' }}</td>
                                    <td>
                                        <button class="btn btn-sm btn-info btn-action"
                                                @click="viewPatientHistory(patient)">
                                            History
                                        </button>
                                        <button class="btn btn-sm btn-danger btn-action"
                                                @click="blacklistPatient(patient)">
                                            Blacklist
                                        </button>
                                    </td>
                                </tr>
                                <tr v-if="patients.length === 0">
                                    <td colspan="5" class="text-center">No patients found</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Appointments Tab -->
                <div v-show="activeTab === 'appointments'">
                    <div class="data-table-container">
                        <div class="data-table-header">
                            <h3>Upcoming Appointments</h3>
                            <div class="table-actions">
                                <select class="form-select" v-model="appointmentFilter" @change="loadAppointments">
                                    <option value="">All Status</option>
                                    <option value="Booked">Booked</option>
                                    <option value="Completed">Completed</option>
                                    <option value="Cancelled">Cancelled</option>
                                </select>
                            </div>
                        </div>

                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Sr No</th>
                                    <th>Patient Name</th>
                                    <th>Doctor Name</th>
                                    <th>Department</th>
                                    <th>Date</th>
                                    <th>Time</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(apt, index) in appointments" :key="apt.id">
                                    <td>{{ index + 1 }}</td>
                                    <td>{{ apt.patient_name }}</td>
                                    <td>{{ apt.doctor_name }}</td>
                                    <td>{{ apt.department_name }}</td>
                                    <td>{{ formatDate(apt.appointment_date) }}</td>
                                    <td>{{ apt.appointment_time }}</td>
                                    <td>
                                        <span class="badge" :class="getStatusClass(apt.status)">
                                            {{ apt.status }}
                                        </span>
                                    </td>
                                </tr>
                                <tr v-if="appointments.length === 0">
                                    <td colspan="7" class="text-center">No appointments found</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Departments Tab -->
                <div v-show="activeTab === 'departments'">
                    <div class="data-table-container">
                        <div class="data-table-header">
                            <h3>Departments</h3>
                            <button class="btn btn-primary" @click="showAddDepartmentModal = true">
                                <i class="bi bi-plus-circle"></i> Add Department
                            </button>
                        </div>

                        <div class="row">
                            <div class="col-md-4 mb-3" v-for="dept in departments" :key="dept.id">
                                <div class="department-card">
                                    <h5>{{ dept.name }}</h5>
                                    <p>{{ dept.description }}</p>
                                    <div class="doctor-count">
                                        <i class="bi bi-people"></i> {{ dept.doctors_count }} Doctors
                                    </div>
                                    <div class="mt-3">
                                        <button class="btn btn-sm btn-outline-primary me-2"
                                                @click="editDepartment(dept)">
                                            Edit
                                        </button>
                                        <button class="btn btn-sm btn-outline-danger"
                                                @click="deleteDepartment(dept)">
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Add/Edit Doctor Modal -->
            <div class="modal" :class="{show: showAddDoctorModal, 'd-block': showAddDoctorModal}"
                 v-if="showAddDoctorModal" @click.self="closeDoctorModal">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">{{ editingDoctor ? 'Edit Doctor' : 'Add New Doctor' }}</h5>
                            <button type="button" class="btn-close" @click="closeDoctorModal"></button>
                        </div>
                        <div class="modal-body">
                            <form @submit.prevent="submitDoctor">
                                <div class="row">
                                    <div class="col-md-6 mb-3" v-if="!editingDoctor">
                                        <label class="form-label">Username</label>
                                        <input type="text" class="form-control"
                                               v-model="doctorForm.username" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Email</label>
                                        <input type="email" class="form-control"
                                               v-model="doctorForm.email" :required="!editingDoctor">
                                    </div>
                                    <div class="col-md-6 mb-3" v-if="!editingDoctor">
                                        <label class="form-label">Password</label>
                                        <input type="password" class="form-control"
                                               v-model="doctorForm.password" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Full Name</label>
                                        <input type="text" class="form-control"
                                               v-model="doctorForm.full_name" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Specialization/Department</label>
                                        <select class="form-select" v-model="doctorForm.department_id" required>
                                            <option value="">Select Department</option>
                                            <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                                                {{ dept.name }}
                                            </option>
                                        </select>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Contact</label>
                                        <input type="tel" class="form-control"
                                               v-model="doctorForm.phone">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Qualification</label>
                                        <input type="text" class="form-control"
                                               v-model="doctorForm.qualification">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Experience (years)</label>
                                        <input type="number" class="form-control"
                                               v-model="doctorForm.experience_years">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Consultation Fee</label>
                                        <input type="number" step="0.01" class="form-control"
                                               v-model="doctorForm.consultation_fee">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Status</label>
                                        <select class="form-select" v-model="doctorForm.is_available">
                                            <option :value="true">Available</option>
                                            <option :value="false">Unavailable</option>
                                        </select>
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-primary">
                                    {{ editingDoctor ? 'Update Doctor' : 'Create Doctor' }}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Add Department Modal -->
            <div class="modal" :class="{show: showAddDepartmentModal, 'd-block': showAddDepartmentModal}"
                 v-if="showAddDepartmentModal" @click.self="showAddDepartmentModal = false">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">{{ editingDepartment ? 'Edit' : 'Add' }} Department</h5>
                            <button type="button" class="btn-close" @click="closeDepModal()"></button>
                        </div>
                        <div class="modal-body">
                            <form @submit.prevent="submitDepartment">
                                <div class="mb-3">
                                    <label class="form-label">Department Name</label>
                                    <input type="text" class="form-control"
                                           v-model="departmentForm.name" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Description</label>
                                    <textarea class="form-control" rows="3"
                                              v-model="departmentForm.description"></textarea>
                                </div>
                                <button type="submit" class="btn btn-primary">
                                    {{ editingDepartment ? 'Update' : 'Create' }}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Patient History Modal -->
            <div class="modal" :class="{show: showPatientHistoryModal, 'd-block': showPatientHistoryModal}"
                 v-if="showPatientHistoryModal" @click.self="showPatientHistoryModal = false">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Patient History - {{ selectedPatient?.full_name }}</h5>
                            <button type="button" class="btn-close" @click="showPatientHistoryModal = false"></button>
                        </div>
                        <div class="modal-body">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Visit Date</th>
                                        <th>Doctor</th>
                                        <th>Diagnosis</th>
                                        <th>Prescription</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="apt in patientAppointments" :key="apt.id">
                                        <td>{{ formatDate(apt.appointment_date) }}</td>
                                        <td>{{ apt.doctor_name }}</td>
                                        <td>{{ apt.treatment?.diagnosis || 'N/A' }}</td>
                                        <td>{{ apt.treatment?.prescription || 'N/A' }}</td>
                                    </tr>
                                    <tr v-if="patientAppointments.length === 0">
                                        <td colspan="4" class="text-center">No history available</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal Backdrop -->
            <div class="modal-backdrop fade show" v-if="showAddDoctorModal || showAddDepartmentModal || showPatientHistoryModal"></div>
        </div>
    `,

    data() {
        return {
            activeTab: 'doctors',
            searchQuery: '',
            appointmentFilter: '',
            stats: {
                total_doctors: 0,
                total_patients: 0,
                total_appointments: 0,
                total_departments: 0
            },
            doctors: [],
            patients: [],
            appointments: [],
            departments: [],
            patientAppointments: [],
            selectedPatient: null,
            showAddDoctorModal: false,
            showAddDepartmentModal: false,
            showPatientHistoryModal: false,
            editingDoctor: null,
            editingDepartment: null,
            doctorForm: {
                username: '',
                email: '',
                password: '',
                full_name: '',
                phone: '',
                department_id: '',
                qualification: '',
                experience_years: 0,
                consultation_fee: 0,
                is_available: true
            },
            departmentForm: {
                name: '',
                description: ''
            }
        };
    },

    computed: {
        filteredDoctors() {
            if (!this.searchQuery) return this.doctors;
            const query = this.searchQuery.toLowerCase();
            return this.doctors.filter(d =>
                d.full_name.toLowerCase().includes(query) ||
                d.department_name?.toLowerCase().includes(query)
            );
        },

        filteredPatients() {
            if (!this.searchQuery) return this.patients;
            const query = this.searchQuery.toLowerCase();
            return this.patients.filter(p =>
                p.full_name.toLowerCase().includes(query) ||
                p.phone?.toLowerCase().includes(query)
            );
        }
    },

    mounted() {
        this.loadDashboard();
    },

    methods: {
        async loadDashboard() {
            try {
                this.$root.loading = true;

                const [dashboardRes, doctorsRes, patientsRes, deptsRes] = await Promise.all([
                    API.admin.getDashboard(),
                    API.admin.getDoctors(),
                    API.admin.getPatients(),
                    API.admin.getDepartments()
                ]);

                this.stats = dashboardRes.data;
                this.doctors = doctorsRes.data.doctors;
                this.patients = patientsRes.data.patients;
                this.departments = deptsRes.data.departments;

                await this.loadAppointments();

            } catch (error) {
                this.$root.showToast('Failed to load dashboard data', 'error');
            } finally {
                this.$root.loading = false;
            }
        },

        async loadAppointments() {
            try {
                const params = this.appointmentFilter ? { status: this.appointmentFilter } : {};
                const response = await API.admin.getAppointments(params);
                this.appointments = response.data.appointments;
            } catch (error) {
                this.$root.showToast('Failed to load appointments', 'error');
            }
        },

        async submitDoctor() {
            try {
                if (this.editingDoctor) {
                    // Update existing doctor
                    await API.admin.updateDoctor(this.editingDoctor.id, this.doctorForm);
                    this.$root.showToast('Doctor updated successfully', 'success');
                } else {
                    // Create new doctor
                    await API.admin.createDoctor(this.doctorForm);
                    this.$root.showToast('Doctor created successfully', 'success');
                }
                this.closeDoctorModal();
                await this.loadDashboard();
            } catch (error) {
                const message = error.response?.data?.error || 'Failed to save doctor';
                this.$root.showToast(message, 'error');
            }
        },

        editDoctor(doctor) {
            this.editingDoctor = doctor;
            this.doctorForm = {
                full_name: doctor.full_name,
                email: doctor.email || '',
                department_id: doctor.department_id,
                phone: doctor.phone || '',
                qualification: doctor.qualification || '',
                experience_years: doctor.experience_years || 0,
                consultation_fee: doctor.consultation_fee || 0,
                is_available: doctor.is_available
            };
            this.showAddDoctorModal = true;
        },

        closeDoctorModal() {
            this.showAddDoctorModal = false;
            this.editingDoctor = null;
            this.doctorForm = {
                username: '',
                email: '',
                password: '',
                full_name: '',
                phone: '',
                department_id: '',
                qualification: '',
                experience_years: 0,
                consultation_fee: 0,
                is_available: true
            };
        },

        async submitDepartment() {
            try {
                if (this.editingDepartment) {
                    await API.admin.updateDepartment(this.editingDepartment.id, this.departmentForm);
                    this.$root.showToast('Department updated successfully', 'success');
                } else {
                    await API.admin.createDepartment(this.departmentForm);
                    this.$root.showToast('Department created successfully', 'success');
                }
                this.closeDepModal();
                await this.loadDashboard();
            } catch (error) {
                const message = error.response?.data?.error || 'Failed to save department';
                this.$root.showToast(message, 'error');
            }
        },

        editDepartment(dept) {
            this.editingDepartment = dept;
            this.departmentForm = {
                name: dept.name,
                description: dept.description
            };
            this.showAddDepartmentModal = true;
        },

        closeDepModal() {
            this.showAddDepartmentModal = false;
            this.editingDepartment = null;
            this.departmentForm = { name: '', description: '' };
        },

        async deleteDepartment(dept) {
            if (!confirm(`Are you sure you want to delete ${dept.name}?`)) return;

            try {
                await API.admin.deleteDepartment(dept.id);
                this.$root.showToast('Department deleted successfully', 'success');
                await this.loadDashboard();
            } catch (error) {
                const message = error.response?.data?.error || 'Failed to delete department';
                this.$root.showToast(message, 'error');
            }
        },

        async blacklistDoctor(doctor) {
            if (!confirm(`Are you sure you want to blacklist ${doctor.full_name}?`)) return;

            try {
                await API.admin.deleteDoctor(doctor.id);
                this.$root.showToast('Doctor blacklisted successfully', 'success');
                await this.loadDashboard();
            } catch (error) {
                const message = error.response?.data?.error || 'Failed to blacklist doctor';
                this.$root.showToast(message, 'error');
            }
        },

        async blacklistPatient(patient) {
            if (!confirm(`Are you sure you want to blacklist ${patient.full_name}?`)) return;

            try {
                await API.admin.blacklistPatient(patient.id);
                this.$root.showToast('Patient blacklisted successfully', 'success');
                await this.loadDashboard();
            } catch (error) {
                const message = error.response?.data?.error || 'Failed to blacklist patient';
                this.$root.showToast(message, 'error');
            }
        },

        async viewPatientHistory(patient) {
            try {
                this.selectedPatient = patient;
                const response = await API.admin.getAppointments({ patient_id: patient.id });
                this.patientAppointments = response.data.appointments;
                this.showPatientHistoryModal = true;
            } catch (error) {
                this.$root.showToast('Failed to load patient history', 'error');
            }
        },

        viewDoctorDetails(doctor) {
            alert(`Doctor Details:\n\nName: ${doctor.full_name}\nDepartment: ${doctor.department_name}\nQualification: ${doctor.qualification}\nExperience: ${doctor.experience_years} years\nPhone: ${doctor.phone}`);
        },

        formatDate(dateStr) {
            return new Date(dateStr).toLocaleDateString();
        },

        getStatusClass(status) {
            const classes = {
                'Booked': 'badge-booked',
                'Completed': 'badge-completed',
                'Cancelled': 'badge-cancelled'
            };
            return classes[status] || '';
        }
    }
};
