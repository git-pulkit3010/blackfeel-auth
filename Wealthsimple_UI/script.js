document.addEventListener('DOMContentLoaded', () => {
    // Handle Signup Validation
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', (e) => {
            const pass = document.getElementById('regPassword').value;
            const confirm = document.getElementById('confirmPassword').value;

            if (pass !== confirm) {
                e.preventDefault();
                alert("Passwords do not match. Please try again.");
            } else {
                console.log("Signup data ready for backend.");
            }
        });
    }

    // Handle Login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log("Login submitted.");
        });
    }
});