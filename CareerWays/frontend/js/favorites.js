// favorites.js - Favorites page functionality

const API_BASE_URL = window.__CW_API_BASE__;

// DOM
const sidebarAvatar      = document.getElementById('sidebarAvatar');
const sidebarUserName    = document.getElementById('sidebarUserName');
const mobileUserName     = document.getElementById('mobileUserName');
const logoutBtn          = document.getElementById('logoutBtn');
const burgerBtn          = document.getElementById('burgerBtn');
const sidebar            = document.getElementById('sidebar');
const overlay            = document.getElementById('overlay');
const favoritesGrid      = document.getElementById('favoritesGrid');
const emptyState         = document.getElementById('emptyState');
const noResults          = document.getElementById('noResults');
const favCountBadge      = document.getElementById('favCountBadge');
const searchInput        = document.getElementById('searchInput');
const sortSelect         = document.getElementById('sortSelect');
const courseModal        = document.getElementById('courseModal');
const modalBody          = document.getElementById('modalBody');
const modalClose         = document.getElementById('modalClose');
const notification       = document.getElementById('notification');

let allFavorites = [];   // raw data from API
let filtered     = [];   // after search/sort

// ── Init ──────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    loadUserData();
    setupEventListeners();
    loadFavorites();
});

// ── Auth ──────────────────────────────────────
function checkAuthentication() {
    const userType = localStorage.getItem('userType');
    if (!userType) { window.location.href = 'index.html'; return; }
    if (userType !== 'registered') { window.location.href = 'dashboard.html'; }
}

// ── User data ─────────────────────────────────
function loadUserData() {
    const user    = JSON.parse(localStorage.getItem('user') || '{}');
    const name    = user.name || 'User';
    const initial = name.charAt(0).toUpperCase();

    if (sidebarAvatar)   sidebarAvatar.textContent   = initial;
    if (sidebarUserName) sidebarUserName.textContent = name;
    if (mobileUserName)  mobileUserName.textContent  = name;
}

// ── Event listeners ───────────────────────────
function setupEventListeners() {
    logoutBtn.addEventListener('click', handleLogout);
    burgerBtn.addEventListener('click', toggleSidebar);
    overlay.addEventListener('click', closeSidebar);
    modalClose.addEventListener('click', closeModal);
    courseModal.addEventListener('click', (e) => { if (e.target === courseModal) closeModal(); });

    searchInput.addEventListener('input', applyFilters);
    sortSelect.addEventListener('change', applyFilters);
}

// ── Load favorites ────────────────────────────
async function loadFavorites() {
    showSkeletons();

    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`${API_BASE_URL}/favorites`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            showNotification('Could not load favorites', 'error');
            showEmpty();
            return;
        }

        const data = await response.json();
        allFavorites = data.favorites || [];
        applyFilters();

    } catch (err) {
        console.error('Error loading favorites:', err);
        showNotification('An error occurred loading favorites', 'error');
        showEmpty();
    }
}

// ── Filter & sort ─────────────────────────────
function applyFilters() {
    const query = searchInput.value.trim().toLowerCase();
    const sort  = sortSelect.value;

    filtered = allFavorites.filter(fav => {
        const course = fav.course || fav;
        const name   = (course.name || '').toLowerCase();
        const desc   = (course.description || '').toLowerCase();
        return !query || name.includes(query) || desc.includes(query);
    });

    // Sort
    filtered.sort((a, b) => {
        const ca = a.course || a;
        const cb = b.course || b;
        if (sort === 'name')    return (ca.name || '').localeCompare(cb.name || '');
        if (sort === 'oldest')  return new Date(a.saved_at || 0) - new Date(b.saved_at || 0);
        return new Date(b.saved_at || 0) - new Date(a.saved_at || 0); // newest
    });

    renderGrid();
}

// ── Render grid ───────────────────────────────
function renderGrid() {
    favoritesGrid.innerHTML = '';

    // Update badge
    favCountBadge.textContent = `${allFavorites.length} saved`;

    if (allFavorites.length === 0) {
        emptyState.style.display = 'flex';
        noResults.style.display  = 'none';
        return;
    }

    emptyState.style.display = 'none';

    if (filtered.length === 0) {
        noResults.style.display = 'flex';
        return;
    }

    noResults.style.display = 'none';

    // Group favorites by priority
    const firstChoices = filtered.filter(f => f.priority === 'first_choice');
    const secondChoices = filtered.filter(f => f.priority === 'second_choice');
    const justSaved = filtered.filter(f => !f.priority || f.priority === 'saved');

    // Render sections
    let cardIndex = 0;
    
    // 1st Choice Section
    if (firstChoices.length > 0) {
        const sectionHeader = document.createElement('div');
        sectionHeader.className = 'fav-section-header';
        sectionHeader.innerHTML = `
            <h3 class="fav-section-title">
                <span class="section-badge badge-gold">1</span>
                1st Choice (${firstChoices.length})
            </h3>
        `;
        favoritesGrid.appendChild(sectionHeader);
        
        firstChoices.forEach((fav) => {
            const course = fav.course || fav;
            const card   = buildCard(fav, course, cardIndex++, true);
            favoritesGrid.appendChild(card);
        });
    }

    // 2nd Choice Section
    if (secondChoices.length > 0) {
        const sectionHeader = document.createElement('div');
        sectionHeader.className = 'fav-section-header';
        sectionHeader.innerHTML = `
            <h3 class="fav-section-title">
                <span class="section-badge badge-silver">2</span>
                2nd Choice (${secondChoices.length})
            </h3>
        `;
        favoritesGrid.appendChild(sectionHeader);
        
        secondChoices.forEach((fav) => {
            const course = fav.course || fav;
            const card   = buildCard(fav, course, cardIndex++, true);
            favoritesGrid.appendChild(card);
        });
    }

    // Just Saved Section
    if (justSaved.length > 0) {
        const sectionHeader = document.createElement('div');
        sectionHeader.className = 'fav-section-header';
        sectionHeader.innerHTML = `
            <h3 class="fav-section-title">
                <span class="section-badge badge-coral">★</span>
                Saved (${justSaved.length})
            </h3>
        `;
        favoritesGrid.appendChild(sectionHeader);
        
        justSaved.forEach((fav) => {
            const course = fav.course || fav;
            const card   = buildCard(fav, course, cardIndex++, false);
            favoritesGrid.appendChild(card);
        });
    }
}

// ── Build card ────────────────────────────────
function buildCard(fav, course, index, isPriority = false) {
    const savedDate = fav.saved_at
        ? new Date(fav.saved_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
        : '';

    const card = document.createElement('div');
    card.className = 'fav-card' + (isPriority ? ' priority-card' : '');
    card.style.animationDelay = `${index * 40}ms`;

    // Priority badge
    let priorityBadge = '';
    if (fav.priority === 'first_choice') {
        priorityBadge = '<span class="priority-badge badge-first">1st</span>';
    } else if (fav.priority === 'second_choice') {
        priorityBadge = '<span class="priority-badge badge-second">2nd</span>';
    }

    // Tags
    const tags = [];
    if (course.duration)    tags.push(course.duration);
    if (course.difficulty)  tags.push(course.difficulty);
    if (course.career_path) tags.push(course.career_path);
    const tagsHTML = tags.map(t => `<span class="fav-tag">${t}</span>`).join('');

    card.innerHTML = `
        <div class="fav-card-header">
            <div class="card-header-left">
                ${priorityBadge}
                <h4 class="fav-card-title">${course.name || 'Unnamed Course'}</h4>
            </div>
            <button class="fav-card-remove" title="Remove from favorites" onclick="removeFavorite('${fav.id || course.id}', this)">×</button>
        </div>
        <div class="fav-card-body">
            <p class="fav-card-desc">${course.description || 'No description available.'}</p>
            <div class="fav-card-meta">${tagsHTML}</div>
        </div>
        ${savedDate ? `<div class="fav-saved-date">Saved ${savedDate}</div>` : ''}
        <div class="fav-card-footer">
            <button onclick="openModal(${index})">View Details</button>
            <button class="primary" onclick="goToAssessment()">Take Assessment</button>
        </div>
    `;

    return card;
}

// ── Remove favorite ───────────────────────────
async function removeFavorite(favoriteId, btnEl) {
    if (!confirm('Remove this course from favorites?')) return;

    const token = localStorage.getItem('token');

    // Optimistic UI: fade out the card
    const card = btnEl.closest('.fav-card');
    if (card) { card.style.opacity = '0.4'; card.style.pointerEvents = 'none'; }

    try {
        const response = await fetch(`${API_BASE_URL}/favorites/${favoriteId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            allFavorites = allFavorites.filter(f => (f.id || f.course?.id) !== favoriteId);
            showNotification('Removed from favorites', 'success');
            applyFilters();
        } else {
            // Restore card
            if (card) { card.style.opacity = '1'; card.style.pointerEvents = ''; }
            showNotification('Could not remove favorite', 'error');
        }
    } catch (err) {
        console.error('Error removing favorite:', err);
        if (card) { card.style.opacity = '1'; card.style.pointerEvents = ''; }
        showNotification('An error occurred', 'error');
    }
}

// ── Modal ─────────────────────────────────────
function openModal(index) {
    const fav    = filtered[index];
    const course = fav.course || fav;

    const skillsHTML = (course.skills_learned && course.skills_learned.length)
        ? `<div class="fav-modal-section">
               <h4>Skills You'll Learn</h4>
               <ul>${course.skills_learned.map(s => `<li>${s}</li>`).join('')}</ul>
           </div>`
        : '';

    const prospectsHTML = course.career_prospects
        ? `<div class="fav-modal-section"><h4>Career Prospects</h4><p>${course.career_prospects}</p></div>`
        : '';

    const requirementsHTML = course.requirements
        ? `<div class="fav-modal-section"><h4>Requirements</h4><p>${course.requirements}</p></div>`
        : '';

    const tags = [];
    if (course.duration)    tags.push(course.duration);
    if (course.difficulty)  tags.push(course.difficulty);
    if (course.career_path) tags.push(course.career_path);

    modalBody.innerHTML = `
        <div class="fav-modal-header">
            <h3>${course.name || 'Course Details'}</h3>
            ${tags.map(t => `<span class="fav-modal-badge">${t}</span>`).join(' ')}
        </div>
        <div class="fav-modal-body">
            ${course.description ? `<div class="fav-modal-section"><h4>Overview</h4><p>${course.description}</p></div>` : ''}
            ${skillsHTML}
            ${prospectsHTML}
            ${requirementsHTML}
        </div>
        <div class="fav-modal-actions">
            <button class="btn-remove" onclick="removeFavorite('${fav.id || course.id}', document.querySelector('.fav-modal-close')); closeModal();">Remove Favorite</button>
            <button class="btn-close" onclick="closeModal()">Close</button>
        </div>
    `;

    courseModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    courseModal.style.display = 'none';
    document.body.style.overflow = '';
}

// ── Helpers ───────────────────────────────────
function goToAssessment() {
    window.location.href = 'assessment.html';
}

function showEmpty() {
    favoritesGrid.innerHTML = '';
    emptyState.style.display = 'flex';
}

function showSkeletons() {
    favoritesGrid.innerHTML = Array(3).fill(0).map(() => `
        <div class="fav-skeleton">
            <div class="fav-skeleton-header"></div>
            <div class="fav-skeleton-body">
                <div class="fav-skeleton-line"></div>
                <div class="fav-skeleton-line"></div>
                <div class="fav-skeleton-line short"></div>
            </div>
        </div>
    `).join('');
    emptyState.style.display = 'none';
    noResults.style.display  = 'none';
}

// ── Sidebar ───────────────────────────────────
function toggleSidebar() {
    sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
}

function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
}

// ── Logout ────────────────────────────────────
function handleLogout(e) {
    e.preventDefault();
    if (confirm('Are you sure you want to log out?')) {
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = 'index.html';
    }
}

// ── Notification ──────────────────────────────
function showNotification(message, type = 'info') {
    notification.textContent = message;
    notification.className   = `notification ${type}`;
    notification.style.display    = 'block';
    notification.style.opacity    = '1';
    notification.style.visibility = 'visible';

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.style.display    = 'none';
            notification.style.visibility = 'hidden';
        }, 300);
    }, 3000);
}
