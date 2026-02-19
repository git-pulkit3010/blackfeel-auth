const API_BASE_URL = 'http://localhost:8000/api/auth';

document.addEventListener('DOMContentLoaded', () => {
    // Helper function to show errors
    const showError = (element, message) => {
        // You might want to implement a better UI for errors
        alert(message);
    };

    // Handle Signup Validation
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const fullName = document.getElementById('fullName').value;
            const phone = document.getElementById('phone').value;
            const email = document.getElementById('email').value;
            const pass = document.getElementById('regPassword').value;
            const confirm = document.getElementById('confirmPassword').value;

            if (pass !== confirm) {
                showError(signupForm, "Passwords do not match. Please try again.");
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/signup`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        password: pass,
                        phone: phone // The backend handles phone formatting
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    alert("Account created! Please check your email to verify your account.");
                    window.location.href = 'index.html';
                } else {
                    showError(signupForm, data.detail || "Signup failed");
                }
            } catch (error) {
                console.error("Signup error:", error);
                showError(signupForm, "An error occurred during signup.");
            }
        });
    }

    // Handle Login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch(`${API_BASE_URL}/signin`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Store tokens if needed, though they are also in cookies
                    localStorage.setItem('access_token', data.access_token);
                    window.location.href = 'dashboard.html';
                } else {
                    showError(loginForm, data.detail || "Login failed");
                }
            } catch (error) {
                console.error("Login error:", error);
                showError(loginForm, "An error occurred during login.");
            }
        });
    }
});