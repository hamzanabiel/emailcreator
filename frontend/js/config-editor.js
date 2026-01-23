/**
 * Configuration Editor Module
 * Handles loading and saving configuration
 */

const configEditor = {
    currentConfig: null,

    // Initialize configuration editor
    async init() {
        console.log('Initializing Config Editor...');
        await this.loadConfig();
    },

    // Load configuration from API
    async loadConfig() {
        try {
            const response = await fetch(`${app.apiUrl}/config`);
            const data = await response.json();

            this.currentConfig = data.config;
            this.populateForm(data.config);

            console.log('Configuration loaded');

        } catch (error) {
            console.error('Error loading config:', error);
            app.showToast('Error loading configuration', 'error');
        }
    },

    // Populate form with config data
    populateForm(config) {
        // Company info
        document.getElementById('config-company-name').value = config.company?.name || '';
        document.getElementById('config-sender-name').value = config.company?.sender_name || '';
        document.getElementById('config-sender-title').value = config.company?.sender_title || '';

        // Email settings
        document.getElementById('config-from-email').value = config.email?.from || '';
        document.getElementById('config-subject-single').value = config.email?.subject_single || '';
        document.getElementById('config-subject-group').value = config.email?.subject_group || '';

        // Paths
        document.getElementById('config-attachment-base').value = config.paths?.attachment_base || '';
        document.getElementById('config-output-dir').value = config.paths?.output || '';
    },

    // Save configuration
    async saveConfig() {
        try {
            // Collect form data
            const config = {
                company: {
                    name: document.getElementById('config-company-name').value,
                    sender_name: document.getElementById('config-sender-name').value,
                    sender_title: document.getElementById('config-sender-title').value
                },
                email: {
                    from: document.getElementById('config-from-email').value,
                    subject_single: document.getElementById('config-subject-single').value,
                    subject_group: document.getElementById('config-subject-group').value,
                    format: this.currentConfig.email?.format || 'auto'
                },
                paths: {
                    attachment_base: document.getElementById('config-attachment-base').value,
                    output: document.getElementById('config-output-dir').value,
                    template: this.currentConfig.paths?.template || 'config/template.html',
                    banner: this.currentConfig.paths?.banner || ''
                },
                csv_columns: this.currentConfig.csv_columns || {},
                grouping: this.currentConfig.grouping || {},
                validation: this.currentConfig.validation || {},
                output: this.currentConfig.output || {},
                logging: this.currentConfig.logging || {}
            };

            const response = await fetch(`${app.apiUrl}/config`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({config: config})
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            this.currentConfig = config;
            app.showToast('Configuration saved successfully', 'success');

        } catch (error) {
            console.error('Error saving config:', error);
            app.showToast(`Error saving configuration: ${error.message}`, 'error');
        }
    }
};
