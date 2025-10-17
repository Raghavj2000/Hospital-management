/**
 * Navbar Component
 * Top navigation bar with user info and logout
 */

const NavbarComponent = {
    template: `
        <nav class="navbar navbar-expand-lg navbar-custom">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">
                    <i class="bi bi-hospital-fill"></i>
                    Hospital Management
                </a>

                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>

                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item">
                            <div class="user-info">
                                <div class="user-avatar-small">
                                    {{ getUserInitials() }}
                                </div>
                                <div>
                                    <div class="fw-bold">{{ user.username }}</div>
                                    <small class="text-muted">{{ getRoleLabel() }}</small>
                                </div>
                            </div>
                        </li>
                        <li class="nav-item ms-3">
                            <button class="btn btn-outline-danger btn-sm" @click="handleLogout">
                                <i class="bi bi-box-arrow-right"></i>
                                Logout
                            </button>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    `,

    props: ['user'],

    methods: {
        getUserInitials() {
            if (!this.user || !this.user.username) return '?';
            return this.user.username.substring(0, 2).toUpperCase();
        },

        getRoleLabel() {
            const roles = {
                'admin': 'Administrator',
                'doctor': 'Doctor',
                'patient': 'Patient'
            };
            return roles[this.user.role] || this.user.role;
        },

        handleLogout() {
            if (confirm('Are you sure you want to logout?')) {
                this.$emit('logout');
            }
        }
    }
};
