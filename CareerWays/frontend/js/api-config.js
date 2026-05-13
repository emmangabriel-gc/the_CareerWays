/**
 * API base URL for the Flask backend.
 * Override per deployment: add before this file in HTML:
 *   <script>window.__CW_API_BASE__ = 'https://your-service.up.railway.app/api';</script>
 */
(function () {
    if (typeof window === 'undefined') return;
    if (!window.__CW_API_BASE__) {
        window.__CW_API_BASE__ =
            'https://thecareerways-production.up.railway.app/api';
    }
})();
