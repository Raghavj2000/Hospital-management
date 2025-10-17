/**
 * Main Vue.js Application
 * Hospital Management System Frontend
 */

const { createApp } = Vue;

const app = createApp({
    data() {
        return {
            isAuthenticated: false,
            currentUser: null,
            loading: false,
            toasts: []
        };
    },

    mounted() {
        // Check if user is already logged in
        const token = localStorage.getItem('access_token');
        const user = localStorage.getItem('user');

        if (token && user) {
            this.isAuthenticated = true;
            this.currentUser = JSON.parse(user);
        }
    },

    methods: {
        handleLoginSuccess(user) {
            // Set authenticated state
            this.isAuthenticated = true;
            this.currentUser = user;
        },

        handleLogout() {
            // Clear storage
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            localStorage.removeItem('profile');

            // Reset state
            this.isAuthenticated = false;
            this.currentUser = null;

            // Show message
            this.showToast('Logged out successfully', 'success');
        },

        showToast(message, type = 'success') {
            const toast = { message, type };
            this.toasts.push(toast);

            // Auto remove after 3 seconds
            setTimeout(() => {
                this.removeToast(0);
            }, 3000);
        },

        removeToast(index) {
            this.toasts.splice(index, 1);
        }
    }
});

// Register components
app.component('auth-component', AuthComponent);
app.component('navbar-component', NavbarComponent);
app.component('admin-dashboard', AdminDashboard);
app.component('doctor-dashboard', DoctorDashboard);
app.component('patient-dashboard', PatientDashboard);

// Custom directive for auto-focus
app.directive('focus', {
    mounted(el) {
        el.focus();
    }
});

// Mount the app
app.mount('#app');

// Global error handler
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
});
