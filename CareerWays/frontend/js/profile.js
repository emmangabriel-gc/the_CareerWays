const API_BASE_URL = window.__CW_API_BASE__;

const backBtn = document.getElementById('backBtn');
const logoutBtn = document.getElementById('logoutBtn');
const resetPasswordBtn = document.getElementById('resetPasswordBtn');
const profileName = document.getElementById('profileName');
const profileEmail = document.getElementById('profileEmail');
const notification = document.getElementById('notification');

document.addEventListener('DOMContentLoaded', () => {
    const userType = localStorage.getItem('userType');
    if (userType !== 'registered') {
        window.location.href = 'dashboard.html';
        return;
    }

    setupEventListeners();
    loadProfile();
});

function setupEventListeners() {
    backBtn.addEventListener('click', () => {
        window.location.href = 'dashboard.html';
    });

    logoutBtn.addEventListener('click', handleLogout);

    resetPasswordBtn.addEventListener('click', () => {
        // Log out and redirect to forgot password page
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = 'forgot-password.html';
    });
}

async function loadProfile() {
    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`${API_BASE_URL}/users/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            showNotification('Unable to load profile', 'error');
            return;
        }

        const data = await response.json();
        const user = data.user || {};

        profileName.textContent = user.name || '—';
        profileEmail.textContent = user.email || '—';

        localStorage.setItem('user', JSON.stringify(user));
    } catch (error) {
        console.error('Error loading profile:', error);
        showNotification('An error occurred while loading profile', 'error');
    }
}

function handleLogout() {
    showConfirm('Are you sure you want to log out?', {
        title: 'Confirm logout',
        confirmText: 'Log out',
        cancelText: 'Stay logged in',
        danger: true
    }).then((confirmed) => {
        if (!confirmed) return;
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = 'login.html';
    });
}

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
