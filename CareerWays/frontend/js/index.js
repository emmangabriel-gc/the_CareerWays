// index.js - Index page functionality

// API Base URL
const API_BASE_URL = window.__CW_API_BASE__;

async function parseJsonResponse(response) {
    const text = await response.text();
    if (!text) return {};
    try {
        return JSON.parse(text);
    } catch (_) {
        return { _raw: text };
    }
}

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

// Unverified modal elements
const unverifiedModal = document.getElementById('unverifiedModal');
const unverifiedEmailDisplay = document.getElementById('unverifiedEmailDisplay');
const resendFromLoginBtn = document.getElementById('resendFromLoginBtn');
const closeUnverifiedModal = document.getElementById('closeUnverifiedModal');
const resendStatusModal = document.getElementById('resendStatusModal');

// Pending Action Storage
let pendingAction = null; // 'signup' or 'guest'
let pendingFormData = null;

// Track the last attempted login email (for resend from login screen)
let lastLoginEmail = '';

// Resend cooldown (prevent spam)
let resendCooldown = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupTermsModal();
    setupUnverifiedModal();
    checkAlreadyLoggedIn();
    handleVerifyRedirect(); // Check if coming back from a verification link
});

// ─── Handle Redirect after Email Verification ──────────────────────────────
// If the backend redirects to index.html?verified=true after the user clicks
// the email link, show a success message and switch to the login tab.
function handleVerifyRedirect() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('verified') === 'true') {
        switchTab('login');
        showNotification('Email verified! You can now log in.', 'success');
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    if (params.get('verified') === 'expired') {
        switchTab('login');
        showNotification('Verification link expired. Please request a new one.', 'error');
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// ─── Setup Event Listeners ─────────────────────────────────────────────────
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

    // Resend from verify-email tab
    const resendBtn = document.getElementById('resendBtn');
    if (resendBtn) {
        resendBtn.addEventListener('click', () => handleResendVerification('resendStatus'));
    }

    // Toggle password visibility
    setupPasswordToggle();
}

// ─── Setup Terms Modal ─────────────────────────────────────────────────────
function setupTermsModal() {
    if (!termsCheckbox || !acceptTermsBtn || !declineTermsBtn) return;

    termsCheckbox.addEventListener('change', () => {
        acceptTermsBtn.disabled = !termsCheckbox.checked;
    });

    acceptTermsBtn.addEventListener('click', () => {
        if (termsCheckbox.checked) {
            acceptTerms();
        }
    });

    declineTermsBtn.addEventListener('click', () => {
        hideTermsModal();
        pendingAction = null;
        pendingFormData = null;
    });

    termsModal.addEventListener('click', (e) => {
        if (e.target === termsModal) return; // Force explicit choice
    });
}

// ─── Setup Unverified Modal ────────────────────────────────────────────────
function setupUnverifiedModal() {
    if (!unverifiedModal) return;

    if (closeUnverifiedModal) {
        closeUnverifiedModal.addEventListener('click', hideUnverifiedModal);
    }

    if (resendFromLoginBtn) {
        resendFromLoginBtn.addEventListener('click', () => {
            handleResendVerification('resendStatusModal');
        });
    }

    unverifiedModal.addEventListener('click', (e) => {
        if (e.target === unverifiedModal) hideUnverifiedModal();
    });
}

function showUnverifiedModal(email) {
    lastLoginEmail = email;
    if (unverifiedEmailDisplay) unverifiedEmailDisplay.textContent = email;
    if (resendStatusModal) resendStatusModal.textContent = '';
    if (unverifiedModal) {
        unverifiedModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function hideUnverifiedModal() {
    if (unverifiedModal) {
        unverifiedModal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// ─── Show Terms Modal ──────────────────────────────────────────────────────
function showTermsModal() {
    if (termsModal) {
        termsModal.classList.add('active');
        document.body.style.overflow = 'hidden';
        if (termsCheckbox) termsCheckbox.checked = false;
        if (acceptTermsBtn) acceptTermsBtn.disabled = true;
    }
}

function hideTermsModal() {
    if (termsModal) {
        termsModal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// ─── Terms helpers ─────────────────────────────────────────────────────────
function hasAcceptedTerms() {
    return sessionStorage.getItem('termsAccepted') === 'true';
}

function acceptTerms() {
    sessionStorage.setItem('termsAccepted', 'true');
    hideTermsModal();

    switch (pendingAction) {
        case 'signup':
            if (pendingFormData) {
                document.getElementById('signup-name').value = pendingFormData.name;
                document.getElementById('signup-email').value = pendingFormData.email;
                document.getElementById('signup-password').value = pendingFormData.password;
                document.getElementById('signup-confirm').value = pendingFormData.confirmPassword;
                handleSignupSubmit({ preventDefault: () => { } });
            }
            break;
        case 'guest':
            handleGuestAccessSubmit();
            break;
    }

    pendingAction = null;
    pendingFormData = null;
}

// ─── Password Toggle ───────────────────────────────────────────────────────
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

// ─── Tab Switching ─────────────────────────────────────────────────────────
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tabBtns.forEach(btn => btn.classList.remove('active'));

    const selectedContent = document.getElementById(tabName);
    if (selectedContent) selectedContent.classList.add('active');

    // Only highlight the button if it exists in the nav bar
    const selectedBtn = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
    if (selectedBtn) selectedBtn.classList.add('active');
}

// ─── Handle Login Submit ───────────────────────────────────────────────────
async function handleLoginSubmit(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    lastLoginEmail = email;

    showGlobalLoading('Logging in...');
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await parseJsonResponse(response);
        const code = data.code ? ` [${data.code}]` : '';

        if (response.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('userType', 'registered');

            showNotification('Login successful!', 'success');
            setTimeout(() => { window.location.href = 'dashboard.html'; }, 1000);

        } else if (response.status === 403 && data.code === 'EMAIL_NOT_VERIFIED') {
            // Account exists but email not verified — show the unverified modal
            showUnverifiedModal(email);

        } else {
            console.error('Login error', response.status, data);
            showNotification(`${data.message || 'Login failed'}${code}`, 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('An error occurred. Please try again.', 'error');
    } finally {
        hideGlobalLoading();
    }
}

// ─── Handle Sign Up Submit ─────────────────────────────────────────────────
async function handleSignupSubmit(e) {
    const name = document.getElementById('signup-name').value.trim();
    const email = document.getElementById('signup-email').value.trim();
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm').value;

    if (password !== confirmPassword) {
        showNotification('Passwords do not match', 'error');
        return;
    }

    showGlobalLoading('Creating account...');
    if (password.length < 6) {
        showNotification('Password must be at least 6 characters long', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });

        const data = await parseJsonResponse(response);
        const code = data.code ? ` [${data.code}]` : '';

        if (response.ok) {
            // Show the verify-email tab instead of redirecting
            lastLoginEmail = email;
            const emailDisplay = document.getElementById('verifyEmailDisplay');
            if (emailDisplay) emailDisplay.textContent = email;

            showNotification('Account created! Please check your email to verify.', 'success');
            switchTab('verify-email');

            // Clear signup form
            signupForm.reset();
        } else {
            console.error('Signup error', response.status, data);
            showNotification(`${data.message || 'Sign up failed'}${code}`, 'error');
        }
    } catch (error) {
        console.error('Signup error:', error);
        showNotification('An error occurred. Please try again.', 'error');
    } finally {
        hideGlobalLoading();
    }
}

// ─── Resend Verification Email ─────────────────────────────────────────────
async function handleResendVerification(statusElementId) {
    const statusEl = document.getElementById(statusElementId);
    showGlobalLoading('Sending verification email...');

    if (resendCooldown) {
        if (statusEl) {
            statusEl.textContent = 'Please wait a moment before requesting again.';
            statusEl.style.color = 'var(--color-warning, #e08a00)';
        }
        return;
    }

    if (!lastLoginEmail) {
        if (statusEl) {
            statusEl.textContent = 'No email address found. Please sign up again.';
            statusEl.style.color = 'var(--color-error, #c0392b)';
        }
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/resend-verification`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: lastLoginEmail })
        });

        const data = await response.json();

        if (response.ok) {
            if (statusEl) {
                statusEl.textContent = `Verification email resent to ${lastLoginEmail}.`;
                statusEl.style.color = 'var(--color-success, #27ae60)';
            }
            // Start 60-second cooldown
            resendCooldown = true;
            setTimeout(() => {
                resendCooldown = false;
                if (statusEl) statusEl.textContent = '';
            }, 60000);
        } else {
            if (statusEl) {
                statusEl.textContent = data.message || 'Failed to resend. Please try again.';
                statusEl.style.color = 'var(--color-error, #c0392b)';
            }
        }
    } catch (error) {
        console.error('Resend error:', error);
        if (statusEl) {
            statusEl.textContent = 'Network error. Please try again.';
            statusEl.style.color = 'var(--color-error, #c0392b)';
        }
    } finally {
        hideGlobalLoading();
    }
}

// ─── Guest Access ──────────────────────────────────────────────────────────
function handleGuestAccessSubmit() {
    if (isGuestAssessmentBlocked()) {
        showNotification('Guest access is limited to one assessment per device. Please sign up or log in to continue.', 'warning');
        return;
    }

    localStorage.removeItem('token');
    localStorage.setItem('userType', 'guest');
    localStorage.setItem('guestId', 'guest_' + Date.now());

    showGlobalLoading('Continuing as guest...');
    showNotification('Continuing as guest...', 'info');
    setTimeout(() => { window.location.href = 'dashboard.html'; }, 1000);
}

// ─── Already Logged In ─────────────────────────────────────────────────────
function checkAlreadyLoggedIn() {
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = 'dashboard.html';
    }
}

// ─── Notification ──────────────────────────────────────────────────────────
function showNotification(message, type = 'info') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    notification.style.opacity = '1';
    notification.style.visibility = 'visible';

    setTimeout(() => {
        notification.classList.add('hidden');
        setTimeout(() => {
            notification.style.display = 'none';
            notification.style.visibility = 'hidden';
            notification.style.opacity = '0';
        }, 300);
    }, 3000);
}
