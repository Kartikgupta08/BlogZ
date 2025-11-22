document.addEventListener('DOMContentLoaded', function() {
    // Initialize auth check
    checkAuth();

    // Login form handling
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // Basic validation
            if (!validateEmail(email)) {
                showError('email', 'Please enter a valid email address');
                return;
            }

            // Simulate successful login with user data
            const userData = {
                email: email,
                name: email.split('@')[0],
                avatar: 'default-avatar.png'
            };
            
            handleLoginSuccess(userData);
        });
    }

    // Signup form handling
    const signupForm = document.querySelector('.signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            clearErrors();
            let isValid = true;

            // Validation checks
            if (!name || name.length < 2) {
                showError('name', 'Please enter your full name');
                isValid = false;
            }

            if (!validateEmail(email)) {
                showError('email', 'Please enter a valid email address');
                isValid = false;
            }

            if (password.length < 8) {
                showError('password', 'Password must be at least 8 characters');
                isValid = false;
            }

            if (password !== confirmPassword) {
                showError('confirmPassword', 'Passwords do not match');
                isValid = false;
            }

            if (isValid) {
                // Simulate successful signup
                const userData = {
                    name: name,
                    email: email,
                    avatar: 'default-avatar.png'
                };
                handleLoginSuccess(userData);
            }
        });
    }

    // Profile menu handling
    const profileImg = document.querySelector('.profile-img');
    if (profileImg) {
        profileImg.addEventListener('click', function() {
            const menu = document.querySelector('.profile-menu');
            menu?.classList.toggle('show');
        });
    }

    // Logout button handling
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
});

// Utility functions
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showError(fieldId, message) {
    const errorDiv = document.getElementById(`${fieldId}Error`);
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

function clearErrors() {
    const errorDivs = document.querySelectorAll('.error-message');
    errorDivs.forEach(div => {
        div.textContent = '';
        div.style.display = 'none';
    });
}

function checkAuth() {
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const notLoggedIn = document.querySelector('.not-logged-in');
    const loggedIn = document.querySelector('.logged-in');
    const writeBtn = document.querySelector('.write-btn');
    const notificationBtn = document.querySelector('.notification-btn');
    
    if (isLoggedIn === 'true') {
        notLoggedIn?.classList.add('hidden');
        loggedIn?.classList.remove('hidden');
        writeBtn?.classList.remove('hidden');
        notificationBtn?.classList.remove('hidden');
        
        // Set user data
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        if (userData.name) {
            const avatar = document.getElementById('userAvatar');
            if (avatar) {
                avatar.src = userData.avatar || 'default-avatar.png';
                avatar.alt = userData.name;
            }
        }
    } else {
        notLoggedIn?.classList.remove('hidden');
        loggedIn?.classList.add('hidden');
        writeBtn?.classList.add('hidden');
        notificationBtn?.classList.add('hidden');
    }
}

function handleLoginSuccess(userData) {
    localStorage.setItem('isLoggedIn', 'true');
    localStorage.setItem('userData', JSON.stringify(userData));
    window.location.href = 'index.html';
}

function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userData');
    window.location.href = 'login.html';
}