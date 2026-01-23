# CSV Email Tool - Usage Guide

## Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the tool by editing `config/config.yaml`

3. Prepare your CSV file with the required columns

4. Run the tool:
```bash
python -m src.main your_data.csv
```

## Configuration

Edit `config/config.yaml` to customize:

- **Company Information**: Company name, sender details
- **Email Template**: Subject line format, email format (MSG/EML)
- **File Paths**: Attachment base directory, output directory
- **Template**: Path to HTML template (`config/template.html`)
- **Banner**: Company logo/banner image (optional)

### Customizing the Email Template

The HTML email template is located at `config/template.html`. You can customize:

- **Banner**: Replace the company name or add a logo image
- **Styling**: Modify colors, fonts, and layout in the `<style>` section
- **Content**: Edit the email body text and structure
- **Placeholders**: Template uses Jinja2 syntax with these variables:
  - `{{ company_name }}`
  - `{{ entity_name }}`
  - `{{ invoice_number }}`
  - `{{ amount }}`
  - `{{ due_date }}`
  - `{{ custom_message }}`
  - `{{ group_name }}`
  - `{{ invoices }}` (for group emails)

## CSV Format

Your CSV file must include these columns (exact names can be configured in config.yaml):

### Required Columns:
- **To**: Recipient email address(es) - can use semicolon or comma to separate multiple
- **Entity Name**: Name of the entity/company
- **Invoice Number**: Invoice number

### Optional Columns:
- **CC**: Carbon copy email address(es)
- **BCC**: Blind carbon copy email address(es)
- **Subject**: Custom subject line (overrides auto-generated)
- **Amount**: Invoice amount
- **Due Date**: Payment due date
- **Attachment Path**: Path to attachment file(s) - relative to `attachment_base` in config
- **Group**: Group name for grouping multiple invoices into one email
- **Custom Message**: Custom message to include in the email

### Example CSV:

```csv
To,CC,BCC,Subject,Entity Name,Invoice Number,Amount,Due Date,Attachment Path,Group,Custom Message
john@example.com,manager@example.com,,ACME Invoice 001,ACME Corp,001,2500.00,2026-02-15,invoice_001.pdf,,Thank you for your business
jane@example.com,,,Tech Solutions Invoice 002,Tech Solutions,002,1750.50,2026-02-20,invoice_002.pdf,,
billing@bigcorp.com,,,BigCorp Invoice 003,BigCorp Industries,003,5000.00,2026-02-10,invoice_003.pdf,BigCorp,
billing@bigcorp.com,,,BigCorp Invoice 004,BigCorp Manufacturing,004,3200.00,2026-02-10,invoice_004.pdf,BigCorp,
```

## Email Grouping

To group multiple invoices into a single email:

1. Add a **Group** column to your CSV
2. Use the same group name for all rows that should be grouped together
3. The tool will:
   - Create one email with all grouped invoices
   - Use the To/CC/BCC from the first row in the group
   - Generate subject: `{Group Name} Invoices {Invoice1} / {Invoice2} / {Invoice3}`
   - Include all attachments from all rows

## Command-Line Options

```bash
python -m src.main [OPTIONS] CSV_FILE

Options:
  -c, --config FILE        Path to config file (default: config/config.yaml)
  --skip-validation        Skip email and attachment validation
  -v, --verbose            Enable verbose/debug output
  -h, --help               Show help message
```

### Examples:

```bash
# Basic usage
python -m src.main data.csv

# Use custom config
python -m src.main data.csv --config my_config.yaml

# Skip validation (for testing)
python -m src.main data.csv --skip-validation

# Verbose output
python -m src.main data.csv --verbose
```

## Output

Generated email files are saved to the `output/` directory (configurable in `config.yaml`).

- **On Windows**: Creates `.msg` files (Outlook format)
- **On Linux/Mac**: Creates `.eml` files (universal email format)
- You can force a specific format by setting `email.format` in config.yaml

### Filename Pattern:

Default: `{entity}_{invoice}_{timestamp}.msg` or `.eml`

Configurable in `config.yaml` under `output.filename_pattern`

## Attachments

Attachment paths in the CSV can be:

1. **Relative paths**: Relative to `attachment_base` directory (set in config.yaml)
   - Example: `invoice_001.pdf` → resolves to `tests/attachments/invoice_001.pdf`

2. **Absolute paths**: Full file system paths
   - Example: `/home/user/invoices/invoice_001.pdf`

3. **Multiple attachments**: Separate with comma or semicolon
   - Example: `invoice_001.pdf,receipt_001.pdf`

## Validation

The tool validates:

- **Email addresses**: Checks format for To, CC, BCC fields
- **Attachments**: Verifies files exist at specified paths

To skip validation (useful for testing), use `--skip-validation` flag.

## Platform Support

- **Windows**: Creates native `.msg` files using Outlook COM automation
- **Linux**: Creates `.eml` files (works with all email clients)
- **Mac**: Creates `.eml` files (works with all email clients)

The tool automatically detects your platform. You can override this in `config.yaml`:

```yaml
email:
  format: "auto"  # Options: 'auto', 'msg', 'eml'
```

## Troubleshooting

### Issue: "Attachment file not found"
- Check that the `attachment_base` path in config.yaml is correct
- Verify attachment file paths in your CSV
- Use absolute paths or correct relative paths

### Issue: "Invalid email address"
- Ensure email addresses follow format: `name@domain.com`
- Check for typos in email addresses

### Issue: "Missing required columns"
- Verify CSV has required columns: To, Entity Name, Invoice Number
- Check column names match configuration in config.yaml

### Issue: ".msg files not created on Windows"
- Install pywin32: `pip install pywin32`
- Ensure Microsoft Outlook is installed
- Run as administrator if needed

## Testing

Test data is included:

```bash
python -m src.main tests/sample_data.csv --skip-validation
```

This generates sample emails using mock data.

## Support

For issues or questions, please refer to the README.md file.
