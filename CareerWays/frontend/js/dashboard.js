// dashboard.js - Dashboard page functionality

const API_BASE_URL = 'https://thecareerways-production.up.railway.app/api';
// DOM Elements
const welcomeName = document.getElementById('welcomeName');
const sidebarUserName = document.getElementById('sidebarUserName');
const sidebarAvatar = document.getElementById('sidebarAvatar');
const mobileUserName = document.getElementById('mobileUserName');
const logoutBtn = document.getElementById('logoutBtn');
const userRow = document.getElementById('userRow');
const startAssessmentBtn = document.getElementById('startAssessmentBtn');
const notification = document.getElementById('notification');

// Nav
const navDashboard = document.getElementById('navDashboard');
const navAssessments = document.getElementById('navAssessments');
const navSettings = document.getElementById('navSettings');

// Views
const viewDashboard = document.getElementById('viewDashboard');
const viewAssessments = document.getElementById('viewAssessments');
const viewSettings = document.getElementById('viewSettings');

// Mobile
const burgerBtn = document.getElementById('burgerBtn');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');

// Assessments lists
const dashboardAssessmentsList = document.getElementById('dashboardAssessmentsList');
const assessmentsList = document.getElementById('assessmentsList');

// Settings
const settingsName = document.getElementById('settingsName');
const settingsEmail = document.getElementById('settingsEmail');
const settingsAvatar = document.getElementById('settingsAvatar');
const settingsAccountType = document.getElementById('settingsAccountType');
const settingsMemberSince = document.getElementById('settingsMemberSince');

// Delete account button
const deleteAccountBtn = document.querySelector('.cw-btn-danger');

// View all link
const viewAllLink = document.getElementById('viewAllLink');

// ── Init ──────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    loadUserData();
    setupEventListeners();
    loadPreviousAssessments();
});

// ── Auth ──────────────────────────────────────
function checkAuthentication() {
    const userType = localStorage.getItem('userType');
    if (!userType) {
        window.location.href = 'index.html';
    }
}

// ── User data ─────────────────────────────────
function loadUserData() {
    const userType = localStorage.getItem('userType');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const name = user.name || (userType === 'guest' ? 'Guest User' : 'User');
    const initial = name.charAt(0).toUpperCase();

    if (welcomeName) welcomeName.textContent = name;
    if (sidebarUserName) sidebarUserName.textContent = name;
    if (sidebarAvatar) sidebarAvatar.textContent = initial;
    if (mobileUserName) mobileUserName.textContent = name;

    // Settings panel
    if (settingsName) settingsName.textContent = name;
    if (settingsAvatar) settingsAvatar.textContent = initial;
    if (settingsEmail) settingsEmail.textContent = user.email || '—';
    if (settingsAccountType) settingsAccountType.textContent = userType === 'guest' ? 'Guest' : 'Registered';
    if (settingsMemberSince) {
        const created = user.created_at ? new Date(user.created_at).toLocaleDateString() : '—';
        settingsMemberSince.textContent = created;
    }
}

// ── Event listeners ───────────────────────────
function setupEventListeners() {
    logoutBtn.addEventListener('click', handleLogout);
    
    // Toggle logout button on user name click
    if (userRow) {
        userRow.addEventListener('click', toggleLogoutButton);
    }
    
    // Close logout button when clicking outside
    document.addEventListener('click', (e) => {
        if (logoutBtn && userRow && !userRow.contains(e.target) && !logoutBtn.contains(e.target)) {
            logoutBtn.style.display = 'none';
        }
    });
    
    startAssessmentBtn.addEventListener('click', handleStartAssessment);

    navDashboard.addEventListener('click', (e) => { e.preventDefault(); switchView('dashboard'); });
    navAssessments.addEventListener('click', (e) => { e.preventDefault(); switchView('assessments'); });
    navSettings.addEventListener('click', (e) => { e.preventDefault(); switchView('settings'); });

    if (viewAllLink) viewAllLink.addEventListener('click', (e) => { e.preventDefault(); switchView('assessments'); });

    if (deleteAccountBtn) deleteAccountBtn.addEventListener('click', handleDeleteAccount);

    burgerBtn.addEventListener('click', toggleSidebar);
    overlay.addEventListener('click', closeSidebar);
}

// ── View switching ────────────────────────────
function switchView(name) {
    [viewDashboard, viewAssessments, viewSettings].forEach(v => v.classList.remove('active'));
    [navDashboard, navAssessments, navSettings].forEach(n => n.classList.remove('active'));

    if (name === 'dashboard') { viewDashboard.classList.add('active'); navDashboard.classList.add('active'); }
    if (name === 'assessments') { viewAssessments.classList.add('active'); navAssessments.classList.add('active'); }
    if (name === 'settings') { viewSettings.classList.add('active'); navSettings.classList.add('active'); }

    closeSidebar();
}

// ── Mobile sidebar ────────────────────────────
function toggleSidebar() {
    sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
    burgerBtn.classList.toggle('active');
}

function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
    burgerBtn.classList.remove('active');
}

// ── Toggle logout button ─────────────────────
function toggleLogoutButton() {
    const isVisible = logoutBtn.style.display === 'flex';
    logoutBtn.style.display = isVisible ? 'none' : 'flex';
}

// ── Load assessments ──────────────────────────
async function loadPreviousAssessments() {
    const userType = localStorage.getItem('userType');

    if (userType !== 'registered') {
        const msg = '<div class="cw-empty">Previous assessments are available for registered users only.</div>';
        if (dashboardAssessmentsList) dashboardAssessmentsList.innerHTML = msg;
        if (assessmentsList) assessmentsList.innerHTML = msg;
        return;
    }

    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`${API_BASE_URL}/assessments/list`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const data = await response.json();
            const assessments = data.assessments || [];

            if (assessments.length === 0) {
                const msg = '<div class="cw-empty">No previous assessments yet. Start your first assessment!</div>';
                if (dashboardAssessmentsList) dashboardAssessmentsList.innerHTML = msg;
                if (assessmentsList) assessmentsList.innerHTML = msg;
                return;
            }

            // Sort assessments by date (newest first)
            assessments.sort((a, b) => new Date(b.date) - new Date(a.date));
            
            const html = assessments.map(a => buildAssessmentCard(a)).join('');

            // Dashboard shows max 3
            if (dashboardAssessmentsList) {
                const preview = assessments.slice(0, 3).map(a => buildAssessmentCard(a)).join('');
                dashboardAssessmentsList.innerHTML = preview;
            }

            if (assessmentsList) assessmentsList.innerHTML = html;

        } else {
            const msg = '<div class="cw-empty">Unable to load assessments.</div>';
            if (dashboardAssessmentsList) dashboardAssessmentsList.innerHTML = msg;
            if (assessmentsList) assessmentsList.innerHTML = msg;
        }
    } catch (error) {
        console.error('Error loading assessments:', error);
        const msg = '<div class="cw-empty">Error loading assessments.</div>';
        if (dashboardAssessmentsList) dashboardAssessmentsList.innerHTML = msg;
        if (assessmentsList) assessmentsList.innerHTML = msg;
    }
}

function buildAssessmentCard(assessment) {
    const courses = assessment.courses || [];
    const date = new Date(assessment.date).toLocaleDateString();
    
    // Find the most compatible course within this assessment
    let mostCompatibleCourse = null;
    let highestScore = 0;
    
    courses.forEach(course => {
        const score = course.match_score || 0;
        if (score > highestScore) {
            highestScore = score;
            mostCompatibleCourse = course;
        }
    });
    
    const bestFitCourse = mostCompatibleCourse ? mostCompatibleCourse.name : (assessment.best_fit_course || 'Not available');
    const bestFitScore = Math.round(mostCompatibleCourse ? mostCompatibleCourse.match_score : (assessment.best_fit_score || 0));
    const courseCount = courses.length;

    return `
        <div class="assessment-item">
            <div class="assessment-item-header">
                <p class="assessment-date">${date}</p>
                <span class="assessment-score">${bestFitScore}% Compatible</span>
            </div>
            <span class="assessment-course-name featured-name">${bestFitCourse}</span>
            <p class="assessment-courses">${bestFitScore}% compatibility - Most suitable for you</p>
            <p class="assessment-courses">${courseCount} course(s) recommended</p>
            <div class="assessment-item-actions">
                <button onclick="viewAssessmentResult('${assessment.id}')">View Results</button>
                <button onclick="deleteAssessment('${assessment.id}')">Delete</button>
            </div>
        </div>
    `;
}

// ── View result ───────────────────────────────
function viewAssessmentResult(assessmentId) {
    sessionStorage.setItem('assessmentId', assessmentId);
    window.location.href = 'results.html';
}

// ── Delete assessment ─────────────────────────
async function deleteAssessment(assessmentId) {
    if (!confirm('Are you sure you want to delete this assessment?')) return;

    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`${API_BASE_URL}/assessments/${assessmentId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            showNotification('Assessment deleted successfully', 'success');
            loadPreviousAssessments();
        } else {
            showNotification('Error deleting assessment', 'error');
        }
    } catch (error) {
        console.error('Error deleting assessment:', error);
        showNotification('An error occurred', 'error');
    }
}

// ── Top Courses (system-wide) ─────────────────

/**
 * Derives an abbreviation from a course name.
 * Skips common filler words so "Bachelor of Science in Computer Science" → "BSCS"
 */
function abbreviateCourseName(name) {
    const skip = new Set(['of', 'in', 'and', 'the', 'for', 'a', 'an', 'with', 'to']);
    return name
        .split(/\s+/)
        .filter(w => !skip.has(w.toLowerCase()))
        .map(w => w.charAt(0).toUpperCase())
        .join('');
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}




// ── Start assessment ──────────────────────────
function handleStartAssessment() {
    showNotification('Starting assessment...', 'info');
    setTimeout(() => { window.location.href = 'assessment.html'; }, 800);
}

// ── Logout ────────────────────────────────────
function handleLogout(e) {
    e.preventDefault();
    if (confirm('Are you sure you want to log out?')) {
        localStorage.clear();
        sessionStorage.clear();
        showNotification('Logged out successfully', 'success');
        setTimeout(() => { window.location.href = 'index.html'; }, 800);
    }
}

// ── Delete Account ────────────────────────────
async function handleDeleteAccount() {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone and will permanently remove all your data.')) {
        return;
    }

    if (!confirm('This is your final warning. All your assessments, favorites, and profile data will be permanently deleted. Are you absolutely sure?')) {
        return;
    }

    // Ask for password confirmation
    const password = prompt('Please enter your password to confirm account deletion:');
    if (!password || password.trim() === '') {
        showNotification('Password is required to delete account', 'error');
        return;
    }

    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`${API_BASE_URL}/users/delete-account`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password: password.trim() })
        });

        if (response.ok) {
            showNotification('Account deleted successfully', 'success');
            localStorage.clear();
            sessionStorage.clear();
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        } else {
            const errorData = await response.json();
            showNotification(errorData.message || 'Failed to delete account', 'error');
        }
    } catch (error) {
        console.error('Error deleting account:', error);
        showNotification('An error occurred while deleting your account', 'error');
    }
}

// ── Notification ──────────────────────────────
function showNotification(message, type = 'info') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    notification.style.opacity = '1';
    notification.style.visibility = 'visible';

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.style.display = 'none';
            notification.style.visibility = 'hidden';
        }, 300);
    }, 3000);
}
