# CSV Email Tool - Quick Start Guide

## ✅ Tool is Ready and Tested!

All 20 automated tests passed. The tool is working correctly.

---

## 🚀 How to Test (3 Easy Ways)

### Method 1: Automated Test (Recommended)
```bash
python run_tests.py
```
**What it does:** Runs 20 automated tests and shows you a complete report

---

### Method 2: Manual Test with Sample Data
```bash
# Generate sample emails
python -m src.main tests/sample_data.csv --skip-validation

# View what was created
ls -lh output/

# View an email in terminal
python view_email.py "output/ACME Corporation_1.eml"
```
**What it does:** Creates 8 test emails you can inspect

---

### Method 3: View Emails in Your Email Client

1. Navigate to the `output/` directory
2. Double-click any `.eml` file
3. It will open in your default email client (Outlook, Apple Mail, etc.)
4. You can see the full HTML email with formatting and attachments

**On Linux without email client:**
```bash
# Extract HTML and open in browser
python -c "
import email
from email import policy

with open('output/ACME Corporation_1.eml', 'rb') as f:
    msg = email.message_from_binary_file(f, policy=policy.default)
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            with open('preview.html', 'w') as out:
                out.write(part.get_content())
            print('Saved to preview.html')
            break
"

# Open in browser
xdg-open preview.html  # Linux
open preview.html      # Mac
start preview.html     # Windows
```

---

## 📊 What the Sample Data Tests

The included `tests/sample_data.csv` demonstrates:

✅ **Single invoice emails** (6 emails)
- Basic invoices
- Invoices with CC recipients
- Invoices with custom messages
- Invoices with custom subjects

✅ **Grouped invoice emails** (2 invoices → 1 email)
- BigCorp Group: Combines 2 invoices into 1 email
- Includes CC and BCC recipients
- All attachments included

✅ **Special features**
- Custom subject lines
- Custom messages
- Multiple recipients (To, CC, BCC)
- Attachments
- Different amounts and due dates

---

## 🔍 What to Look For When Testing

### In the Generated Emails:

1. **Headers**
   - ✅ From: billing@yourcompany.com
   - ✅ To: Correct recipient
   - ✅ CC/BCC: When specified in CSV
   - ✅ Subject: Entity Invoice Number format

2. **Email Body**
   - ✅ Professional HTML formatting
   - ✅ Company name displayed
   - ✅ Invoice details table (Invoice #, Amount, Due Date)
   - ✅ Custom message (when provided)
   - ✅ Attachment list
   - ✅ Company footer

3. **Attachments**
   - ✅ PDF files attached
   - ✅ Correct filenames
   - ✅ Downloadable from email

4. **Grouped Emails**
   - ✅ Subject: "BigCorp Group Invoices 0003 / 0004"
   - ✅ Multiple invoice sections in body
   - ✅ All attachments from both invoices

---

## 📁 Generated Files Location

All generated emails are in: `output/`

Expected files from sample data:
```
output/
├── ACME Corporation_1.eml          (Single invoice)
├── Tech Solutions LLC_2.eml        (Single invoice)
├── BigCorp Group_Multiple_*.eml    (Grouped: 2 invoices)
├── MidSize Company_5.eml           (Single invoice)
├── StartUp Inc_6.eml               (Single invoice)
├── Enterprise Corp_7.eml           (Single invoice)
└── Small Business Co_8.eml         (Single invoice)
```

---

## 🎯 Understanding Test Results

### Automated Test Results (run_tests.py)

```
Total Tests:  20
Passed:       20   ← All features working!
Failed:       0    ← No errors!
Success Rate: 100%
```

**What each test verifies:**
- Dependencies installed ✓
- Project files present ✓
- Email generation works ✓
- Correct number of emails created ✓
- Email headers populated ✓
- Email content formatted ✓
- Grouping works ✓
- Attachments included ✓

---

## 🔧 Testing Your Own Data

### Quick Test with Your CSV:

1. **Create a simple test CSV:**
```csv
To,CC,BCC,Subject,Entity Name,Invoice Number,Amount,Due Date,Attachment Path,Group,Custom Message
your.email@example.com,,,Test Invoice,Test Company,001,100.00,2026-03-01,,,Testing the tool!
```

2. **Save as** `my_test.csv`

3. **Place any PDF in** `tests/attachments/` (or use absolute path)

4. **Run:**
```bash
python -m src.main my_test.csv --skip-validation
```

5. **Check** `output/` for your email file

6. **Open the .eml file** in your email client

---

## ⚙️ Command Options

```bash
# Basic run
python -m src.main data.csv

# Skip validation (faster, for testing)
python -m src.main data.csv --skip-validation

# Verbose output (see detailed logs)
python -m src.main data.csv --verbose

# Custom config file
python -m src.main data.csv --config my_config.yaml

# Get help
python -m src.main --help
```

---

## 📖 Need More Details?

- **Comprehensive Testing:** See `TESTING_GUIDE.md`
- **Usage Instructions:** See `USAGE.md`
- **Project Status:** See `PROJECT_STATUS.md`
- **Original Documentation:** See `README.md`

---

## ✅ Testing Checklist

Before using with real data, verify:

- [ ] Ran automated tests (`python run_tests.py`)
- [ ] All 20 tests passed
- [ ] Opened generated .eml files in email client
- [ ] Verified email formatting looks professional
- [ ] Checked attachments open correctly
- [ ] Tested grouped emails (multiple invoices)
- [ ] Reviewed email content for accuracy
- [ ] Customized config.yaml with your company info
- [ ] Customized template.html with your branding

---

## 🐛 If Something Doesn't Work

1. **Check the log file:** `email_tool.log`
2. **Run with verbose mode:** `python -m src.main data.csv --verbose`
3. **Verify CSV format:** Check column names match config
4. **Check attachments:** Files exist at specified paths
5. **Review validation errors:** Run without `--skip-validation`

---

## 🎉 You're Ready!

The tool has been tested and is working correctly. You can now:

1. ✅ Test with your own CSV data
2. ✅ Customize the configuration
3. ✅ Customize the email template
4. ✅ Use for production email generation

**Happy email generating!** 📧
