// index.js - Index page functionality

// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const guestBtn = document.getElementById('guestBtn');
const tabBtns = document.querySelectorAll('.tab-btn');
const switchTabs = document.querySelectorAll('.switch-tab');
const notification = document.getElementById('notification');

// Terms and Conditions Elements
const termsModal = document.getElementById('termsModal');
const termsContent = document.getElementById('termsContent');
const termsCheckbox = document.getElementById('termsCheckbox');
const acceptTermsBtn = document.getElementById('acceptTerms');
const declineTermsBtn = document.getElementById('declineTerms');

// Pending Action Storage
let pendingAction = null; // 'signup' or 'guest'
let pendingFormData = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupTermsModal();
    checkAlreadyLoggedIn();
});

// Setup Event Listeners
function setupEventListeners() {
    // Tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', (e) => switchTab(e.target.dataset.tab));
    });

    switchTabs.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(e.target.dataset.tab);
        });
    });

    // Form submissions
    // Login - no terms check required
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }

    // Signup - check terms acceptance first
    if (signupForm) {
        signupForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!hasAcceptedTerms()) {
                pendingAction = 'signup';
                pendingFormData = {
                    name: document.getElementById('signup-name').value,
                    email: document.getElementById('signup-email').value,
                    password: document.getElementById('signup-password').value,
                    confirmPassword: document.getElementById('signup-confirm').value
                };
                showTermsModal();
                return;
            }
            handleSignupSubmit(e);
        });
    }

    // Guest access - check terms acceptance first
    if (guestBtn) {
        guestBtn.addEventListener('click', () => {
            if (!hasAcceptedTerms()) {
                pendingAction = 'guest';
                showTermsModal();
                return;
            }
            handleGuestAccessSubmit();
        });
    }

    // Toggle password visibility
    setupPasswordToggle();
}

// Setup Terms Modal
function setupTermsModal() {
    if (!termsCheckbox || !acceptTermsBtn || !declineTermsBtn) return;

    // Handle checkbox change - enable Continue when checked
    termsCheckbox.addEventListener('change', () => {
        acceptTermsBtn.disabled = !termsCheckbox.checked;
    });

    // Handle Continue button
    acceptTermsBtn.addEventListener('click', () => {
        if (termsCheckbox.checked) {
            acceptTerms();
        }
    });

    // Handle Back button
    declineTermsBtn.addEventListener('click', () => {
        hideTermsModal();
        pendingAction = null;
        pendingFormData = null;
    });

    // Close on overlay click
    termsModal.addEventListener('click', (e) => {
        if (e.target === termsModal) {
            // Don't close on overlay click - force explicit choice
            return;
        }
    });
}

// Show Terms Modal
function showTermsModal() {
    if (termsModal) {
        termsModal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Reset checkbox and button state
        if (termsCheckbox) {
            termsCheckbox.checked = false;
        }
        if (acceptTermsBtn) {
            acceptTermsBtn.disabled = true;
        }
    }
}

// Hide Terms Modal
function hideTermsModal() {
    if (termsModal) {
        termsModal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Check if user has accepted terms (stored in session)
function hasAcceptedTerms() {
    return sessionStorage.getItem('termsAccepted') === 'true';
}

// Accept Terms and proceed with pending action
function acceptTerms() {
    sessionStorage.setItem('termsAccepted', 'true');
    hideTermsModal();
    
    // Execute pending action
    switch (pendingAction) {
        case 'signup':
            if (pendingFormData) {
                document.getElementById('signup-name').value = pendingFormData.name;
                document.getElementById('signup-email').value = pendingFormData.email;
                document.getElementById('signup-password').value = pendingFormData.password;
                document.getElementById('signup-confirm').value = pendingFormData.confirmPassword;
                handleSignupSubmit({ preventDefault: () => {} });
            }
            break;
        case 'guest':
            handleGuestAccessSubmit();
            break;
    }
    
    pendingAction = null;
    pendingFormData = null;
}

// Setup Password Toggle
function setupPasswordToggle() {
    const toggleButtons = document.querySelectorAll('.toggle-password');

    toggleButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const passwordInput = btn.parentElement.querySelector('input');
            const isPassword = passwordInput.type === 'password';

            passwordInput.type = isPassword ? 'text' : 'password';
            btn.textContent = isPassword ? 'Hide' : 'Show';
        });
    });
}

// Tab Switching
function switchTab(tabName) {
    // Hide all content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    // Deactivate all tabs
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected content
    const selectedContent = document.getElementById(tabName);
    if (selectedContent) {
        selectedContent.classList.add('active');
    }

    // Activate selected tab
    const selectedBtn = document.querySelector(`[data-tab="${tabName}"]`);
    if (selectedBtn) {
        selectedBtn.classList.add('active');
    }
}

// Handle Login Submit
async function handleLoginSubmit(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            // Store token and user info
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('userType', 'registered');

            showNotification('Login successful!', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            showNotification(data.message || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('An error occurred. Please try again.', 'error');
    }
}

// Handle Sign Up Submit
async function handleSignupSubmit(e) {
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm').value;

    // Validate passwords match
    if (password !== confirmPassword) {
        showNotification('Passwords do not match', 'error');
        return;
    }

    // Validate password strength
    if (password.length < 6) {
        showNotification('Password must be at least 6 characters long', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Account created successfully! Logging in...', 'success');

            // Auto login after signup
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('userType', 'registered');

            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            showNotification(data.message || 'Sign up failed', 'error');
        }
    } catch (error) {
        console.error('Signup error:', error);
        showNotification('An error occurred. Please try again.', 'error');
    }
}

// Handle Guest Access Submit
function handleGuestAccessSubmit() {
    // Set guest session
    localStorage.removeItem('token');
    localStorage.setItem('userType', 'guest');
    localStorage.setItem('guestId', 'guest_' + Date.now());

    showNotification('Continuing as guest...', 'info');
    setTimeout(() => {
        window.location.href = 'dashboard.html';
    }, 1000);
}

// Check if already logged in
function checkAlreadyLoggedIn() {
    const token = localStorage.getItem('token');
    if (token) {
        // User is already logged in, redirect to dashboard
        window.location.href = 'dashboard.html';
    }
}

// Show Notification
function showNotification(message, type = 'info') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    notification.style.opacity = '1';        // Reset opacity
    notification.style.visibility = 'visible'; // Reset visibility

    setTimeout(() => {
        notification.classList.add('hidden');
        setTimeout(() => {
            notification.style.display = 'none';
            notification.style.visibility = 'hidden';
            notification.style.opacity = '0';
        }, 300);
    }, 3000);
}