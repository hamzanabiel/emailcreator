# CSV Email Tool - Testing Guide

## Quick Testing Steps

### 1. Test with Sample Data (Included)

Run the tool with the included sample data:

```bash
python -m src.main tests/sample_data.csv --skip-validation
```

**Expected Output:**
- ✅ 8 email files generated in `output/` directory
- ✅ 6 single invoice emails
- ✅ 2 grouped invoice emails (BigCorp Group with 2 invoices)

### 2. View Generated Emails

Use the email viewer to inspect the generated files:

```bash
# View a single invoice email
python view_email.py "output/ACME Corporation_1.eml"

# View a grouped invoice email
python view_email.py "output/BigCorp Group_Multiple_*.eml"

# View all emails
for file in output/*.eml; do python view_email.py "$file"; done
```

### 3. Open Emails in Email Client

The generated `.eml` files can be opened directly in:
- **Outlook**: Double-click the .eml file
- **Apple Mail**: Double-click the .eml file
- **Gmail**: Drag and drop into Gmail web interface
- **Thunderbird**: File → Open → Saved Message

### 4. Verify Email Content

Check each email for:
- ✅ **Headers**: To, CC, BCC, Subject populated correctly
- ✅ **Body**: Professional formatting, invoice details displayed
- ✅ **Attachments**: PDF files attached correctly
- ✅ **Grouping**: Multiple invoices in grouped emails
- ✅ **Custom Messages**: Displayed when provided

---

## Sample Data Explanation

The included `tests/sample_data.csv` contains 8 test invoices:

| Row | Type | Entity | Invoice | Group | Special Features |
|-----|------|--------|---------|-------|------------------|
| 1 | Single | ACME Corporation | 0001 | - | Custom subject, CC, Custom message |
| 2 | Single | Tech Solutions LLC | 0002 | - | Basic invoice |
| 3 | **Group** | BigCorp Industries | 0003 | BigCorp Group | Part of group, BCC included |
| 4 | **Group** | BigCorp Manufacturing | 0004 | BigCorp Group | Part of group |
| 5 | Single | MidSize Company | 0005 | - | Custom message |
| 6 | Single | StartUp Inc | 0006 | - | Basic invoice |
| 7 | Single | Enterprise Corp | 0007 | - | High amount, CC, Custom message |
| 8 | Single | Small Business Co | 0008 | - | Basic invoice |

**Note:** Rows 3 and 4 have the same "Group" value, so they will be combined into ONE email sent to the first recipient (accounting@bigcorp.com).

---

## Testing Your Own Data

### Step 1: Create Your CSV File

Create a CSV file with these columns (exact names):

```csv
To,CC,BCC,Subject,Entity Name,Invoice Number,Amount,Due Date,Attachment Path,Group,Custom Message
```

**Required columns:**
- `To` - Recipient email address
- `Entity Name` - Company/entity name
- `Invoice Number` - Invoice identifier

**Optional columns:**
- `CC` - Carbon copy recipients (separate multiple with semicolon)
- `BCC` - Blind carbon copy recipients
- `Subject` - Custom subject (leave empty for auto-generated)
- `Amount` - Invoice amount
- `Due Date` - Payment due date
- `Attachment Path` - Path to PDF file (relative to `tests/attachments/` or absolute)
- `Group` - Group name for combining invoices
- `Custom Message` - Special message for this invoice

### Step 2: Prepare Attachments

Place your invoice PDF files in a directory, then update `config/config.yaml`:

```yaml
paths:
  attachment_base: "path/to/your/invoices"
```

Or use absolute paths in your CSV.

### Step 3: Run the Tool

```bash
# With validation (recommended for first run)
python -m src.main your_data.csv

# Skip validation (if you're confident in your data)
python -m src.main your_data.csv --skip-validation

# Verbose output for debugging
python -m src.main your_data.csv --verbose
```

### Step 4: Review Output

Check the `output/` directory for generated emails.

---

## Testing Checklist

Use this checklist to verify the tool is working correctly:

### Basic Functionality
- [ ] Tool runs without errors
- [ ] Correct number of emails generated
- [ ] Output files created in `output/` directory
- [ ] Filenames are descriptive and unique

### Email Content
- [ ] To/CC/BCC addresses correct
- [ ] Subject lines formatted properly
  - Single: `{Entity} Invoice {Number}`
  - Group: `{Group} Invoices {Num1} / {Num2} / {Num3}`
- [ ] Email body displays invoice details
- [ ] Custom messages appear when provided
- [ ] Company name and sender info correct
- [ ] Professional formatting and styling

### Attachments
- [ ] Attachments listed in email body
- [ ] Attachment files actually attached to email
- [ ] Multiple attachments work (if applicable)
- [ ] Attachment filenames correct

### Grouping
- [ ] Invoices with same Group value combined into one email
- [ ] All invoices in group displayed in email body
- [ ] All attachments from group included
- [ ] Grouped emails sent to first recipient in group

### Error Handling
- [ ] Invalid emails detected (if validation enabled)
- [ ] Missing attachments reported (if validation enabled)
- [ ] Helpful error messages displayed
- [ ] Tool recovers gracefully from errors

---

## Common Testing Scenarios

### Test 1: Single Invoice Email

**CSV:**
```csv
To,CC,BCC,Subject,Entity Name,Invoice Number,Amount,Due Date,Attachment Path,Group,Custom Message
test@example.com,,,Test Invoice,Test Company,TEST001,1000.00,2026-03-01,test.pdf,,
```

**Expected:** One email to test@example.com with subject "Test Invoice"

### Test 2: Grouped Invoices

**CSV:**
```csv
To,CC,BCC,Subject,Entity Name,Invoice Number,Amount,Due Date,Attachment Path,Group,Custom Message
billing@acme.com,,,Group 1,ACME Widget,001,500.00,2026-03-01,inv1.pdf,ACME,
billing@acme.com,,,Group 1,ACME Gadget,002,750.00,2026-03-01,inv2.pdf,ACME,
```

**Expected:** One email to billing@acme.com with both invoices, subject "ACME Invoices 001 / 002"

### Test 3: Multiple Recipients (CC/BCC)

**CSV:**
```csv
To,CC,BCC,Subject,Entity Name,Invoice Number,Amount,Due Date,Attachment Path,Group,Custom Message
primary@example.com,cc1@example.com;cc2@example.com,bcc@example.com,,Test Multi,001,100.00,2026-03-01,,,
```

**Expected:** Email to primary with CC to two addresses and BCC to one

### Test 4: Custom Subject and Message

**CSV:**
```csv
To,CC,BCC,Subject,Entity Name,Invoice Number,Amount,Due Date,Attachment Path,Group,Custom Message
test@example.com,,,URGENT: Payment Required,Test Co,001,5000.00,2026-02-01,test.pdf,,Please pay immediately due to contract terms.
```

**Expected:** Email with custom subject and message displayed prominently

---

## Viewing Email in Different Formats

### View in Terminal (Text Preview)

```bash
python view_email.py output/your_email.eml
```

### Extract HTML for Browser Viewing

```bash
# Extract HTML body to file
python -c "
import email
from email import policy

with open('output/ACME Corporation_1.eml', 'rb') as f:
    msg = email.message_from_binary_file(f, policy=policy.default)

for part in msg.walk():
    if part.get_content_type() == 'text/html':
        with open('preview.html', 'w') as out:
            out.write(part.get_content())
        print('HTML saved to preview.html')
        break
"

# Open in browser
open preview.html  # Mac
xdg-open preview.html  # Linux
start preview.html  # Windows
```

### View Attachments

```bash
# List all attachments
python -c "
import email
from email import policy

with open('output/ACME Corporation_1.eml', 'rb') as f:
    msg = email.message_from_binary_file(f, policy=policy.default)

for part in msg.walk():
    if part.get_filename():
        print(f'Attachment: {part.get_filename()}')
"
```

---

## Windows Testing (MSG Files)

If you're testing on Windows with Outlook installed:

1. Set email format in `config/config.yaml`:
```yaml
email:
  format: "msg"  # Force MSG format
```

2. Install Windows dependencies:
```bash
pip install pywin32
```

3. Run the tool:
```bash
python -m src.main tests/sample_data.csv
```

4. Generated `.msg` files will open directly in Outlook

---

## Troubleshooting

### Problem: No emails generated

**Check:**
- CSV file path correct?
- CSV has required columns (To, Entity Name, Invoice Number)?
- Any error messages in output?

**Solution:** Run with `--verbose` to see detailed errors

### Problem: Attachments not found

**Check:**
- Attachment files exist at specified paths?
- `attachment_base` in config.yaml set correctly?
- Using correct relative/absolute paths?

**Solution:** Use `--skip-validation` for testing, or fix attachment paths

### Problem: Emails look wrong

**Check:**
- Template file at `config/template.html`?
- Company info in `config/config.yaml` correct?
- Invoice data in CSV complete?

**Solution:** Customize template and config files

### Problem: Grouping not working

**Check:**
- Group column exists in CSV?
- Group values EXACTLY the same (case-sensitive)?
- Group column name matches config (default: "Group")?

**Solution:** Verify Group column values are identical for rows to group

---

## Next Steps After Testing

Once you've verified the tool works:

1. **Customize Configuration**
   - Edit `config/config.yaml` with your company details
   - Update email addresses, company name, sender info

2. **Customize Template**
   - Edit `config/template.html` for your branding
   - Add company logo, change colors, modify layout

3. **Prepare Production Data**
   - Create your real invoice CSV file
   - Organize invoice PDF files
   - Set correct attachment paths

4. **Production Run**
   - Test with small batch first
   - Verify emails before sending
   - Use validation mode (remove `--skip-validation`)

5. **Report Issues**
   - Note any bugs or unexpected behavior
   - Suggest improvements for Advanced features

---

## Performance Testing

For large CSV files:

```bash
# Test with 100+ rows
python -m src.main large_data.csv --verbose

# Monitor performance
time python -m src.main large_data.csv
```

Expected performance:
- ~1-5 emails per second on typical hardware
- ~1000 emails in 3-5 minutes

---

**Happy Testing! 🎉**

If you encounter any issues, check the logs in `email_tool.log` or run with `--verbose` for detailed output.
