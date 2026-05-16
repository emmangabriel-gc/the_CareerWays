// results.js - Results page functionality

const API_BASE_URL = window.__CW_API_BASE__;

// DOM Elements
const userNameDisplay = document.getElementById('userNameDisplay');
const logoutBtn = document.getElementById('logoutBtn');
const profileAnalysis = document.getElementById('profileAnalysis');
const coursesList = document.getElementById('coursesList');
const anotherAssessmentBtn = document.getElementById('anotherAssessmentBtn');
const backToDashboardBtn = document.getElementById('backToDashboardBtn');
const notification = document.getElementById('notification');

let currentAssessmentData = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    setupEventListeners();
    loadUserData();
    loadAssessmentResults();
});

// Setup Event Listeners
function setupEventListeners() {
    logoutBtn.addEventListener('click', handleLogout);
    anotherAssessmentBtn.addEventListener('click', handleAnotherAssessment);
    backToDashboardBtn.addEventListener('click', handleBackToDashboard);

}

// Check Authentication
function checkAuthentication() {
    const userType = localStorage.getItem('userType');

    if (!userType) {
        window.location.href = 'login.html';
        return;
    }
}

// Load User Data
function loadUserData() {
    const userType = localStorage.getItem('userType');

    if (userType === 'registered') {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        userNameDisplay.textContent = user.name || 'User';
    } else if (userType === 'guest') {
        userNameDisplay.textContent = 'Guest';
        if (isGuestAssessmentBlocked() && anotherAssessmentBtn) {
            anotherAssessmentBtn.disabled = true;
            anotherAssessmentBtn.textContent = 'Guest limit reached';
        }
    }
}

// Load Assessment Results
async function loadAssessmentResults() {
    const assessmentId = sessionStorage.getItem('assessmentId');

    if (!assessmentId) {
        showNotification('No assessment found', 'error');
        return;
    }

    const userType = localStorage.getItem('userType');
    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`${API_BASE_URL}/assessments/${assessmentId}`, {
            headers: {
                ...(userType === 'registered' && { 'Authorization': `Bearer ${token}` })
            }
        });

        if (response.ok) {
            const data = await response.json();
            currentAssessmentData = data;

            displayProfileAnalysis(data);
            displayRecommendedCourses(data);
        } else {
            showNotification('Error loading assessment results', 'error');
        }
    } catch (error) {
        console.error('Error loading results:', error);
        showNotification('An error occurred while loading results', 'error');
    }
}

// Display Profile Analysis
function displayProfileAnalysis(data) {
    let analysisHTML = '';

    if (data.skills && data.skills.length > 0) {
        analysisHTML += `
            <div class="analysis-item">
                <strong>Identified Skills:</strong>
                ${data.skills.map(skill => `<span style="display: inline-block; margin-right: 0.5rem; padding: 0.25rem 0.75rem; background-color: rgba(255, 87, 34, 0.1); border-radius: 4px; font-size: 0.9rem;">${skill}</span>`).join('')}
            </div>
        `;
    }

    if (data.interests && data.interests.length > 0) {
        analysisHTML += `
            <div class="analysis-item">
                <strong>Your Interests:</strong>
                <p>${data.interests.join(', ')}</p>
            </div>
        `;
    }

    if (data.sentiment) {
        analysisHTML += `
            <div class="analysis-item">
                <strong>Career Motivation:</strong>
                <p>${data.sentiment}</p>
            </div>
        `;
    }

    if (data.experience) {
        analysisHTML += `
            <div class="analysis-item">
                <strong>Your Experience:</strong>
                <p>${data.experience}</p>
            </div>
        `;
    }

    // Add recommendation quality indicator
    if (data.recommendation_quality) {
        analysisHTML += `
            <div class="analysis-item">
                <strong>Analysis Quality:</strong>
                <div class="quality-indicator">
                    <span class="quality-badge ${data.recommendation_quality.uses_semantic_embedding ? 'semantic-enabled' : 'tfidf-only'}">
                        ${data.recommendation_quality.uses_semantic_embedding ? '🧠 Semantic AI' : '📊 Traditional'}
                    </span>
                    <span class="quality-stats">
                        ${data.recommendation_quality.relevant_matches} relevant courses found from ${data.recommendation_quality.total_analyzed} analyzed
                    </span>
                </div>
            </div>
        `;
    }

    profileAnalysis.innerHTML = analysisHTML;
}

// Display Recommended Courses
function displayRecommendedCourses(data) {
    const courses = data.courses || [];
    const embeddingData = data.embedding_data || {};

    if (courses.length === 0) {
        coursesList.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-light);">No course recommendations available at this time.</p>';
        return;
    }

    coursesList.innerHTML = '';

    courses.forEach((course, index) => {
        const matchScore = Math.max(0, Math.min(100, Math.round(course.match_score || 0)));
        const semanticScore = Math.round(course.semantic_score || 0);
        const relevanceScore = Math.round(course.relevance_score || 0);
        const courseEmbeddingData = embeddingData[course.id] || {};

        const courseCard = document.createElement('div');
        courseCard.className = 'course-card';
        courseCard.innerHTML = `
            <div class="course-card-header">
                <h4>${course.name}</h4>
                <div class="course-match">
                    <span class="match-percentage">${matchScore}% Match</span>
                </div>
            </div>
            <div class="course-card-body">
                <div class="match-progress">
                    <div class="match-progress-label">
                        <span>Overall Compatibility</span>
                        <span>${matchScore}%</span>
                    </div>
                    <div class="match-progress-track">
                        <div class="match-progress-fill" style="width: ${matchScore}%;"></div>
                    </div>
                </div>
                
                <!-- Vector Embedding Visualization -->
                <div class="embedding-analysis">
                    <div class="embedding-title">🧠 AI Analysis Breakdown:</div>
                    <div class="embedding-metrics">
                        <div class="metric-item">
                            <span class="metric-label">Semantic Match:</span>
                            <div class="metric-bar">
                                <div class="metric-fill semantic-fill" style="width: ${semanticScore}%"></div>
                                <span class="metric-value">${semanticScore}%</span>
                            </div>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Relevance Score:</span>
                            <div class="metric-bar">
                                <div class="metric-fill relevance-fill" style="width: ${relevanceScore}%"></div>
                                <span class="metric-value">${relevanceScore}%</span>
                            </div>
                        </div>
                        ${courseEmbeddingData.skill_match !== undefined ? `
                        <div class="metric-item">
                            <span class="metric-label">Skill Match:</span>
                            <div class="metric-bar">
                                <div class="metric-fill skill-fill" style="width: ${Math.round(courseEmbeddingData.skill_match)}%"></div>
                                <span class="metric-value">${Math.round(courseEmbeddingData.skill_match)}%</span>
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                <p class="course-description">${course.description || 'A promising course for your profile.'}</p>
                <div class="course-details">
                    <div class="detail-item">
                        <span class="detail-label">Duration:</span> ${course.duration || 'Variable'}
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Difficulty:</span> ${course.difficulty || 'Intermediate'}
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Career Path:</span> ${course.career_path || 'Professional Development'}
                    </div>
                </div>
            </div>
            <div class="course-card-footer">
                <button class="btn-primary" onclick="showSaveChoiceModal('${course.id}')">Save</button>
            </div>
        `;
        coursesList.appendChild(courseCard);
    });
}


// Show Save Choice Modal
function showSaveChoiceModal(courseId) {
    const modal = document.createElement('div');
    modal.className = 'choice-modal';
    modal.id = 'saveChoiceModal';
    modal.innerHTML = `
        <div class="choice-modal-content">
            <h3>Save Course</h3>
            <p>How would you like to save this course?</p>
            <div class="choice-buttons">
                <button class="btn-choice btn-first" onclick="saveFavoriteCourse('${courseId}', 'first_choice')">
                    <span class="choice-icon">1</span>
                    <span class="choice-label">1st Choice</span>
                </button>
                <button class="btn-choice btn-second" onclick="saveFavoriteCourse('${courseId}', 'second_choice')">
                    <span class="choice-icon">2</span>
                    <span class="choice-label">2nd Choice</span>
                </button>
                <button class="btn-choice btn-save" onclick="saveFavoriteCourse('${courseId}', 'saved')">
                    <span class="choice-icon">★</span>
                    <span class="choice-label">Just Save</span>
                </button>
            </div>
            <button class="btn-cancel" onclick="closeSaveChoiceModal()">Cancel</button>
        </div>
    `;
    document.body.appendChild(modal);
}

// Close Save Choice Modal
function closeSaveChoiceModal() {
    const modal = document.getElementById('saveChoiceModal');
    if (modal) {
        modal.remove();
    }
}

// Save Favorite Course with Priority
async function saveFavoriteCourse(courseId, priority = 'saved') {
    const userType = localStorage.getItem('userType');

    if (userType === 'guest') {
        showNotification('Please log in to save favorite courses', 'warning');
        return;
    }

    // Close the choice modal if open
    closeSaveChoiceModal();

    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`${API_BASE_URL}/favorites`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                course_id: courseId,
                priority: priority
            })
        });

        if (response.ok) {
            const priorityLabel = {
                'first_choice': '1st Choice',
                'second_choice': '2nd Choice',
                'saved': 'Saved'
            }[priority];
            showNotification(`Course saved as ${priorityLabel}!`, 'success');
        } else {
            showNotification('Error saving course', 'error');
        }
    } catch (error) {
        console.error('Error saving favorite:', error);
        showNotification('An error occurred', 'error');
    }
}

// Handle Another Assessment
function handleAnotherAssessment() {
    const userType = localStorage.getItem('userType');
    if (userType === 'guest' && isGuestAssessmentBlocked()) {
        showNotification('Guest users may take only one assessment per device. Please sign up or log in to continue.', 'warning');
        return;
    }

    showGlobalLoading('Opening assessment...');
    sessionStorage.removeItem('assessmentId');
    window.location.href = 'assessment.html';
}

// Handle Back to Dashboard
function handleBackToDashboard() {
    sessionStorage.removeItem('assessmentId');
    window.location.href = 'dashboard.html';
}

// Handle Logout
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
        showNotification('Logged out successfully', 'success');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1000);
    });
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
