/**
 * Patient Dashboard Component
 * Complete patient interface matching wireframe
 */

const PatientDashboard = {
    template: `
        <div class="dashboard-container">

            <!-- Statistics Cards -->
            <div class="row mb-4">
                <div class="col-md-6 col-sm-6 mb-3">
                    <div class="stat-card">
                        <div class="stat-card-title">Upcoming Appointments</div>
                        <div class="stat-card-value">{{ upcomingCount }}</div>
                    </div>
                </div>
                <div class="col-md-6 col-sm-6 mb-3">
                    <div class="stat-card">
                        <div class="stat-card-title">Total Appointments</div>
                        <div class="stat-card-value">{{ totalAppointments }}</div>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Left Column: Departments & Doctors -->
                <div class="col-lg-8">
                    <!-- Departments -->
                    <div class="section-card mb-4">
                        <div class="section-card-header">
                            <h4>Departments</h4>
                            <div class="search-box">
                                <i class="bi bi-search"></i>
                                <input type="text" class="form-control"
                                       v-model="searchQuery"
                                       placeholder="Search departments or doctors...">
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-md-6 mb-3" v-for="dept in filteredDepartments" :key="dept.id">
                                <div class="department-card" @click="viewDepartmentDoctors(dept)">
                                    <h5>{{ dept.name }}</h5>
                                    <p>{{ dept.description }}</p>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <span class="doctor-count">
                                            {{ dept.doctors_count }} Doctors
                                        </span>
                                        <button class="btn btn-sm btn-primary"
                                                @click.stop="viewDepartmentDoctors(dept)">
                                            View Doctors
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Upcoming Appointments -->
                    <div class="data-table-container">
                        <div class="data-table-header">
                            <h3>My Appointments</h3>
                            <div class="table-actions">
                                <select class="form-select" v-model="appointmentFilter" @change="loadAppointments">
                                    <option value="upcoming">Upcoming</option>
                                    <option value="all">All</option>
                                    <option value="past">Past</option>
                                </select>
                            </div>
                        </div>

                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Time</th>
                                    <th>Doctor</th>
                                    <th>Department</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="apt in appointments" :key="apt.id">
                                    <td>{{ formatDate(apt.appointment_date) }}</td>
                                    <td>{{ apt.appointment_time }}</td>
                                    <td>{{ apt.doctor_name }}</td>
                                    <td>{{ apt.department_name }}</td>
                                    <td>
                                        <span class="badge" :class="getStatusClass(apt.status)">
                                            {{ apt.status }}
                                        </span>
                                    </td>
                                    <td>
                                        <button class="btn btn-sm btn-warning btn-action"
                                                @click="rescheduleAppointment(apt)"
                                                v-if="apt.status === 'Booked'">
                                            Reschedule
                                        </button>
                                        <button class="btn btn-sm btn-danger btn-action"
                                                @click="cancelAppointment(apt)"
                                                v-if="apt.status === 'Booked'">
                                            Cancel
                                        </button>
                                        <button class="btn btn-sm btn-info btn-action"
                                                @click="viewTreatmentDetails(apt)"
                                                v-if="apt.status === 'Completed' && apt.treatment">
                                            View Treatment
                                        </button>
                                    </td>
                                </tr>
                                <tr v-if="appointments.length === 0">
                                    <td colspan="6" class="text-center">No appointments found</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Right Column: Profile & History -->
                <div class="col-lg-4">
                    <!-- Profile Card -->
                    <div class="section-card mb-3">
                        <div class="section-card-header">
                            <h4>My Profile</h4>
                            <button class="btn btn-sm btn-outline-primary"
                                    @click="showEditProfileModal = true">
                                Edit
                            </button>
                        </div>

                        <div class="profile-info">
                            <p><strong>Name:</strong> {{ profile?.full_name || 'N/A' }}</p>
                            <p><strong>Phone:</strong> {{ profile?.phone || 'N/A' }}</p>
                            <p><strong>Blood Group:</strong> {{ profile?.blood_group || 'N/A' }}</p>
                            <p><strong>Gender:</strong> {{ profile?.gender || 'N/A' }}</p>
                        </div>
                    </div>

                    <!-- Quick Actions -->
                    <div class="section-card">
                        <h5>Actions</h5>
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary" @click="showBookModal = true">
                            Book Appointment
                            </button>
                            <button class="btn btn-primary" @click="viewTreatmentHistory">
                             View Medical History
                            </button>
                            <button class="btn btn-secondary" @click="exportTreatmentHistory" :disabled="exporting">
                                <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
                                Export Treatment History
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- View Doctors Modal -->
            <div class="modal" :class="{show: showDoctorsModal, 'd-block': showDoctorsModal}"
                 v-if="showDoctorsModal" @click.self="showDoctorsModal = false">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">{{ selectedDepartment?.name }} - Doctors</h5>
                            <button type="button" class="btn-close" @click="showDoctorsModal = false"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6 mb-3" v-for="doctor in departmentDoctors" :key="doctor.id">
                                    <div class="doctor-card">
                                        <div class="doctor-name">{{ doctor.full_name }}</div>
                                        <div class="doctor-specialty">{{ selectedDepartment.name }}</div>
                                        <div class="doctor-info">
                                            {{ doctor.qualification || 'N/A' }}
                                        </div>
                                        <div class="doctor-info">
                                            {{ doctor.experience_years }} years exp.
                                        </div>
                                        <div class="doctor-info">
                                            Fee: {{ doctor.consultation_fee }}


                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Doctor Availability & Book Modal -->
            <div class="modal" :class="{show: showBookModal, 'd-block': showBookModal}"
                 v-if="showBookModal" @click.self="showBookModal = false">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                {{ selectedDoctor ? selectedDoctor.full_name + ' - Availability' : 'Book Appointment' }}
                            </h5>
                            <button type="button" class="btn-close" @click="closeBookModal"></button>
                        </div>
                        <div class="modal-body">
                            <form @submit.prevent="submitBooking">
                                <div class="mb-3" v-if="!selectedDoctor">
                                    <label class="form-label">Select Department</label>
                                    <select class="form-select" v-model="bookingForm.department_id"
                                            @change="loadDepartmentDoctorsForBooking" required>
                                        <option value="">Choose department</option>
                                        <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                                            {{ dept.name }}
                                        </option>
                                    </select>
                                </div>

                                <div class="mb-3" v-if="!selectedDoctor">
                                    <label class="form-label">Select Doctor</label>
                                    <select class="form-select" v-model="bookingForm.doctor_id"
                                            @change="loadDoctorAvailability" required>
                                        <option value="">Choose doctor</option>
                                        <option v-for="doc in bookingDoctors" :key="doc.id" :value="doc.id">
  {{ doc.full_name }} - $ {{ doc.consultation_fee }}
</option>

                                    </select>
                                </div>

                                <div v-if="doctorAvailability.length > 0">
                                    <h6>Available Time Slots</h6>
                                    <div class="availability-calendar">
                                        <div class="calendar-day" v-for="slot in doctorAvailability" :key="slot.id">
                                            <div class="calendar-day-header">
                                                {{ formatDate(slot.date) }}
                                            </div>
                                            <div class="time-slots">
                                                <div class="time-slot available"
                                                     :class="{selected: isSlotSelected(slot.date, slot.start_time)}"
                                                     @click="selectTimeSlot(slot.date, slot.start_time)">
                                                    {{ slot.start_time }} - {{ slot.end_time }}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="mb-3 mt-3">
                                    <label class="form-label">Reason for Visit</label>
                                    <textarea class="form-control" rows="2"
                                              v-model="bookingForm.reason"
                                              placeholder="Brief description of your concern"></textarea>
                                </div>

                                <button type="submit" class="btn btn-primary"
                                        :disabled="!bookingForm.doctor_id || !bookingForm.appointment_date">
                                     Book Appointment
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Edit Profile Modal -->
            <div class="modal" :class="{show: showEditProfileModal, 'd-block': showEditProfileModal}"
                 v-if="showEditProfileModal" @click.self="showEditProfileModal = false">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Edit Profile</h5>
                            <button type="button" class="btn-close" @click="showEditProfileModal = false"></button>
                        </div>
                        <div class="modal-body">
                            <form @submit.prevent="submitProfileUpdate">
                                <div class="mb-3">
                                    <label class="form-label">Full Name</label>
                                    <input type="text" class="form-control" v-model="profileForm.full_name">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Phone</label>
                                    <input type="tel" class="form-control" v-model="profileForm.phone">
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Gender</label>
                                        <select class="form-select" v-model="profileForm.gender">
                                            <option value="">Select</option>
                                            <option value="Male">Male</option>
                                            <option value="Female">Female</option>
                                            <option value="Other">Other</option>
                                        </select>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Blood Group</label>
                                        <select class="form-select" v-model="profileForm.blood_group">
                                            <option value="">Select</option>
                                            <option v-for="bg in bloodGroups" :key="bg">{{ bg }}</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Address</label>
                                    <textarea class="form-control" rows="2" v-model="profileForm.address"></textarea>
                                </div>
                                <button type="submit" class="btn btn-primary">Update Profile</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Treatment History Modal -->
            <div class="modal" :class="{show: showHistoryModal, 'd-block': showHistoryModal}"
                 v-if="showHistoryModal" @click.self="showHistoryModal = false">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">My Medical History</h5>
                            <button type="button" class="btn-close" @click="showHistoryModal = false"></button>
                        </div>
                        <div class="modal-body">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Doctor</th>
                                        <th>Department</th>
                                        <th>Diagnosis</th>
                                        <th>Prescription</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="treatment in treatmentHistory" :key="treatment.id">
                                        <td>{{ formatDate(treatment.appointment_date) }}</td>
                                        <td>{{ treatment.doctor_name }}</td>
                                        <td>{{ treatment.department }}</td>
                                        <td>{{ treatment.diagnosis }}</td>
                                        <td>{{ treatment.prescription || 'N/A' }}</td>
                                    </tr>
                                    <tr v-if="treatmentHistory.length === 0">
                                        <td colspan="5" class="text-center">No treatment history</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal Backdrop -->
            <div class="modal-backdrop fade show"
                 v-if="showDoctorsModal || showBookModal || showEditProfileModal || showHistoryModal">
            </div>
        </div>
    `,

    data() {
        return {
            currentUser: {},
            profile: null,
            departments: [],
            appointments: [],
            treatmentHistory: [],
            departmentDoctors: [],
            bookingDoctors: [],
            doctorAvailability: [],
            selectedDepartment: null,
            selectedDoctor: null,
            searchQuery: '',
            appointmentFilter: 'upcoming',
            showDoctorsModal: false,
            showBookModal: false,
            showEditProfileModal: false,
            showHistoryModal: false,
            bookingForm: {
                department_id: '',
                doctor_id: '',
                appointment_date: '',
                appointment_time: '',
                reason: ''
            },
            profileForm: {
                full_name: '',
                phone: '',
                gender: '',
                blood_group: '',
                address: ''
            },
            bloodGroups: ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'],
            exporting: false
        };
    },

    computed: {
        filteredDepartments() {
            if (!this.searchQuery) return this.departments;
            const query = this.searchQuery.toLowerCase();
            return this.departments.filter(d =>
                d.name.toLowerCase().includes(query) ||
                d.description?.toLowerCase().includes(query)
            );
        },

        upcomingCount() {
            return this.appointments.filter(a => a.status === 'Booked').length;
        },

        totalAppointments() {
            return this.appointments.length;
        }
    },

    mounted() {
        this.currentUser = JSON.parse(localStorage.getItem('user'));
        this.profile = JSON.parse(localStorage.getItem('profile'));
        this.loadDashboard();
    },

    methods: {
        async loadDashboard() {
            try {
                this.$root.loading = true;

                const [deptRes, aptsRes] = await Promise.all([
                    API.patient.getDepartments(),
                    API.patient.getAppointments({ upcoming: true })
                ]);

                this.departments = deptRes.data.departments;
                this.appointments = aptsRes.data.appointments;

            } catch (error) {
                this.$root.showToast('Failed to load dashboard', 'error');
            } finally {
                this.$root.loading = false;
            }
        },

        async loadAppointments() {
            try {
                const params = this.appointmentFilter === 'all' ? {} :
                    this.appointmentFilter === 'past' ? { past: true } :
                        { upcoming: true };

                const response = await API.patient.getAppointments(params);
                this.appointments = response.data.appointments;
            } catch (error) {
                this.$root.showToast('Failed to load appointments', 'error');
            }
        },

        async viewDepartmentDoctors(dept) {
            try {
                this.selectedDepartment = dept;
                const response = await API.patient.getDepartmentDoctors(dept.id);
                this.departmentDoctors = response.data.doctors;
                this.showDoctorsModal = true;
            } catch (error) {
                this.$root.showToast('Failed to load doctors', 'error');
            }
        },

        async loadDepartmentDoctorsForBooking() {
            if (!this.bookingForm.department_id) return;

            try {
                const response = await API.patient.getDepartmentDoctors(this.bookingForm.department_id);
                this.bookingDoctors = response.data.doctors;
            } catch (error) {
                this.$root.showToast('Failed to load doctors', 'error');
            }
        },

        async loadDoctorAvailability() {
            if (!this.bookingForm.doctor_id) return;

            try {
                const response = await API.patient.getDoctor(this.bookingForm.doctor_id);
                this.doctorAvailability = response.data.availability || [];
            } catch (error) {
                this.$root.showToast('Failed to load availability', 'error');
            }
        },

        selectTimeSlot(date, time) {
            this.bookingForm.appointment_date = date;
            this.bookingForm.appointment_time = time;
        },

        isSlotSelected(date, time) {
            return this.bookingForm.appointment_date === date &&
                this.bookingForm.appointment_time === time;
        },

        async submitBooking() {
            try {
                await API.patient.bookAppointment(this.bookingForm);
                this.$root.showToast('Appointment booked successfully!', 'success');
                this.closeBookModal();
                await this.loadDashboard();
            } catch (error) {
                const message = error.response?.data?.error || 'Failed to book appointment';
                this.$root.showToast(message, 'error');
            }
        },

        closeBookModal() {
            this.showBookModal = false;
            this.selectedDoctor = null;
            this.doctorAvailability = [];
            this.bookingForm = {
                department_id: '',
                doctor_id: '',
                appointment_date: '',
                appointment_time: '',
                reason: ''
            };
        },

        async cancelAppointment(apt) {
            if (!confirm('Are you sure you want to cancel this appointment?')) return;

            try {
                await API.patient.cancelAppointment(apt.id);
                this.$root.showToast('Appointment cancelled', 'success');
                await this.loadDashboard();
            } catch (error) {
                this.$root.showToast('Failed to cancel appointment', 'error');
            }
        },

        rescheduleAppointment(apt) {
            alert('Reschedule feature: Please cancel and book a new appointment for now.');
        },

        async viewTreatmentHistory() {
            try {
                const response = await API.patient.getTreatments();
                this.treatmentHistory = response.data.treatments;
                this.showHistoryModal = true;
            } catch (error) {
                this.$root.showToast('Failed to load treatment history', 'error');
            }
        },

        viewTreatmentDetails(apt) {
            if (apt.treatment) {
                alert(`Treatment Details:\n\nDiagnosis: ${apt.treatment.diagnosis}\nPrescription: ${apt.treatment.prescription || 'N/A'}\nNotes: ${apt.treatment.treatment_notes || 'N/A'}`);
            }
        },

        async submitProfileUpdate() {
            try {
                await API.patient.updateProfile(this.profileForm);
                this.$root.showToast('Profile updated successfully', 'success');

                // Reload profile
                const response = await API.patient.getProfile();
                this.profile = response.data.profile;
                localStorage.setItem('profile', JSON.stringify(this.profile));

                this.showEditProfileModal = false;
            } catch (error) {
                const message = error.response?.data?.error || 'Failed to update profile';
                this.$root.showToast(message, 'error');
            }
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
        },

        async exportTreatmentHistory() {
            try {
                this.exporting = true;
                const response = await API.patient.exportTreatments();
                 // Create a blob and trigger download
                const blob = new Blob([response.data], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', `treatment_history.csv`);
                document.body.appendChild(link);
                link.click();
                link.remove();
            } catch (error) {
                const message = error.response?.data?.error || 'Failed to export treatment history.';
                this.$root.showToast(message, 'error');
            } finally {
                this.exporting = false;
            }
        }
    },

    watch: {
        showEditProfileModal(val) {
            if (val && this.profile) {
                this.profileForm = {
                    full_name: this.profile.full_name || '',
                    phone: this.profile.phone || '',
                    gender: this.profile.gender || '',
                    blood_group: this.profile.blood_group || '',
                    address: this.profile.address || ''
                };
            }
        }
    }
};
