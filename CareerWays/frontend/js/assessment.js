// assessment.js - Assessment page functionality

const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const backBtn = document.getElementById('backBtn');
const userNameDisplay = document.getElementById('userNameDisplay');
const logoutBtn = document.getElementById('logoutBtn');
const chatMessages = document.getElementById('chatMessages');
const assessmentForm = document.getElementById('assessmentForm');
const userResponse = document.getElementById('userResponse');
const sendBtn = document.getElementById('sendBtn');
const charCount = document.getElementById('charCount');
const loadingIndicator = document.getElementById('loadingIndicator');
const notification = document.getElementById('notification');

let currentAssessmentId = null;
let isProcessing = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    setupEventListeners();
    loadUserData();
    displayInitialMessage();
});

// Setup Event Listeners
function setupEventListeners() {
    backBtn.addEventListener('click', handleBack);
    logoutBtn.addEventListener('click', handleLogout);
    assessmentForm.addEventListener('submit', handleSubmitAssessment);
    userResponse.addEventListener('input', updateCharCount);
}

// Check Authentication
function checkAuthentication() {
    const userType = localStorage.getItem('userType');

    if (!userType) {
        window.location.href = 'index.html';
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
    }
}

// Display Initial Message
function displayInitialMessage() {
    const hint = document.createElement('div');
    hint.className = 'chat-greeting-hint';
    hint.textContent = 'Tell us about your interests, skills, experience, and goals.';
    chatMessages.appendChild(hint);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Create Message Element
function createMessage(text, sender = 'bot') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'bot' ? 'AI' : 'You';

    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    return messageDiv;
}

function appendRecommendationsToChat(courses) {
    if (!courses || courses.length === 0) {
        return;
    }

    const wrapper = document.createElement('div');
    wrapper.className = 'message bot';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'AI';

    const content = document.createElement('div');
    content.className = 'message-content';

    const lines = courses.map((course, index) =>
        `${index + 1}. ${course.name} (${Math.round(course.match_score || 0)}% match)`
    );
    content.textContent = `Top recommended courses:\n${lines.join('\n')}`;
    content.style.whiteSpace = 'pre-line';

    wrapper.appendChild(avatar);
    wrapper.appendChild(content);
    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendAnotherAssessmentQuestion() {
    const wrapper = document.createElement('div');
    wrapper.className = 'message bot';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'AI';

    const content = document.createElement('div');
    content.className = 'message-content chat-followup';

    const question = document.createElement('p');
    question.className = 'chat-followup-question';
    question.textContent = 'Do you want to take another assessment?';

    const actions = document.createElement('div');
    actions.className = 'chat-followup-actions';

    const yesBtn = document.createElement('button');
    yesBtn.className = 'btn btn-primary';
    yesBtn.type = 'button';
    yesBtn.textContent = 'Yes, take another';
    yesBtn.addEventListener('click', handleAnotherAssessment);

    const noBtn = document.createElement('button');
    noBtn.className = 'btn btn-secondary';
    noBtn.type = 'button';
    noBtn.textContent = 'No, view full results';
    noBtn.addEventListener('click', handleViewResults);

    actions.appendChild(yesBtn);
    actions.appendChild(noBtn);
    content.appendChild(question);
    content.appendChild(actions);
    wrapper.appendChild(avatar);
    wrapper.appendChild(content);

    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Update Character Count
function updateCharCount() {
    charCount.textContent = userResponse.value.length;

    if (userResponse.value.length > 1000) {
        userResponse.value = userResponse.value.substring(0, 1000);
        charCount.textContent = '1000';
    }
}

// Handle Submit Assessment
async function handleSubmitAssessment(e) {
    e.preventDefault();

    if (isProcessing) {
        return;
    }

    const response = userResponse.value.trim();

    if (response.length === 0) {
        showNotification('Please enter your response', 'warning');
        return;
    }

    if (response.length < 20) {
        showNotification('Please provide more details (at least 20 characters)', 'warning');
        return;
    }

    // Display user message
    const userMessage = createMessage(response, 'user');
    chatMessages.appendChild(userMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Clear input
    userResponse.value = '';
    charCount.textContent = '0';
    assessmentForm.style.display = 'none';
    loadingIndicator.style.display = 'flex';

    isProcessing = true;

    try {
        const userType = localStorage.getItem('userType');
        const token = localStorage.getItem('token');

        const response_obj = await fetch(`${API_BASE_URL}/assessments/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(userType === 'registered' && { 'Authorization': `Bearer ${token}` })
            },
            body: JSON.stringify({
                response: response,
                userType: userType
            })
        });

        const data = await response_obj.json();

        if (response_obj.ok) {
            // Store assessment ID for results page
            currentAssessmentId = data.assessment_id;
            sessionStorage.setItem('assessmentId', data.assessment_id);

            // Display bot response
            const botMessage = createMessage(
                "Thank you for your response! We've analyzed your profile and recommendations are ready.",
                'bot'
            );
            chatMessages.appendChild(botMessage);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            appendRecommendationsToChat(data.courses);
            appendAnotherAssessmentQuestion();

            loadingIndicator.style.display = 'none';
            assessmentForm.style.display = 'none';
        } else {
            showNotification(data.message || 'Error analyzing response', 'error');
            loadingIndicator.style.display = 'none';
            assessmentForm.style.display = 'flex';
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('An error occurred. Please try again.', 'error');
        loadingIndicator.style.display = 'none';
        assessmentForm.style.display = 'flex';
    } finally {
        isProcessing = false;
    }
}

// Handle Another Assessment
function handleAnotherAssessment() {
    // Reset chat
    chatMessages.innerHTML = '';
    displayInitialMessage();

    // Reset form
    userResponse.value = '';
    charCount.textContent = '0';
    assessmentForm.style.display = 'flex';
    loadingIndicator.style.display = 'none';
    isProcessing = false;
}

// Handle View Results
function handleViewResults() {
    if (currentAssessmentId) {
        sessionStorage.setItem('assessmentId', currentAssessmentId);
    }

    window.location.href = 'results.html';
}

// Handle Back
function handleBack() {
    if (confirm('Are you sure you want to go back? Your current assessment will not be saved.')) {
        window.location.href = 'dashboard.html';
    }
}

// Handle Logout
function handleLogout() {
    if (confirm('Are you sure you want to log out?')) {
        localStorage.clear();
        sessionStorage.clear();
        showNotification('Logged out successfully', 'success');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1000);
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