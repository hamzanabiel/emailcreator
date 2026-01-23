# CSV Email Tool - Installation & Usage Guide

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone or download the repository**
```bash
cd /path/to/emailcreator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- pandas (CSV processing)
- pyyaml (configuration)
- jinja2 (HTML templating)
- colorama (colored output)
- pywin32 (Windows only - for .msg files)

3. **Verify installation**
```bash
python run_tests.py
```
Should show: **20/20 tests passed**

---

## Configuration

### 1. Edit Company Information

Open `config/config.yaml` and update:

```yaml
company:
  name: "Your Company Name"          # Change this
  sender_name: "Accounts Receivable" # Change this
  sender_title: "Billing Department" # Change this

email:
  from: "billing@yourcompany.com"    # Change this
```

### 2. Set Attachment Path

Set where your invoice PDFs are located:

```yaml
paths:
  attachment_base: "path/to/your/invoices"  # Change this
  output: "output"                           # Keep or change output folder
```

### 3. Customize Email Template (Optional)

Edit `config/template.html` to:
- Change colors (search for `#0066cc` and replace)
- Add company logo (replace banner section)
- Modify email text
- Adjust styling

---

## CSV File Format

### Required Columns

Your CSV **must** have these columns (exact names):

| Column Name | Description | Required | Example |
|-------------|-------------|----------|---------|
| **To** | Recipient email | ✅ Yes | `john@example.com` |
| **Entity Name** | Company/entity name | ✅ Yes | `ACME Corp` |
| **Invoice Number** | Invoice identifier | ✅ Yes | `0001` |

### Optional Columns

| Column Name | Description | Example |
|-------------|-------------|---------|
| **CC** | Carbon copy recipients | `manager@example.com` |
| **BCC** | Blind carbon copy | `accounting@example.com` |
| **Subject** | Custom subject (overrides auto-generated) | `Urgent: Invoice 0001` |
| **Amount** | Invoice amount | `2500.00` |
| **Due Date** | Payment due date | `2026-02-15` |
| **Attachment Path** | Path to PDF file | `invoice_0001.pdf` |
| **Group** | Group name (for combining invoices) | `ACME Group` |
| **Custom Message** | Special message for this invoice | `Thank you for your business` |

### CSV Example

```csv
To,CC,BCC,Subject,Entity Name,Invoice Number,Amount,Due Date,Attachment Path,Group,Custom Message
john@example.com,manager@example.com,,Invoice 0001,ACME Corp,0001,2500.00,2026-02-15,invoice_0001.pdf,,Thank you for your business
jane@example.com,,,Invoice 0002,Tech Solutions,0002,1750.50,2026-02-20,invoice_0002.pdf,,
billing@bigcorp.com,,,Group Invoice,BigCorp A,0003,5000.00,2026-02-10,invoice_0003.pdf,BigCorp,
billing@bigcorp.com,,,Group Invoice,BigCorp B,0004,3200.00,2026-02-10,invoice_0004.pdf,BigCorp,
```

**Note:** Rows with same **Group** value are combined into one email.

### Multiple Recipients

Separate multiple email addresses with **semicolon (;)** or **comma (,)**:

```csv
To,CC
john@example.com,"manager@example.com;cfo@example.com"
```

---

## Usage

### Basic Usage

```bash
python -m src.main your_data.csv
```

This will:
1. Read your CSV file
2. Validate email addresses and attachments
3. Group invoices (if Group column present)
4. Generate email files in `output/` directory
5. Show summary report

### Command Options

```bash
# Skip validation (faster, for testing)
python -m src.main data.csv --skip-validation

# Use custom config file
python -m src.main data.csv --config custom_config.yaml

# Verbose output (debug mode)
python -m src.main data.csv --verbose

# Show help
python -m src.main --help
```

### Example Commands

```bash
# First test with sample data
python -m src.main tests/sample_data.csv --skip-validation

# Production run with validation
python -m src.main invoices_january.csv

# Large file with verbose output
python -m src.main large_file.csv --verbose
```

---

## Output

### Generated Files

Emails are saved to `output/` directory (configurable):

**File format:**
- **Linux/Mac:** `.eml` files (universal format)
- **Windows:** `.msg` files (Outlook format) or `.eml` (fallback)

**Filename pattern:**
- Single invoice: `EntityName_InvoiceNumber_Timestamp.eml`
- Grouped invoice: `GroupName_Multiple_Timestamp.eml`

Example files:
```
output/
├── ACME Corp_0001_20260123_172049.eml
├── Tech Solutions_0002_20260123_172049.eml
└── BigCorp_Multiple_20260123_172049.eml
```

### Opening Generated Emails

**Method 1: Email Client (Recommended)**
1. Navigate to `output/` folder
2. Double-click any `.eml` or `.msg` file
3. Opens in Outlook, Apple Mail, Thunderbird, etc.

**Method 2: Preview in Terminal**
```bash
python view_email.py "output/ACME Corp_0001_*.eml"
```

**Method 3: Extract HTML for Browser**
```bash
python -c "
import email
from email import policy
with open('output/YourFile.eml', 'rb') as f:
    msg = email.message_from_binary_file(f, policy=policy.default)
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            with open('preview.html', 'w') as out:
                out.write(part.get_content())
"
# Then open preview.html in browser
```

---

## Workflow Example

### Complete Workflow

**Step 1: Prepare your data**
```bash
# Create CSV file: invoices.csv
# Place PDF files in: /path/to/invoices/
```

**Step 2: Update configuration**
```bash
# Edit config/config.yaml
# Set company name, sender info, attachment_base path
```

**Step 3: Test with sample data**
```bash
python run_tests.py
```

**Step 4: Generate emails**
```bash
python -m src.main invoices.csv
```

**Step 5: Review output**
```bash
ls output/
python view_email.py "output/YourFile.eml"
```

**Step 6: Send emails**
- Open each `.eml` file in your email client
- Review content
- Click Send (or save as draft)

---

## Email Grouping

### How Grouping Works

Rows with the **same Group value** are combined into **one email**:

**CSV:**
```csv
To,Entity Name,Invoice Number,Group
billing@acme.com,ACME Widget,0001,ACME
billing@acme.com,ACME Gadget,0002,ACME
billing@acme.com,ACME Tools,0003,ACME
```

**Result:** ONE email to `billing@acme.com` containing all 3 invoices

**Subject:** `ACME Invoices 0001 / 0002 / 0003`

**Email body:** Shows all 3 invoices with details

**Attachments:** All 3 PDF files attached

### Mixing Grouped and Single Emails

```csv
To,Entity Name,Invoice Number,Group
john@example.com,Company A,0001,          ← Single email
jane@example.com,Company B,0002,          ← Single email
billing@acme.com,ACME Widget,0003,ACME    ← Grouped (part 1)
billing@acme.com,ACME Gadget,0004,ACME    ← Grouped (part 2)
```

**Result:** 3 emails total (2 single + 1 grouped)

---

## Attachment Paths

### Relative Paths (Recommended)

Set `attachment_base` in config, use relative paths in CSV:

**config.yaml:**
```yaml
paths:
  attachment_base: "/home/user/invoices"
```

**CSV:**
```csv
Attachment Path
invoice_0001.pdf     ← Resolves to: /home/user/invoices/invoice_0001.pdf
january/inv_002.pdf  ← Resolves to: /home/user/invoices/january/inv_002.pdf
```

### Absolute Paths

Use full paths in CSV:

**CSV:**
```csv
Attachment Path
/full/path/to/invoice_0001.pdf
C:\Invoices\invoice_0002.pdf
```

### Multiple Attachments

Separate with **comma** or **semicolon**:

```csv
Attachment Path
invoice_0001.pdf,receipt_0001.pdf
invoice_0002.pdf;supporting_doc.pdf
```

---

## Subject Line Formats

### Auto-Generated Subjects

**Single Invoice:**
```
Format: {Entity Name} Invoice {Invoice Number}
Example: ACME Corporation Invoice 0001
```

**Grouped Invoices:**
```
Format: {Group Name} Invoices {Num1} / {Num2} / {Num3}
Example: BigCorp Invoices 0003 / 0004 / 0005
```

### Custom Subjects

Provide in **Subject** column:

```csv
Subject,Entity Name,Invoice Number
URGENT: Payment Required,ACME Corp,0001
Reminder: Invoice Due Soon,Tech Solutions,0002
```

Custom subjects **override** auto-generated ones.

### Customizing Subject Templates

Edit `config/config.yaml`:

```yaml
email:
  subject_single: "{entity_name} Invoice {invoice_number}"
  subject_group: "{group_name} Invoices {invoice_numbers}"
```

Change to whatever format you prefer:
```yaml
subject_single: "Invoice #{invoice_number} - {entity_name}"
subject_group: "{group_name} - Multiple Invoices: {invoice_numbers}"
```

---

## Validation

### What Gets Validated

**Email Addresses:**
- To, CC, BCC fields
- Checks for valid format (`name@domain.com`)

**Attachments:**
- Verifies files exist at specified paths
- Reports missing files

### Validation Modes

**With validation (recommended):**
```bash
python -m src.main data.csv
```
Shows errors, asks to continue if issues found.

**Skip validation (testing):**
```bash
python -m src.main data.csv --skip-validation
```
Generates emails without checking.

### Handling Validation Errors

**Example output:**
```
Email validation errors:
  ✗ Row 3: Invalid To email: bad-email
  ✗ Row 5: Invalid CC email: missing@

Attachment validation errors:
  ✗ Row 2: Attachment file not found: invoice_0002.pdf
  ✗ Row 7: Attachment file not found: missing.pdf

Continue anyway? (y/N):
```

Type **y** to continue or **N** to abort and fix errors.

---

## Troubleshooting

### Issue: "Module not found"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "CSV file not found"
**Solution:** Check file path, use absolute path or correct relative path
```bash
python -m src.main /full/path/to/data.csv
```

### Issue: "Missing required columns"
**Solution:** Ensure CSV has: `To`, `Entity Name`, `Invoice Number`

Check column names exactly match (case-sensitive)

### Issue: "Attachment file not found"
**Solution:**
1. Check `attachment_base` in config.yaml
2. Verify PDF files exist
3. Use absolute paths in CSV
4. Or use `--skip-validation` for testing

### Issue: "No emails generated"
**Solution:** Check CSV has data rows (not just headers)

Run with `--verbose` to see detailed errors:
```bash
python -m src.main data.csv --verbose
```

### Issue: ".msg files not created on Windows"
**Solution:**
1. Install pywin32: `pip install pywin32`
2. Ensure Outlook is installed
3. Or force EML format in config:
```yaml
email:
  format: "eml"
```

---

## Advanced Configuration

### Logging

**config.yaml:**
```yaml
logging:
  level: "INFO"        # DEBUG, INFO, WARNING, ERROR
  file: "email_tool.log"
  console: true
```

**View logs:**
```bash
cat email_tool.log
tail -f email_tool.log  # Watch in real-time
```

### Output Settings

**config.yaml:**
```yaml
output:
  timestamp: true                              # Add timestamp to filenames
  filename_pattern: "{entity}_{invoice}_{timestamp}"
  organize_by_date: false                      # Create date subdirectories
```

### CSV Column Mapping

If your CSV has different column names, map them in config:

**config.yaml:**
```yaml
csv_columns:
  to: "Email Address"           # Your column name
  entity_name: "Customer Name"  # Your column name
  invoice_number: "Invoice ID"  # Your column name
```

---

## Quick Reference

### Essential Commands
```bash
# Install
pip install -r requirements.txt

# Test
python run_tests.py

# Generate emails
python -m src.main data.csv

# View email
python view_email.py "output/file.eml"
```

### Key Files
```
config/config.yaml     → Company info, paths, settings
config/template.html   → Email template (HTML)
output/                → Generated email files
email_tool.log         → Log file
```

### CSV Requirements
```
Required: To, Entity Name, Invoice Number
Optional: CC, BCC, Subject, Amount, Due Date,
          Attachment Path, Group, Custom Message
```

### Support Files
```
QUICK_START.md       → Quick reference guide
TESTING_GUIDE.md     → Detailed testing instructions
USAGE.md             → Complete usage guide
PROJECT_STATUS.md    → Project status and roadmap
```

---

## Getting Help

**Show command help:**
```bash
python -m src.main --help
```

**View logs:**
```bash
cat email_tool.log
```

**Run with verbose output:**
```bash
python -m src.main data.csv --verbose
```

**Test with sample data:**
```bash
python -m src.main tests/sample_data.csv --skip-validation
```

---

**Version:** 1.0.0 - Core Features
**Platform:** Windows, Linux, macOS
**Format:** .msg (Windows), .eml (Universal)
