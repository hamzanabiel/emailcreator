/**
 * Email Viewer Module
 * Handles viewing and downloading generated emails
 */

const emailViewer = {
    currentEmails: [],
    selectedEmail: null,

    // Initialize email viewer
    init() {
        console.log('Initializing Email Viewer...');
    },

    // Refresh email list
    async refresh() {
        const listDiv = document.getElementById('email-list');

        try {
            app.showLoading('email-list');

            const response = await fetch(`${app.apiUrl}/emails`);
            const data = await response.json();

            this.currentEmails = data.emails;

            if (data.count === 0) {
                listDiv.innerHTML = `
                    <div class="text-center text-muted p-3">
                        <i class="bi bi-inbox"></i>
                        <p>No emails generated yet</p>
                        <button class="btn btn-sm btn-primary" onclick="switchTab('generate-tab')">
                            <i class="bi bi-plus-circle"></i> Generate Emails
                        </button>
                    </div>
                `;
                return;
            }

            // Create list items
            listDiv.innerHTML = '';
            data.emails.forEach((email, index) => {
                const item = document.createElement('a');
                item.href = '#';
                item.className = `list-group-item list-group-item-action email-list-item ${index === 0 ? 'active' : ''}`;
                item.innerHTML = `
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${email.filename}</h6>
                        <small>${app.formatFileSize(email.size)}</small>
                    </div>
                    <small class="text-muted">${app.formatDate(email.modified)}</small>
                `;

                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.selectEmail(email.filename);

                    // Update active state
                    document.querySelectorAll('.email-list-item').forEach(el => {
                        el.classList.remove('active');
                    });
                    item.classList.add('active');
                });

                listDiv.appendChild(item);
            });

            // Auto-select first email
            if (data.emails.length > 0) {
                await this.selectEmail(data.emails[0].filename);
            }

            console.log(`Loaded ${data.count} emails`);

        } catch (error) {
            console.error('Error loading emails:', error);
            listDiv.innerHTML = `
                <div class="alert alert-danger m-2">
                    <i class="bi bi-exclamation-triangle-fill"></i>
                    Error loading emails
                </div>
            `;
        }
    },

    // Select and preview email
    async selectEmail(filename) {
        const previewDiv = document.getElementById('email-preview');
        this.selectedEmail = filename;

        try {
            app.showLoading('email-preview');

            const response = await fetch(`${app.apiUrl}/emails/${encodeURIComponent(filename)}`);
            const data = await response.json();

            // Display email preview
            previewDiv.innerHTML = `
                <div class="email-header mb-3 pb-3 border-bottom">
                    <div class="row mb-2">
                        <div class="col-2 fw-bold">From:</div>
                        <div class="col-10">${data.from_addr}</div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-2 fw-bold">To:</div>
                        <div class="col-10">${data.to}</div>
                    </div>
                    ${data.cc ? `
                    <div class="row mb-2">
                        <div class="col-2 fw-bold">CC:</div>
                        <div class="col-10">${data.cc}</div>
                    </div>
                    ` : ''}
                    ${data.bcc ? `
                    <div class="row mb-2">
                        <div class="col-2 fw-bold">BCC:</div>
                        <div class="col-10">${data.bcc}</div>
                    </div>
                    ` : ''}
                    <div class="row mb-2">
                        <div class="col-2 fw-bold">Subject:</div>
                        <div class="col-10">${data.subject}</div>
                    </div>
                    ${data.attachments.length > 0 ? `
                    <div class="row mb-2">
                        <div class="col-2 fw-bold">Attachments:</div>
                        <div class="col-10">
                            ${data.attachments.map(att => `
                                <span class="badge bg-secondary me-1">
                                    <i class="bi bi-paperclip"></i> ${att}
                                </span>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    <div class="row mt-3">
                        <div class="col-12">
                            <button class="btn btn-sm btn-primary" onclick="emailViewer.downloadEmail('${filename}')">
                                <i class="bi bi-download"></i> Download
                            </button>
                            <button class="btn btn-sm btn-secondary" onclick="emailViewer.openInClient('${filename}')">
                                <i class="bi bi-envelope-open"></i> Open in Email Client
                            </button>
                        </div>
                    </div>
                </div>

                <div class="email-body">
                    <h6 class="border-bottom pb-2">Email Body Preview:</h6>
                    ${data.html_preview}
                </div>
            `;

        } catch (error) {
            console.error('Error loading email:', error);
            previewDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle-fill"></i>
                    Error loading email preview
                </div>
            `;
        }
    },

    // Download single email
    async downloadEmail(filename) {
        try {
            const response = await fetch(`${app.apiUrl}/emails/${encodeURIComponent(filename)}/download`);

            if (!response.ok) {
                throw new Error('Download failed');
            }

            const blob = await response.blob();
            app.downloadFile(blob, filename);

            app.showToast(`Downloaded ${filename}`, 'success');

        } catch (error) {
            console.error('Error downloading email:', error);
            app.showToast(`Error: ${error.message}`, 'error');
        }
    },

    // Open email in default email client
    async openInClient(filename) {
        // Download the file (browser will ask to open)
        await this.downloadEmail(filename);
        app.showToast('Email downloaded. Open it to view in your email client.', 'info');
    },

    // Download all emails
    async downloadAll() {
        try {
            const response = await fetch(`${app.apiUrl}/emails/download-all/zip`);

            if (!response.ok) {
                throw new Error('Download failed');
            }

            const blob = await response.blob();
            app.downloadFile(blob, 'all_emails.zip');

            app.showToast('Downloaded all emails as zip', 'success');

        } catch (error) {
            console.error('Error downloading all emails:', error);
            app.showToast(`Error: ${error.message}`, 'error');
        }
    }
};
