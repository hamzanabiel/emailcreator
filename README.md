# CSV Email Tool - README

## PROJECT OVERVIEW

This tool reads entity data from a CSV file, groups entities by specified criteria, 
and generates Microsoft Outlook .msg files (draft emails) for each group. The tool 
uses customizable email templates and handles multiple entities per email efficiently.

## END PRODUCT DESCRIPTION

### What the tool does:
1. Reads CSV file containing entity information and email details
2. Groups entities by specified grouping column (e.g., group_id, department, etc.)
3. Generates one .msg file per group containing all entities in that group
4. Uses customizable email templates with placeholders for dynamic content
5. Handles variable numbers of entities per group (1 entity vs 10+ entities)
6. Creates properly formatted .msg files that open directly in Outlook

### What you get:
- Folder of .msg files ready to open in Outlook
- Each .msg file is a draft email with:
  * Proper To/CC/BCC recipients
  * Custom subject line (enhanced with invoice numbers)
  * Formatted email body with all group entities
  * All relevant invoice files attached
  * Your company banner/template preserved
- Summary report of emails generated
- Attachment processing report
- Error log for any issues encountered

## REQUIRED CSV FORMAT

### Mandatory Columns:
- entity_name: Name of the entity/company
- group_id: Identifier for grouping (entities with same group_id go in one email)
- to_email: Primary recipient email address
- subject: Email subject line
- invoice_number: Invoice number/identifier for this entity
- invoice_file_path: Full path to the invoice file (PDF, DOC, etc.)

### Optional Columns:
- cc_email: Carbon copy recipients (separate multiple with semicolons)
- bcc_email: Blind carbon copy recipients (separate multiple with semicolons)
- entity_type: Type of entity (Corporation, Partnership, Trust, etc.)
- jurisdiction: Entity jurisdiction/location
- custom_field_1: Any additional data field
- custom_field_2: Any additional data field
- notes: Special notes or instructions

### Example CSV Structure:
```
entity_name,group_id,to_email,cc_email,bcc_email,subject,entity_type,jurisdiction,invoice_number,invoice_file_path
"Acme Corp","CLIENT_001","john@acme.com","legal@acme.com","","FATCA Compliance Update","Corporation","Delaware","INV-2024-001","invoices/acme_corp_inv_001.pdf"
"Beta LLC","CLIENT_001","john@acme.com","legal@acme.com","","FATCA Compliance Update","LLC","Nevada","INV-2024-002","invoices/beta_llc_inv_002.pdf"
"Gamma Inc","CLIENT_002","admin@gamma.com","","compliance@ourcompany.com","CRS Filing Notification","Corporation","Ontario","INV-2024-003","invoices/gamma_inc_inv_003.pdf"
```

## EMAIL TEMPLATE SYSTEM

### Template Structure:
The tool uses HTML email templates with placeholders that get replaced with actual data.

### Available Placeholders:
- {{entity_count}}: Number of entities in this group
- {{entity_list}}: Formatted list of all entities in group
- {{group_id}}: The group identifier
- {{subject}}: Subject line from CSV (enhanced with invoice numbers)
- {{current_date}}: Today's date
- {{entity_table}}: HTML table of all entities with details
- {{single_entity_name}}: For single-entity emails only
- {{custom_greeting}}: Personalized greeting based on entity count
- {{invoice_list}}: Comma-separated list of all invoice numbers
- {{invoice_count}}: Total number of invoices attached
- {{attachment_summary}}: Summary of attached files

### Template Examples:

#### Single Entity Template Block:
```html
<p>Dear {{contact_name}},</p>
<p>This email concerns {{single_entity_name}} and the required compliance documentation.</p>
<p>Please find invoice {{invoice_list}} attached for your review.</p>
```

#### Multiple Entities Template Block:
```html
<p>Dear Team,</p>
<p>This email concerns the following {{entity_count}} entities under your management:</p>
{{entity_table}}
<p>Please review the compliance requirements for all entities listed above.</p>
<p>{{invoice_count}} invoices are attached: {{invoice_list}}</p>
```

## TECHNICAL SPECIFICATIONS

### Dependencies:
- Python 3.8+
- pandas (CSV processing)
- jinja2 (templating engine)
- python-msg (create .msg files)
- openpyxl (Excel file support, optional)
- pathlib (file path handling)
- mimetypes (attachment type detection)

### File Structure:
```
csv_email_tool/
├── main.py                 # Main script
├── templates/
│   ├── email_template.html # Main email template
│   └── entity_table.html   # Entity table template
├── output/                 # Generated .msg files go here
├── logs/                   # Error and processing logs
├── config.json            # Configuration settings
└── requirements.txt       # Python dependencies
```

### Configuration Options (config.json):
```json
{
  "csv_file_path": "data/entities.csv",
  "output_directory": "output",
  "template_file": "templates/email_template.html",
  "grouping_column": "group_id",
  "date_format": "%B %d, %Y",
  "max_entities_inline": 3,
  "company_name": "Your Company Name",
  "sender_name": "Your Name",
  "sender_title": "Your Title",
  "attachment_base_path": "invoices/",
  "include_invoice_in_subject": true,
  "max_attachment_size_mb": 25,
  "allowed_attachment_types": [".pdf", ".docx", ".xlsx", ".png", ".jpg"]
}
```

## USAGE INSTRUCTIONS

### Setup:
1. Install Python 3.8+ on your system
2. Download/clone the tool files
3. Install dependencies: `pip install -r requirements.txt`
4. Place your CSV file in the project directory
5. Customize email template in templates/email_template.html
6. Update config.json with your settings

### Running the Tool:
1. Open command prompt/terminal in project directory
2. Run: `python main.py --csv your_file.csv`
3. Optional flags:
   - `--output-dir custom_output_folder`
   - `--template custom_template.html`
   - `--group-by custom_grouping_column`
   - `--dry-run` (preview without generating files)
   - `--skip-attachments` (generate emails without attachments)
   - `--attachment-base-path /path/to/invoices/`

### Output:
- .msg files created in output directory with attachments embedded
- Files named: "GROUP_ID_YYYYMMDD_HHMMSS.msg"
- Summary report: "email_generation_summary.txt"
- Attachment report: "attachment_summary.txt"
- Error log: "logs/errors.log"

## ATTACHMENT HANDLING

### Supported File Types:
- PDF documents (.pdf)
- Microsoft Word documents (.docx, .doc)
- Excel spreadsheets (.xlsx, .xls)
- Image files (.png, .jpg, .jpeg, .gif)
- Text files (.txt)
- Other document formats (configurable)

### Attachment Processing:
- **File Validation**: Checks file existence, size, and type before processing
- **Size Limits**: Configurable maximum attachment size (default: 25MB per file)
- **Batch Embedding**: All files for a group are embedded into single .msg file
- **Error Handling**: Missing files are logged, email generation continues
- **Path Resolution**: Supports relative and absolute file paths
- **Duplicate Detection**: Prevents duplicate attachments in same email

### Subject Line Enhancement:
- **Single Invoice**: "Original Subject - Invoice INV-001"
- **Multiple Invoices**: "Original Subject - Invoices INV-001, INV-002, INV-003"
- **Configurable Format**: Customizable subject line templates
- **Group Consolidation**: All invoice numbers for a group included

### File Organization:
```
project/
├── invoices/
│   ├── client_001_invoice_001.pdf
│   ├── client_001_invoice_002.pdf
│   └── client_002_invoice_003.pdf
├── templates/
└── output/
    ├── CLIENT_001_20240123_143022.msg  # Contains invoices 001 & 002
    └── CLIENT_002_20240123_143023.msg  # Contains invoice 003
```



### Your Current Template Integration:
1. Save your current email template as HTML
2. Replace dynamic content areas with placeholders
3. Preserve your company banner, footer, styling
4. Add conditional blocks for single vs multiple entities

### Template Customization Example:
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Your existing CSS styles */
    </style>
</head>
<body>
    <!-- Your company banner -->
    <div class="banner">
        <img src="your-logo.png" alt="Company Logo">
    </div>
    
    <!-- Dynamic content area -->
    <div class="content">
        {% if entity_count == 1 %}
            <!-- Single entity template -->
            <p>Dear {{contact_name}},</p>
            <p>This communication relates to {{single_entity_name}}...</p>
        {% else %}
            <!-- Multiple entities template -->
            <p>Dear Team,</p>
            <p>This communication relates to the following {{entity_count}} entities:</p>
            {{entity_table}}
        {% endif %}
        
        <!-- Common content -->
        <p>Your common compliance message here...</p>
    </div>
    
    <!-- Your company footer -->
    <div class="footer">
        <!-- Your existing footer content -->
    </div>
</body>
</html>
```

## FEATURES & CAPABILITIES

### Core Features:
- ✓ CSV parsing with validation
- ✓ Entity grouping by any column
- ✓ Template-based email generation
- ✓ .msg file creation for Outlook
- ✓ Multiple recipients (To/CC/BCC)
- ✓ File attachment handling (PDFs, documents, images)
- ✓ Automatic subject line enhancement with invoice numbers
- ✓ Error handling and logging
- ✓ Preview mode (dry-run)
- ✓ Batch processing

### Smart Features:
- ✓ Automatic entity count detection
- ✓ Dynamic template switching (single vs multiple entities)
- ✓ HTML table generation for entity lists
- ✓ Date formatting and insertion
- ✓ File naming with timestamps
- ✓ Duplicate detection and handling
- ✓ Unicode/special character support
- ✓ Attachment validation and size checking
- ✓ Invoice number aggregation in subject lines
- ✓ Missing file detection and reporting

### Quality of Life Features:
- ✓ Progress indicators during processing
- ✓ Detailed error messages
- ✓ Summary statistics
- ✓ Configuration file for easy customization
- ✓ Command-line interface with helpful flags
- ✓ Automatic backup of original CSV

## ERROR HANDLING

### Common Issues Addressed:
- Invalid email addresses (validation)
- Missing required CSV columns
- Empty groups (skipped with warning)
- Template rendering errors
- File permission issues
- Large entity lists (pagination/truncation)
- Special characters in entity names
- Duplicate group IDs with different recipients
- Missing attachment files (with detailed reporting)
- Oversized attachments (automatic handling/warning)
- Unsupported file types (validation and filtering)
- Corrupted attachment files (detection and skipping)

### Validation Rules:
- At least one valid email address per group
- Required CSV columns present
- Template file exists and is readable
- Output directory is writable
- Entity names are not empty
- Group IDs are consistent within groups
- All attachment files exist and are accessible
- Attachment file sizes within limits
- Attachment file types are supported
- Invoice numbers are unique within groups

## PERFORMANCE CONSIDERATIONS

### Optimization Features:
- Processes groups in batches
- Memory-efficient CSV reading
- Template caching
- Parallel .msg file generation (optional)
- Large file handling with chunking

### Scalability:
- Tested with 1000+ entities
- Supports 50+ entities per email
- Handles CSV files up to 100MB
- Configurable memory limits

## SECURITY & COMPLIANCE

### Data Protection:
- No data transmitted over network
- Local file processing only
- Temporary files cleaned up automatically
- Optional data encryption for sensitive CSVs
- Audit trail of all operations

### Email Privacy:
- BCC handling for confidential recipients
- No email addresses exposed between groups
- Proper email header formatting
- Attachment scanning capability (future feature)

## FUTURE ENHANCEMENTS

### Planned Features:
- Excel file support (.xlsx input)
- Email scheduling integration
- Mail merge with Word documents
- Advanced filtering options
- GUI interface (optional)
- Integration with email APIs (SendGrid, etc.)
- Template library with common compliance scenarios
- Bulk attachment processing optimizations

### Customization Options:
- Plugin system for custom data processors
- Advanced conditional logic in templates
- Multi-language support
- Custom validation rules
- Integration with CRM systems

## SUPPORT & MAINTENANCE

### Documentation Included:
- Complete API documentation
- Template development guide
- Troubleshooting manual
- Configuration examples
- Best practices guide

### Testing:
- Unit tests for all core functions
- Integration tests with sample data
- Template validation tests
- Performance benchmarks
- Compatibility tests (Windows/Mac/Linux)

## DEVELOPMENT TIMELINE

### Phase 1 (Day 1): Core Functionality
- CSV parsing and validation
- Basic grouping logic
- Simple template system
- .msg file generation
- Basic attachment handling

### Phase 2 (Day 2): Advanced Features
- Complex template engine with invoice placeholders
- Advanced attachment validation and embedding
- Subject line enhancement with invoice numbers
- Error handling and logging
- Configuration system
- Command-line interface

### Phase 3 (Day 3): Polish & Testing
- Comprehensive testing with various file types
- Attachment size and validation testing
- Documentation
- Performance optimization
- User experience improvements

## COST ESTIMATE

### Development Effort: 24-28 hours
- Core development: 15-18 hours
- Attachment handling: 4-6 hours
- Testing and debugging: 3-4 hours
- Documentation: 2-3 hours
- Polish and optimization: 2-3 hours

### Maintenance: 2-4 hours/month
- Bug fixes and minor enhancements
- Template updates
- Dependency updates

This tool will significantly streamline your email generation process while maintaining 
the professional appearance of your current templates and ensuring compliance with 
your organizational requirements.
