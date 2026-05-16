// common.js - Shared frontend utilities for loading UI and guest limits

function initGlobalLoadingOverlay() {
    if (document.getElementById('globalLoadingOverlay')) return;

    const style = document.createElement('style');
    style.textContent = `
        #globalLoadingOverlay {
            position: fixed;
            inset: 0;
            z-index: 9999;
            display: none;
            align-items: center;
            justify-content: center;
            background: rgba(0, 0, 0, 0.55);
            backdrop-filter: blur(2px);
        }
        #globalLoadingOverlay.active {
            display: flex;
        }
        #globalLoadingOverlay .loading-card {
            max-width: 360px;
            width: 100%;
            padding: 1.75rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.98);
            box-shadow: 0 22px 70px rgba(0, 0, 0, 0.18);
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 1rem;
        }
        #globalLoadingOverlay .loading-card .wrap {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 0;
        }
        #globalLoadingOverlay .line-svg {
            width: 100%;
            height: auto;
            display: block;
        }
        #globalLoadingOverlay .line-path {
            fill: none;
            stroke: #E85B35;
            stroke-width: 9;
            stroke-linecap: round;
            stroke-linejoin: round;
            stroke-dasharray: 1400;
            stroke-dashoffset: 1400;
            animation: cw-draw 3s cubic-bezier(0.3, 0, 0.2, 1) infinite;
        }
        @keyframes cw-draw {
            0%   { stroke-dashoffset: 1400; }
            80%  { stroke-dashoffset: 0; }
            100% { stroke-dashoffset: 0; }
        }
        #globalLoadingOverlay .global-loading-text {
            margin: 0;
            font-size: 1rem;
            font-weight: 600;
            color: #333;
        }
    `;
    document.head.appendChild(style);

    const overlay = document.createElement('div');
    overlay.id = 'globalLoadingOverlay';
    overlay.innerHTML = `
        <div class="loading-card" role="status" aria-live="polite">
            <div class="wrap">
                <svg class="line-svg" viewBox="0 0 680 150" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
                    <path class="line-path" d="
                        M10,75
                        C25,75 35,55 52,48
                        C69,41 76,58 72,70
                        C68,82 56,86 62,76
                        C68,66 83,62 108,62

                        C140,62 162,88 184,98
                        C206,108 228,100 244,83
                        C260,66 254,44 237,39
                        C220,34 208,50 214,64
                        C220,78 238,82 266,76

                        C298,68 320,18 348,6
                        C376,-6 393,28 398,56
                        C403,84 390,116 372,121
                        C354,126 338,104 350,84
                        C362,64 393,55 432,58

                        C460,60 476,74 494,70
                        C512,66 515,52 508,45
                        C501,38 491,43 496,55
                        C501,67 520,70 546,67

                        C574,63 596,42 616,36
                        C636,30 646,52 649,68
                        C652,84 644,103 634,107
                        C624,111 614,99 621,87
                        C628,75 648,70 670,72
                    " />
                </svg>
            </div>
            <p class="global-loading-text">Loading...</p>
        </div>
    `;

    overlay.addEventListener('click', (event) => {
        if (event.target === overlay) {
            event.stopPropagation();
            event.preventDefault();
        }
    });

    document.body.appendChild(overlay);
}

function showGlobalLoading(message = 'Loading...') {
    initGlobalLoadingOverlay();
    const overlay = document.getElementById('globalLoadingOverlay');
    if (!overlay) return;
    const text = overlay.querySelector('.global-loading-text');
    if (text) text.textContent = message;
    overlay.classList.add('active');
}

function hideGlobalLoading() {
    const overlay = document.getElementById('globalLoadingOverlay');
    if (!overlay) return;
    overlay.classList.remove('active');
}

function isGuestAssessmentBlocked() {
    return localStorage.getItem('guestAssessmentTaken') === 'true';
}

function markGuestAssessmentTaken() {
    localStorage.setItem('guestAssessmentTaken', 'true');
}
