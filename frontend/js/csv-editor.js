/**
 * CSV Editor Module
 * Handles CSV upload, editing, and validation using Tabulator
 */

const csvEditor = {
    table: null,
    currentData: [],

    // Initialize CSV editor
    init() {
        console.log('Initializing CSV Editor...');
        this.setupUploadArea();
    },

    // Setup drag & drop upload area
    setupUploadArea() {
        const uploadArea = document.getElementById('csv-upload-area');
        const fileInput = document.getElementById('csv-file-input');

        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // File selected
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFile(e.target.files[0]);
            }
        });

        // Drag & drop events
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            if (e.dataTransfer.files.length > 0) {
                this.handleFile(e.dataTransfer.files[0]);
            }
        });
    },

    // Handle file upload
    async handleFile(file) {
        if (!file.name.endsWith('.csv')) {
            app.showToast('Please upload a CSV file', 'error');
            return;
        }

        try {
            app.showToast('Uploading CSV...', 'info');

            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${app.apiUrl}/csv/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const data = await response.json();

            app.showToast(`Loaded ${data.rows} rows from ${file.name}`, 'success');

            // Update UI
            document.getElementById('csv-upload-area').style.display = 'none';
            document.getElementById('csv-table').style.display = 'block';

            // Initialize table
            this.currentData = data.data;
            this.initTable(data.columns, data.data);

            // Update stats
            await app.updateStats();

            // Enable generate button
            document.getElementById('generate-btn').disabled = false;

        } catch (error) {
            console.error('Error uploading CSV:', error);
            app.showToast(`Error: ${error.message}`, 'error');
        }
    },

    // Initialize Tabulator table
    initTable(columns, data) {
        // Convert columns to Tabulator format
        const tableColumns = columns.map(col => ({
            title: col,
            field: col,
            editor: 'input',
            headerFilter: true,
            headerFilterPlaceholder: `Filter ${col}...`
        }));

        // Initialize Tabulator
        this.table = new Tabulator('#csv-grid', {
            data: data,
            columns: tableColumns,
            layout: 'fitDataFill',
            height: '500px',
            pagination: 'local',
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            movableColumns: true,
            resizableColumns: true,
            cellEdited: (cell) => {
                this.onCellEdit(cell);
            }
        });

        console.log('Table initialized with', data.length, 'rows');
    },

    // Handle cell edit
    async onCellEdit(cell) {
        console.log('Cell edited:', cell.getField(), '=', cell.getValue());

        // Update current data
        this.currentData = this.table.getData();

        // Send update to backend
        try {
            await fetch(`${app.apiUrl}/csv/update`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(this.currentData)
            });
        } catch (error) {
            console.error('Error updating CSV:', error);
        }
    },

    // Add new row
    addRow() {
        if (!this.table) {
            app.showToast('Please upload a CSV file first', 'warning');
            return;
        }

        // Get columns from first row
        const columns = this.table.getColumns().map(col => col.getField());
        const newRow = {};
        columns.forEach(col => newRow[col] = '');

        // Add row to table
        this.table.addRow(newRow);

        app.showToast('Row added', 'success');
    },

    // Validate CSV
    async validateCSV() {
        if (!this.table) {
            app.showToast('Please upload a CSV file first', 'warning');
            return;
        }

        try {
            app.showToast('Validating CSV...', 'info');

            const response = await fetch(`${app.apiUrl}/csv/validate`, {
                method: 'POST'
            });

            const data = await response.json();

            // Display validation results
            const messagesDiv = document.getElementById('validation-messages');
            messagesDiv.innerHTML = '';

            if (data.valid) {
                messagesDiv.innerHTML = `
                    <div class="validation-success">
                        <i class="bi bi-check-circle-fill"></i>
                        <strong>Validation Passed!</strong> No errors found.
                    </div>
                `;
                app.showToast('Validation passed', 'success');
            } else {
                // Show errors
                data.errors.forEach(error => {
                    const div = document.createElement('div');
                    div.className = 'validation-error';
                    div.innerHTML = `
                        <i class="bi bi-exclamation-triangle-fill"></i>
                        ${error}
                    `;
                    messagesDiv.appendChild(div);
                });

                app.showToast(`Found ${data.errors.length} validation errors`, 'error');
            }

            // Show warnings
            if (data.warnings.length > 0) {
                data.warnings.forEach(warning => {
                    const div = document.createElement('div');
                    div.className = 'validation-warning';
                    div.innerHTML = `
                        <i class="bi bi-exclamation-circle-fill"></i>
                        ${warning}
                    `;
                    messagesDiv.appendChild(div);
                });
            }

        } catch (error) {
            console.error('Error validating CSV:', error);
            app.showToast(`Validation error: ${error.message}`, 'error');
        }
    },

    // Upload CSV button
    uploadCSV() {
        document.getElementById('csv-file-input').click();
    }
};
