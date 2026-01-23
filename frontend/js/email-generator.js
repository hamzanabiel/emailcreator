/**
 * Email Generator Module
 * Handles email generation process
 */

const emailGenerator = {
    // Initialize email generator
    init() {
        console.log('Initializing Email Generator...');
        this.updateSummary();
    },

    // Update generation summary
    async updateSummary() {
        const summaryDiv = document.getElementById('generate-summary');
        const generateBtn = document.getElementById('generate-btn');

        try {
            const response = await fetch(`${app.apiUrl}/csv/data`);
            const data = await response.json();

            if (data.rows === 0) {
                summaryDiv.innerHTML = `
                    <h6><i class="bi bi-info-circle"></i> Ready to Generate</h6>
                    <p class="mb-0">Upload a CSV file to get started.</p>
                `;
                generateBtn.disabled = true;
            } else {
                summaryDiv.innerHTML = `
                    <h6><i class="bi bi-info-circle"></i> Ready to Generate</h6>
                    <p class="mb-0">
                        <strong>${data.rows}</strong> rows loaded.
                        Emails will be generated based on your CSV data and configuration.
                    </p>
                    <ul class="mt-2 mb-0">
                        <li>Single invoices will create individual emails</li>
                        <li>Grouped invoices (same Group value) will be combined</li>
                        <li>Attachments will be included if specified</li>
                        <li>Files will be saved to the output directory</li>
                    </ul>
                `;
                generateBtn.disabled = false;
            }

        } catch (error) {
            console.error('Error updating summary:', error);
        }
    },

    // Generate emails
    async generate() {
        const generateBtn = document.getElementById('generate-btn');
        const progressDiv = document.getElementById('generate-progress');
        const resultsDiv = document.getElementById('generate-results');
        const summaryDiv = document.getElementById('generate-summary');

        try {
            // Disable button
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Generating...';

            // Show progress
            summaryDiv.style.display = 'none';
            progressDiv.style.display = 'block';
            resultsDiv.style.display = 'none';

            this.updateProgress(0, 'Starting generation...');

            // Call API
            const response = await fetch(`${app.apiUrl}/generate`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const data = await response.json();

            // Simulate progress (instant API call)
            this.updateProgress(50, 'Processing...');
            await this.sleep(500);
            this.updateProgress(100, 'Complete!');
            await this.sleep(500);

            // Hide progress, show results
            progressDiv.style.display = 'none';

            if (data.success) {
                resultsDiv.style.display = 'block';
                document.getElementById('results-text').innerHTML = `
                    Successfully generated <strong>${data.count}</strong> email file(s).
                    <br><br>
                    <strong>Files created:</strong>
                    <ul class="mt-2">
                        ${data.files.map(f => `<li>${f}</li>`).join('')}
                    </ul>
                `;

                app.showToast(`${data.count} emails generated successfully`, 'success');

                // Update stats
                await app.updateStats();

            } else {
                throw new Error(data.errors.join(', '));
            }

        } catch (error) {
            console.error('Error generating emails:', error);

            progressDiv.style.display = 'none';
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h6><i class="bi bi-exclamation-triangle-fill"></i> Generation Failed</h6>
                    <p>${error.message}</p>
                </div>
            `;

            app.showToast(`Generation failed: ${error.message}`, 'error');

        } finally {
            // Reset button
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="bi bi-play-circle-fill"></i> Generate Emails';
        }
    },

    // Update progress bar
    updateProgress(percent, text) {
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');

        progressBar.style.width = `${percent}%`;
        progressBar.textContent = `${percent}%`;
        progressText.textContent = text;
    },

    // Download all emails as zip
    async downloadAll() {
        try {
            const response = await fetch(`${app.apiUrl}/emails/download-all/zip`);

            if (!response.ok) {
                throw new Error('Failed to download emails');
            }

            const blob = await response.blob();
            app.downloadFile(blob, 'emails.zip');

            app.showToast('Downloaded all emails as zip', 'success');

        } catch (error) {
            console.error('Error downloading emails:', error);
            app.showToast(`Error: ${error.message}`, 'error');
        }
    },

    // Helper: sleep
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};
