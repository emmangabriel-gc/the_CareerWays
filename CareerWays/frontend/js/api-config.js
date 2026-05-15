/**
 * API base URL for the Flask backend.
 * On Vercel we use same-origin "/api" so the browser never hits cross-origin CORS;
 * vercel.json rewrites /api/* to the Render backend.
 * Override: <script>window.__CW_API_BASE__ = 'https://…/api';</script> before this file.
 */
(function () {
    if (typeof window === 'undefined') return;
    if (window.__CW_API_BASE__) return;
    var h = typeof location !== 'undefined' ? location.hostname : '';
    var isLocal =
        !h ||
        h === 'localhost' ||
        h === '127.0.0.1' ||
        /^192\.168\./.test(h) ||
        /^10\./.test(h);
    // Vercel (and any HTTPS deploy with /api rewrite) → same-origin proxy, no CORS
    var useRelativeApi =
        typeof location !== 'undefined' &&
        location.protocol === 'https:' &&
        !isLocal;
    window.__CW_API_BASE__ = useRelativeApi
        ? '/api'
        : 'https://careerways-production.up.railway.app/api';
})();
