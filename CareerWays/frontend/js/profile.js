const API_BASE_URL = 'http://localhost:5000/api';

const backBtn = document.getElementById('backBtn');
const logoutBtn = document.getElementById('logoutBtn');
const userNameDisplay = document.getElementById('userNameDisplay');
const profileForm = document.getElementById('profileForm');
const passwordForm = document.getElementById('passwordForm');
const deleteForm = document.getElementById('deleteForm');
const notification = document.getElementById('notification');

const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const oldPasswordInput = document.getElementById('oldPassword');
const newPasswordInput = document.getElementById('newPassword');
const confirmPasswordInput = document.getElementById('confirmPassword');
const deletePasswordInput = document.getElementById('deletePassword');

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
    backBtn.addEventListener('click', () => window.location.href = 'dashboard.html');
    logoutBtn.addEventListener('click', handleLogout);
    profileForm.addEventListener('submit', handleProfileUpdate);
    passwordForm.addEventListener('submit', handlePasswordChange);
    deleteForm.addEventListener('submit', handleDeleteAccount);
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

        nameInput.value = user.name || '';
        emailInput.value = user.email || '';
        userNameDisplay.textContent = user.name || 'User';
        localStorage.setItem('user', JSON.stringify(user));
    } catch (error) {
        console.error('Error loading profile:', error);
        showNotification('An error occurred while loading profile', 'error');
    }
}

async function handleProfileUpdate(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`${API_BASE_URL}/users/profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                name: nameInput.value.trim(),
                email: emailInput.value.trim()
            })
        });

        const data = await response.json();
        if (!response.ok) {
            showNotification(data.message || 'Failed to update profile', 'error');
            return;
        }

        localStorage.setItem('user', JSON.stringify(data.user));
        userNameDisplay.textContent = data.user.name || 'User';
        showNotification('Profile updated successfully', 'success');
    } catch (error) {
        console.error('Error updating profile:', error);
        showNotification('An error occurred while updating profile', 'error');
    }
}

async function handlePasswordChange(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    const oldPassword = oldPasswordInput.value;
    const newPassword = newPasswordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    if (newPassword !== confirmPassword) {
        showNotification('New passwords do not match', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/change-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword
            })
        });

        const data = await response.json();
        if (!response.ok) {
            showNotification(data.message || 'Failed to change password', 'error');
            return;
        }

        oldPasswordInput.value = '';
        newPasswordInput.value = '';
        confirmPasswordInput.value = '';
        showNotification('Password changed successfully', 'success');
    } catch (error) {
        console.error('Error changing password:', error);
        showNotification('An error occurred while changing password', 'error');
    }
}

async function handleDeleteAccount(e) {
    e.preventDefault();
    const token = localStorage.getItem('token');

    if (!confirm('Are you sure? This will permanently delete your account.')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/delete-account`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ password: deletePasswordInput.value })
        });

        const data = await response.json();
        if (!response.ok) {
            showNotification(data.message || 'Failed to delete account', 'error');
            return;
        }

        localStorage.clear();
        sessionStorage.clear();
        window.location.href = 'index.html';
    } catch (error) {
        console.error('Error deleting account:', error);
        showNotification('An error occurred while deleting account', 'error');
    }
}

function handleLogout() {
    if (!confirm('Are you sure you want to log out?')) {
        return;
    }
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = 'index.html';
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