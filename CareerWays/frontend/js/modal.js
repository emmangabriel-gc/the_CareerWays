(function () {
    const template = `
    <div id="cwDialogOverlay" class="cw-dialog-overlay" aria-hidden="true">
        <div class="cw-dialog" role="dialog" aria-modal="true" aria-labelledby="cwDialogTitle" aria-describedby="cwDialogMessage">
            <div class="cw-dialog-header">
                <div>
                    <h3 id="cwDialogTitle" class="cw-dialog-title"></h3>
                    <p id="cwDialogMessage" class="cw-dialog-message"></p>
                </div>
                <button id="cwDialogClose" class="cw-dialog-close" aria-label="Close dialog">×</button>
            </div>
            <div class="cw-dialog-body">
                <div id="cwDialogInputWrapper" class="cw-dialog-input-wrapper">
                    <label for="cwDialogInput" class="cw-dialog-input-label"></label>
                    <input id="cwDialogInput" class="cw-dialog-input" type="text" />
                </div>
            </div>
            <div class="cw-dialog-actions">
                <button id="cwDialogCancel" class="btn btn-secondary">Cancel</button>
                <button id="cwDialogConfirm" class="btn btn-primary">Confirm</button>
            </div>
        </div>
    </div>`;

    function insertDialogTemplate() {
        if (!document.body || document.getElementById('cwDialogOverlay')) return;
        document.body.insertAdjacentHTML('beforeend', template);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', insertDialogTemplate);
    } else {
        insertDialogTemplate();
    }

    let currentResolve = null;
    let currentReject = null;

    function getElement(id) {
        return document.getElementById(id);
    }

    function openDialog(options) {
        return new Promise((resolve, reject) => {
            const overlay = getElement('cwDialogOverlay');
            const titleEl = getElement('cwDialogTitle');
            const messageEl = getElement('cwDialogMessage');
            const closeBtn = getElement('cwDialogClose');
            const cancelBtn = getElement('cwDialogCancel');
            const confirmBtn = getElement('cwDialogConfirm');
            const inputWrapper = getElement('cwDialogInputWrapper');
            const inputEl = getElement('cwDialogInput');

            if (!overlay || !titleEl || !messageEl || !cancelBtn || !confirmBtn || !closeBtn || !inputWrapper || !inputEl) {
                reject(new Error('Dialog elements are missing'));
                return;
            }

            currentResolve = resolve;
            currentReject = reject;

            titleEl.textContent = options.title || 'Confirm action';
            messageEl.textContent = options.message || '';
            confirmBtn.textContent = options.confirmText || 'Confirm';
            cancelBtn.textContent = options.cancelText || 'Cancel';

            confirmBtn.classList.toggle('btn-primary', !options.danger);
            confirmBtn.classList.toggle('btn-danger', !!options.danger);

            if (options.showInput) {
                inputWrapper.style.display = 'block';
                inputEl.type = options.inputType || 'text';
                inputEl.placeholder = options.placeholder || '';
                inputEl.value = options.defaultValue || '';
                inputEl.autocomplete = options.inputType === 'password' ? 'current-password' : 'on';
                const label = getElement('cwDialogInputWrapper').querySelector('.cw-dialog-input-label');
                label.textContent = options.inputLabel || '';
                setTimeout(() => inputEl.focus(), 50);
            } else {
                inputWrapper.style.display = 'none';
            }

            const cleanup = () => {
                overlay.classList.remove('active');
                document.body.style.overflow = '';
                document.removeEventListener('keydown', handleKeydown);
                confirmBtn.removeEventListener('click', handleConfirm);
                cancelBtn.removeEventListener('click', handleCancel);
                closeBtn.removeEventListener('click', handleCancel);
                overlay.removeEventListener('click', handleOverlayClick);
                currentResolve = null;
                currentReject = null;
            };

            const handleResult = (value) => {
                cleanup();
                resolve(value);
            };

            const handleCancel = (event) => {
                event.preventDefault();
                handleResult(options.showInput ? null : false);
            };

            const handleConfirm = (event) => {
                event.preventDefault();
                if (options.showInput) {
                    handleResult(inputEl.value.trim());
                } else {
                    handleResult(true);
                }
            };

            const handleOverlayClick = (event) => {
                if (event.target === overlay && options.dismissible !== false) {
                    handleCancel(event);
                }
            };

            const handleKeydown = (event) => {
                if (event.key === 'Escape') {
                    handleCancel(event);
                }
                if (event.key === 'Enter' && document.activeElement === inputEl) {
                    handleConfirm(event);
                }
            };

            confirmBtn.addEventListener('click', handleConfirm);
            cancelBtn.addEventListener('click', handleCancel);
            closeBtn.addEventListener('click', handleCancel);
            overlay.addEventListener('click', handleOverlayClick);
            document.addEventListener('keydown', handleKeydown);

            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }

    window.showConfirm = function (message, options = {}) {
        return openDialog(Object.assign({
            title: options.title || 'Confirm action',
            message,
            confirmText: options.confirmText || 'Yes',
            cancelText: options.cancelText || 'Cancel',
            danger: options.danger || false,
            showInput: false,
            dismissible: options.dismissible !== false
        }, options));
    };

    window.showPrompt = function (message, options = {}) {
        return openDialog(Object.assign({
            title: options.title || 'Confirm action',
            message,
            confirmText: options.confirmText || 'Submit',
            cancelText: options.cancelText || 'Cancel',
            danger: options.danger || true,
            showInput: true,
            inputType: options.inputType || 'text',
            inputLabel: options.inputLabel || '',
            placeholder: options.placeholder || '',
            defaultValue: options.defaultValue || '',
            dismissible: options.dismissible !== false
        }, options));
    };

    window.showAlert = function (message, options = {}) {
        return openDialog(Object.assign({
            title: options.title || 'Notice',
            message,
            confirmText: options.confirmText || 'OK',
            cancelText: options.cancelText || 'Close',
            danger: false,
            showInput: false,
            dismissible: options.dismissible !== false
        }, options));
    };
})();
