/**
 * Doctor Dashboard Component
 * Complete doctor interface matching wireframe
 */

const DoctorDashboard = {
    template: `
        <div class="dashboard-container">
            <!-- Statistics Cards -->
            <div class="row mb-4">
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card">
                        <div class="stat-card-title">Today's Appointments</div>
                        <div class="stat-card-value">{{ stats.today_appointments }}</div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card">
                        <div class="stat-card-title">This Week</div>
                        <div class="stat-card-value">{{ stats.week_appointments }}</div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card">
                        <div class="stat-card-title">Total Patients</div>
                        <div class="stat-card-value">{{ stats.total_patients }}</div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="stat-card">
                        <div class="stat-card-title">Completed</div>
                        <div class="stat-card-value">{{ stats.completed_appointments }}</div>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Left Column: Appointments & Patients -->
                <div class="col-lg-8">
                    <!-- Upcoming Appointments -->
                    <div class="data-table-container mb-4">
                        <div class="data-table-header">
                            <h3>Upcoming Appointments</h3>
                        </div>

                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Time</th>
                                    <th>Patient</th>
                                    <th>Reason</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="apt in appointments" :key="apt.id">
                                    <td>{{ formatDate(apt.appointment_date) }}</td>
                                    <td>{{ apt.appointment_time }}</td>
                                    <td>{{ apt.patient_name }}</td>
                                    <td>{{ apt.reason || 'General checkup' }}</td>
                                    <td>
                                        <button class="btn btn-sm btn-info btn-action"
                                                @click="viewDetails(apt)">
                                            Details
                                        </button>
                                        <button class="btn btn-sm btn-success btn-action"
                                                @click="markComplete(apt)"
                                                v-if="apt.status === 'Booked'">
                                            Complete
                                        </button>
                                        <button class="btn btn-sm btn-danger btn-action"
                                                @click="cancelAppointment(apt)"
                                                v-if="apt.status === 'Booked'">
                                            Cancel
                                        </button>
                                        <span v-else class="badge" :class="getStatusClass(apt.status)">
                                            {{ apt.status }}
                                        </span>
                                    </td>
                                </tr>
                                <tr v-if="appointments.length === 0">
                                    <td colspan="5" class="text-center">No upcoming appointments</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Assigned Patients -->
                    <div class="section-card">
                        <div class="section-card-header">
                            <h4>Assigned Patients</h4>
                        </div>

                        <div class="row">
                            <div class="col-md-6 mb-3" v-for="patient in patients" :key="patient.id">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title">{{ patient.full_name }}</h5>
                                        <p class="card-text">
                                             {{ patient.phone || 'N/A' }}<br>
                                            Blood: {{ patient.blood_group || 'N/A' }}
                                        </p>
                                        <button class="btn btn-sm btn-primary"
                                                @click="viewPatientHistory(patient)">
                                            View History
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Right Column: Availability -->
                <div class="col-lg-4">
                    <div class="section-card">
                        <div class="section-card-header">
                            <h4>Doctor's Availability</h4>
                            <button class="btn btn-sm btn-primary" @click="showAddAvailabilityModal = true">
                                <i class="bi bi-plus"></i> Add
                            </button>
                        </div>

                        <div class="availability-calendar">
                            <div class="calendar-day" v-for="slot in availability" :key="slot.id">
                                <div class="calendar-day-header">
                                    {{ formatDate(slot.date) }}
                                </div>
                                <div class="d-flex justify-content-between align-items-center">
                                    <span>
                                        {{ slot.start_time }} - {{ slot.end_time }}
                                    </span>
                                    <button class="btn btn-sm btn-outline-danger"
                                            @click="deleteAvailability(slot.id)">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </div>
                            </div>
                            <div v-if="availability.length === 0" class="text-center text-muted p-4">
                                No availability set. Click Add to set your schedule.
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Complete Appointment Modal -->
            <div class="modal" :class="{show: showCompleteModal, 'd-block': showCompleteModal}"
                 v-if="showCompleteModal" @click.self="showCompleteModal = false">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Complete Appointment - {{ selectedAppointment?.patient_name }}</h5>
                            <button type="button" class="btn-close" @click="showCompleteModal = false"></button>
                        </div>
                        <div class="modal-body">
                            <form @submit.prevent="submitComplete">
                                <div class="mb-3">
                                    <label class="form-label">Patient Name</label>
                                    <input type="text" class="form-control"
                                           :value="selectedAppointment?.patient_name" disabled>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Date</label>
                                    <input type="text" class="form-control"
                                           :value="formatDate(selectedAppointment?.appointment_date)" disabled>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Diagnosis *</label>
                                    <textarea class="form-control" rows="3"
                                              v-model="treatmentForm.diagnosis"
                                              placeholder="Enter diagnosis" required></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Prescription</label>
                                    <textarea class="form-control" rows="3"
                                              v-model="treatmentForm.prescription"
                                              placeholder="Enter medicines and dosage"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Treatment Notes</label>
                                    <textarea class="form-control" rows="2"
                                              v-model="treatmentForm.treatment_notes"
                                              placeholder="Additional notes"></textarea>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Next Visit Date</label>
                                        <input type="date" class="form-control"
                                               v-model="treatmentForm.next_visit_date">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">Follow-up Required</label>
                                        <select class="form-select" v-model="treatmentForm.follow_up_required">
                                            <option value="false">No</option>
                                            <option value="true">Yes</option>
                                        </select>
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-success">Save & Complete</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Add Availability Modal -->
            <div class="modal" :class="{show: showAddAvailabilityModal, 'd-block': showAddAvailabilityModal}"
                 v-if="showAddAvailabilityModal" @click.self="showAddAvailabilityModal = false">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Set Availability</h5>
                            <button type="button" class="btn-close" @click="showAddAvailabilityModal = false"></button>
                        </div>
                        <div class="modal-body">
                            <form @submit.prevent="submitAvailability">
                                <div class="mb-3">
                                    <label class="form-label">Date</label>
                                    <input type="date" class="form-control"
                                           v-model="availabilityForm.date" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Start Time</label>
                                    <input type="time" class="form-control"
                                           v-model="availabilityForm.start_time" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">End Time</label>
                                    <input type="time" class="form-control"
                                           v-model="availabilityForm.end_time" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Save Availability</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Patient History Modal -->
            <div class="modal" :class="{show: showPatientHistoryModal, 'd-block': showPatientHistoryModal}"
                 v-if="showPatientHistoryModal" @click.self="showPatientHistoryModal = false">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Patient History - {{ selectedPatient?.full_name }}</h5>
                            <button type="button" class="btn-close" @click="showPatientHistoryModal = false"></button>
                        </div>
                        <div class="modal-body">
                            <h6>Patient Information</h6>
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <strong>Phone:</strong> {{ selectedPatient?.phone || 'N/A' }}
                                </div>
                                <div class="col-md-6">
                                    <strong>Blood Group:</strong> {{ selectedPatient?.blood_group || 'N/A' }}
                                </div>
                            </div>

                            <h6>Medical History</h6>
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Diagnosis</th>
                                        <th>Prescription</th>
                                        <th>Notes</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="treatment in patientHistory" :key="treatment.id">
                                        <td>{{ formatDate(treatment.appointment_date) }}</td>
                                        <td>{{ treatment.diagnosis }}</td>
                                        <td>{{ treatment.prescription || 'N/A' }}</td>
                                        <td>{{ treatment.treatment_notes || 'N/A' }}</td>
                                    </tr>
                                    <tr v-if="patientHistory.length === 0">
                                        <td colspan="4" class="text-center">No history available</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal Backdrop -->
            <div class="modal-backdrop fade show" v-if="showCompleteModal || showAddAvailabilityModal || showPatientHistoryModal"></div>
        </div>
    `,

    data() {
        return {
            profile: null,
            stats: {
                today_appointments: 0,
                week_appointments: 0,
                total_patients: 0,
                completed_appointments: 0
            },
            appointments: [],
            patients: [],
            availability: [],
            patientHistory: [],
            selectedAppointment: null,
            selectedPatient: null,
            showCompleteModal: false,
            showAddAvailabilityModal: false,
            showPatientHistoryModal: false,
            treatmentForm: {
                diagnosis: '',
                prescription: '',
                treatment_notes: '',
                next_visit_date: '',
                follow_up_required: false
            },
            availabilityForm: {
                date: '',
                start_time: '',
                end_time: ''
            }
        };
    },

    mounted() {
        this.profile = JSON.parse(localStorage.getItem('profile'));
        this.loadDashboard();
    },

    methods: {
        async loadDashboard() {
            try {
                this.$root.loading = true;

                const [statsRes, aptsRes, patientsRes, availRes] = await Promise.all([
                    API.doctor.getDashboard(),
                    API.doctor.getAppointments({ upcoming: true }),
                    API.doctor.getPatients(),
                    API.doctor.getAvailability()
                ]);

                this.stats = statsRes.data;
                this.appointments = aptsRes.data.appointments;
                this.patients = patientsRes.data.patients;
                this.availability = availRes.data.availability;

            } catch (error) {
                this.$root.showToast('Failed to load dashboard', 'error');
            } finally {
                this.$root.loading = false;
            }
        },

        markComplete(appointment) {
            this.selectedAppointment = appointment;
            this.treatmentForm = {
                diagnosis: '',
                prescription: '',
                treatment_notes: '',
                next_visit_date: '',
                follow_up_required: false
            };
            this.showCompleteModal = true;
        },

        async submitComplete() {
            try {
                await API.doctor.completeAppointment(this.selectedAppointment.id, this.treatmentForm);
                this.$root.showToast('Appointment completed successfully', 'success');
                this.showCompleteModal = false;
                await this.loadDashboard();
            } catch (error) {
                const message = error.response?.data?.error || 'Failed to complete appointment';
                this.$root.showToast(message, 'error');
            }
        },

        async cancelAppointment(appointment) {
            if (!confirm(`Cancel appointment with ${appointment.patient_name}?`)) return;

            try {
                await API.doctor.cancelAppointment(appointment.id);
                this.$root.showToast('Appointment cancelled', 'success');
                await this.loadDashboard();
            } catch (error) {
                this.$root.showToast('Failed to cancel appointment', 'error');
            }
        },

        async submitAvailability() {
            try {
                await API.doctor.setAvailability(this.availabilityForm);
                this.$root.showToast('Availability set successfully', 'success');
                this.showAddAvailabilityModal = false;
                this.availabilityForm = { date: '', start_time: '', end_time: '' };
                await this.loadDashboard();
            } catch (error) {
                const message = error.response?.data?.error || 'Failed to set availability';
                this.$root.showToast(message, 'error');
            }
        },

        async deleteAvailability(id) {
            if (!confirm('Delete this availability slot?')) return;

            try {
                await API.doctor.deleteAvailability(id);
                this.$root.showToast('Availability deleted', 'success');
                await this.loadDashboard();
            } catch (error) {
                this.$root.showToast('Failed to delete availability', 'error');
            }
        },

        async viewPatientHistory(patient) {
            try {
                this.selectedPatient = patient;
                const response = await API.doctor.getPatientHistory(patient.id);
                this.patientHistory = response.data.treatments;
                this.showPatientHistoryModal = true;
            } catch (error) {
                this.$root.showToast('Failed to load patient history', 'error');
            }
        },

        viewDetails(appointment) {
            alert(`Appointment Details:\n\nPatient: ${appointment.patient_name}\nDate: ${this.formatDate(appointment.appointment_date)}\nTime: ${appointment.appointment_time}\nReason: ${appointment.reason || 'General checkup'}\nStatus: ${appointment.status}`);
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
