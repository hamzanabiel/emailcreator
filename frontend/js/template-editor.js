/**
 * Template Editor Module
 * Handles template editing with CodeMirror and live preview
 */

const templateEditor = {
    editor: null,
    currentTemplate: '',

    // Initialize template editor
    async init() {
        console.log('Initializing Template Editor...');
        await this.loadTemplate();
        this.initCodeMirror();
    },

    // Initialize CodeMirror editor
    initCodeMirror() {
        const textarea = document.getElementById('template-editor');

        this.editor = CodeMirror.fromTextArea(textarea, {
            mode: 'htmlmixed',
            theme: 'monokai',
            lineNumbers: true,
            lineWrapping: true,
            indentUnit: 4,
            tabSize: 4,
            autoCloseTags: true,
            matchBrackets: true,
            extraKeys: {
                'Ctrl-S': () => this.saveTemplate(),
                'Cmd-S': () => this.saveTemplate(),
                'Ctrl-Space': 'autocomplete'
            }
        });

        // Set initial value
        this.editor.setValue(this.currentTemplate);

        // Auto-refresh preview on change (debounced)
        let timeout;
        this.editor.on('change', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => this.refreshPreview(), 1000);
        });

        console.log('CodeMirror initialized');
    },

    // Load template from API
    async loadTemplate() {
        try {
            const response = await fetch(`${app.apiUrl}/template`);
            const data = await response.json();

            this.currentTemplate = data.html;

            if (this.editor) {
                this.editor.setValue(data.html);
            }

            console.log('Template loaded');
            await this.refreshPreview();

        } catch (error) {
            console.error('Error loading template:', error);
            app.showToast('Error loading template', 'error');
        }
    },

    // Save template
    async saveTemplate() {
        try {
            const html = this.editor.getValue();

            const response = await fetch(`${app.apiUrl}/template`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({html: html})
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            this.currentTemplate = html;
            app.showToast('Template saved successfully', 'success');
            await this.refreshPreview();

        } catch (error) {
            console.error('Error saving template:', error);
            app.showToast(`Error saving template: ${error.message}`, 'error');
        }
    },

    // Refresh preview
    async refreshPreview() {
        const previewDiv = document.getElementById('template-preview');

        try {
            const html = this.editor ? this.editor.getValue() : this.currentTemplate;

            const response = await fetch(`${app.apiUrl}/template/preview`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    html: html,
                    sample_data: null // Use default sample data
                })
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const data = await response.json();
            previewDiv.innerHTML = data.html;

        } catch (error) {
            console.error('Error refreshing preview:', error);
            previewDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle-fill"></i>
                    <strong>Preview Error:</strong> ${error.message}
                </div>
            `;
        }
    }
};
