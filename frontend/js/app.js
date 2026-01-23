/**
 * Main Application Controller
 * Handles initialization and global utilities
 */

const app = {
    // API base URL
    apiUrl: '/api',

    // Initialize application
    async init() {
        console.log('Initializing CSV Email Tool...');

        // Initialize all modules
        csvEditor.init();
        configEditor.init();
        templateEditor.init();
        emailGenerator.init();
        emailViewer.init();

        // Load initial stats
        await this.updateStats();

        // Setup event listeners
        this.setupEventListeners();

        console.log('Application initialized successfully');
        this.showToast('Application Ready', 'success');
    },

    // Setup global event listeners
    setupEventListeners() {
        // Tab change events
        const tabs = document.querySelectorAll('button[data-bs-toggle="tab"]');
        tabs.forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const targetId = e.target.getAttribute('data-bs-target');
                this.onTabChange(targetId);
            });
        });
    },

    // Handle tab changes
    onTabChange(tabId) {
        console.log('Tab changed to:', tabId);

        switch (tabId) {
            case '#emails-panel':
                emailViewer.refresh();
                break;
            case '#generate-panel':
                emailGenerator.updateSummary();
                break;
            case '#template-panel':
                templateEditor.refreshPreview();
                break;
        }
    },

    // Update statistics badge
    async updateStats() {
        try {
            const response = await fetch(`${this.apiUrl}/stats`);
            const data = await response.json();

            const badge = document.getElementById('stats-badge');
            badge.innerHTML = `
                <i class="bi bi-info-circle"></i>
                ${data.total_emails} emails |
                ${data.csv_rows} rows loaded
            `;
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    },

    // Show toast notification
    showToast(message, type = 'info') {
        const toastEl = document.getElementById('toast');
        const toastBody = toastEl.querySelector('.toast-body');
        const toastHeader = toastEl.querySelector('.toast-header');

        // Set icon based on type
        let icon = 'info-circle';
        let headerClass = 'bg-white text-indigo';

        switch (type) {
            case 'success':
                icon = 'check-circle-fill';
                headerClass = 'border-bottom border-success text-success';
                break;
            case 'error':
                icon = 'exclamation-triangle-fill';
                headerClass = 'border-bottom border-danger text-danger';
                break;
            case 'warning':
                icon = 'exclamation-circle-fill';
                headerClass = 'border-bottom border-warning text-warning';
                break;
            case 'info':
                icon = 'info-circle-fill';
                headerClass = 'border-bottom border-primary text-primary';
                break;
        }

        toastEl.className = 'toast show border-0 shadow-lg rounded-4 overflow-hidden';
        toastHeader.className = `toast-header bg-white border-0 py-3 px-4 ${headerClass}`;
        toastHeader.querySelector('i').className = `bi bi-${icon} me-2 fs-5`;
        toastBody.className = 'toast-body bg-white py-3 px-4 fs-6 fw-medium';
        toastBody.textContent = message;

        const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();
    },

    // Show loading state
    showLoading(elementId, show = true) {
        const element = document.getElementById(elementId);
        if (!element) return;

        if (show) {
            const spinner = document.createElement('div');
            spinner.className = 'text-center p-3';
            spinner.innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Loading...</p>
            `;
            element.innerHTML = '';
            element.appendChild(spinner);
        }
    },

    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    },

    // Format date
    formatDate(timestamp) {
        const date = new Date(timestamp * 1000);
        return date.toLocaleString();
    },

    // Download file from blob
    downloadFile(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
};

// Global function to switch tabs
function switchTab(tabId) {
    const tab = document.getElementById(tabId);
    if (tab) {
        const tabTrigger = new bootstrap.Tab(tab);
        tabTrigger.show();
    }
}

// Handle errors globally
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    app.showToast(`Error: ${event.reason.message || 'An error occurred'}`, 'error');
});
