/**
 * Authentication Component
 * Handles Login and Register functionality
 */

const AuthComponent = {
    template: `
        <div class="auth-container">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-lg-10">
                        <div class="auth-card">
                            <div class="auth-header">
                                <i class="bi bi-hospital-fill" style="font-size: 3rem;"></i>
                                <h2>Hospital Management System</h2>
                                <p class="mb-0">{{ isLogin ? 'Login to your account' : 'Create a new account' }}</p>
                            </div>

                            <div class="auth-body">
                                <div class="row">
                                    <!-- Login Form -->
                                    <div class="col-md-6" v-if="isLogin">
                                        <h3 class="mb-4">Login</h3>
                                        <form @submit.prevent="handleLogin">
                                            <div class="mb-3">
                                                <label class="form-label">Username</label>
                                                <input
                                                    type="text"
                                                    class="form-control"
                                                    v-model="loginForm.username"
                                                    placeholder="Enter username"
                                                    required>
                                            </div>
                                            <div class="mb-3">
                                                <label class="form-label">Password</label>
                                                <input
                                                    type="password"
                                                    class="form-control"
                                                    v-model="loginForm.password"
                                                    placeholder="Enter password"
                                                    required>
                                            </div>
                                            <button type="submit" class="btn btn-primary btn-auth" :disabled="loading">
                                                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                                                Login
                                            </button>
                                            <p class="text-center mt-3">
                                                Patients can
                                                <a href="#" @click.prevent="isLogin = false" class="text-primary">Register</a>
                                            </p>
                                        </form>
                                    </div>

                                    <!-- Register Form -->
                                    <div class="col-md-6" v-else>
                                        <h3 class="mb-4">Register (Patient)</h3>
                                        <form @submit.prevent="handleRegister">
                                            <div class="mb-3">
                                                <label class="form-label">Username</label>
                                                <input
                                                    type="text"
                                                    class="form-control"
                                                    v-model="registerForm.username"
                                                    placeholder="Choose a username"
                                                    required>
                                            </div>
                                            <div class="mb-3">
                                                <label class="form-label">Email</label>
                                                <input
                                                    type="email"
                                                    class="form-control"
                                                    v-model="registerForm.email"
                                                    placeholder="Enter email"
                                                    required>
                                            </div>
                                            <div class="mb-3">
                                                <label class="form-label">Password</label>
                                                <input
                                                    type="password"
                                                    class="form-control"
                                                    v-model="registerForm.password"
                                                    placeholder="Choose a password"
                                                    required>
                                            </div>
                                            <div class="mb-3">
                                                <label class="form-label">Full Name</label>
                                                <input
                                                    type="text"
                                                    class="form-control"
                                                    v-model="registerForm.full_name"
                                                    placeholder="Enter full name"
                                                    required>
                                            </div>
                                            <div class="mb-3">
                                                <label class="form-label">Phone (Optional)</label>
                                                <input
                                                    type="tel"
                                                    class="form-control"
                                                    v-model="registerForm.phone"
                                                    placeholder="Enter phone number">
                                            </div>
                                            <button type="submit" class="btn btn-success btn-auth" :disabled="loading">
                                                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                                                Register
                                            </button>
                                            <p class="text-center mt-3">
                                                Already have an account?
                                                <a href="#" @click.prevent="isLogin = true" class="text-primary">Login</a>
                                            </p>
                                        </form>
                                    </div>

                                    <!-- Divider -->
                                    <div class="col-12 mt-4">
                                        <hr>
                                        <div class="text-center">
                                            <button
                                                class="btn btn-outline-primary me-2"
                                                @click="toggleForm">
                                                {{ isLogin ? 'Switch to Register' : 'Switch to Login' }}
                                            </button>
                                        </div>

                                        <!-- Quick Login Credentials -->
                                        <div class="mt-4 p-3" style="background-color: #f8f9fa; border-radius: 8px;">
                                            <h6 class="text-center mb-3">Quick Test Credentials</h6>
                                            <div class="row text-center small">
                                                <div class="col-md-4">
                                                    <strong>Admin</strong><br>
                                                    admin / admin123
                                                </div>
                                                <div class="col-md-4">
                                                    <strong>Doctor</strong><br>
                                                    dr_heart / doctor123
                                                </div>
                                                <div class="col-md-4">
                                                    <strong>Patient</strong><br>
                                                    patient1 / patient123
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            isLogin: true,
            loading: false,
            loginForm: {
                username: '',
                password: ''
            },
            registerForm: {
                username: '',
                email: '',
                password: '',
                full_name: '',
                phone: ''
            }
        };
    },

    methods: {
       async handleLogin() {
    this.loading = true;
    try {
        const response = await API.auth.login(this.loginForm);
        const { access_token, user, profile } = response.data;

        // Store token and user data
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user', JSON.stringify(user));
        localStorage.setItem('profile', JSON.stringify(profile));

        // ✅ Emit login-success event to parent
        this.$emit('login-success', user);

        // ✅ Optional toast (parent also can show)
        this.$root.showToast('Login successful!', 'success');

    } catch (error) {
        const message = error.response?.data?.error || 'Login failed. Please try again.';
        this.$root.showToast(message, 'error');
    } finally {
        this.loading = false;
    }

        },

        async handleRegister() {
            this.loading = true;
            try {
                await API.auth.register(this.registerForm);

                // Show success message
                this.$root.showToast('Registration successful! Please login.', 'success');

                // Switch to login form
                this.isLogin = true;

                // Reset form
                this.registerForm = {
                    username: '',
                    email: '',
                    password: '',
                    full_name: '',
                    phone: ''
                };

            } catch (error) {
                const message = error.response?.data?.error || 'Registration failed. Please try again.';
                this.$root.showToast(message, 'error');
            } finally {
                this.loading = false;
            }
        },

        toggleForm() {
            this.isLogin = !this.isLogin;
        }
    }
};
