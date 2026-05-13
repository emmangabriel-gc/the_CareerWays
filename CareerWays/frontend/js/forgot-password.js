// forgot-password.js - Password Reset using CareerWays Backend

const API_BASE_URL = window.__CW_API_BASE__;

// DOM Elements
const notification = document.getElementById('notification');
const emailInput = document.getElementById('email');
const otpInput = document.getElementById('otp');
const newPasswordInput = document.getElementById('newPassword');
const confirmPasswordInput = document.getElementById('confirmPassword');

// Buttons
const sendOtpBtn = document.getElementById('sendOtpBtn');
const verifyOtpBtn = document.getElementById('verifyOtpBtn');
const resendOtpBtn = document.getElementById('resendOtpBtn');
const changeEmailBtn = document.getElementById('changeEmailBtn');
const resetPasswordBtn = document.getElementById('resetPasswordBtn');

// Form steps
const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');

const progressSteps = document.querySelectorAll('.progress-step');

// Session data
let userEmail = '';
let resetToken = '';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    sendOtpBtn.addEventListener('click', handleSendOtp);
    verifyOtpBtn.addEventListener('click', handleVerifyOtp);
    resendOtpBtn.addEventListener('click', handleResendOtp);
    changeEmailBtn.addEventListener('click', handleChangeEmail);
    resetPasswordBtn.addEventListener('click', handleResetPassword);

    setupPasswordToggle();

    emailInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleSendOtp(); });
    otpInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleVerifyOtp(); });
}

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

function showStep(stepNumber) {
    step1.classList.remove('active');
    step2.classList.remove('active');
    step3.classList.remove('active');

    if (stepNumber === 1) step1.classList.add('active');
    if (stepNumber === 2) step2.classList.add('active');
    if (stepNumber === 3) step3.classList.add('active');

    updateProgressIndicator(stepNumber);
}

function updateProgressIndicator(currentStep) {
    progressSteps.forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.remove('active', 'completed');
        if (stepNum < currentStep) step.classList.add('completed');
        else if (stepNum === currentStep) step.classList.add('active');
    });
}

async function parseJsonResponse(response) {
    const text = await response.text();
    if (!text) return {};
    try {
        return JSON.parse(text);
    } catch (_) {
        return { _raw: text };
    }
}

// Step 1: Send OTP via backend
async function handleSendOtp() {
    const email = emailInput.value.trim();

    if (!email || !isValidEmail(email)) {
        showNotification('Please enter a valid email address', 'error');
        return;
    }

    try {
        sendOtpBtn.disabled = true;
        sendOtpBtn.textContent = 'Sending...';

        const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        const data = await parseJsonResponse(response);
        const code = data.code ? ` [${data.code}]` : '';

        if (!response.ok) {
            const msg =
                data.message ||
                (data._raw
                    ? `Server returned ${response.status} (not JSON). Check Railway logs.`
                    : `Request failed (${response.status})`);
            console.error('forgot-password error', response.status, data);
            throw new Error(`${msg}${code}`);
        }

        userEmail = email;
        showNotification('OTP sent to your email!', 'success');
        showStep(2);
        otpInput.focus();

    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        sendOtpBtn.disabled = false;
        sendOtpBtn.textContent = 'Send OTP';
    }
}

// Step 2: Verify OTP via backend
async function handleVerifyOtp() {
    const otp = otpInput.value.trim();

    if (!otp || otp.length !== 6) {
        showNotification('Please enter a valid 6-digit OTP', 'error');
        return;
    }

    try {
        verifyOtpBtn.disabled = true;
        verifyOtpBtn.textContent = 'Verifying...';

        const response = await fetch(`${API_BASE_URL}/auth/verify-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: userEmail, otp })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Invalid OTP');
        }

        resetToken = data.reset_token;
        showNotification('OTP verified!', 'success');
        showStep(3);
        newPasswordInput.focus();

    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        verifyOtpBtn.disabled = false;
        verifyOtpBtn.textContent = 'Verify OTP';
    }
}

// Step 3: Reset password via backend
async function handleResetPassword(e) {
    e.preventDefault();
    e.stopPropagation();

    const newPassword = newPasswordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    if (newPassword.length < 6) {
        showNotification('Password must be at least 6 characters', 'error');
        return;
    }
    if (newPassword !== confirmPassword) {
        showNotification('Passwords do not match', 'error');
        return;
    }

    try {
        resetPasswordBtn.disabled = true;
        resetPasswordBtn.textContent = 'Resetting...';

        const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: userEmail,
                reset_token: resetToken,
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to reset password');
        }

        showNotification('Password reset successfully! Redirecting...', 'success');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);

    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        resetPasswordBtn.disabled = false;
        resetPasswordBtn.textContent = 'Reset Password';
    }
}

async function handleResendOtp() {
    otpInput.value = '';
    await handleSendOtp();
}

function handleChangeEmail() {
    userEmail = '';
    resetToken = '';
    showStep(1);
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showNotification(message, type = 'info') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    notification.style.opacity = '1';

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => { notification.style.display = 'none'; }, 300);
    }, 4000);
}
