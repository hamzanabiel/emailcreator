# CSV Email Tool - Web Frontend Guide

## 🎉 Quick Start

### 1. Install Dependencies

```bash
# Make sure you're in the emailcreator directory
cd /path/to/emailcreator

# Install all dependencies (including frontend)
pip install -r requirements.txt
```

### 2. Start the Web Interface

```bash
python api/app.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 3. Open in Browser

Open your web browser and go to:
```
http://localhost:8000
```

You should see the CSV Email Tool web interface! 🎊

---

## 📖 Using the Web Interface

### Tab 1: CSV Data

**Upload Your CSV:**
1. Drag & drop your CSV file into the upload area
2. Or click the area to browse and select a file

**Edit Data:**
- Click any cell to edit
- Changes save automatically
- Use column filters to search
- Pagination controls at bottom

**Add Rows:**
- Click "Add Row" button
- New empty row appears at bottom

**Validate:**
- Click "Validate" button
- Shows errors (red) and warnings (yellow)
- Lists issues with row numbers

---

### Tab 2: Configuration

**Company Information:**
- Company Name
- Sender Name & Title
- From Email Address

**Email Settings:**
- Subject line templates
  - Single: `{entity_name} Invoice {invoice_number}`
  - Group: `{group_name} Invoices {invoice_numbers}`

**File Paths:**
- Attachment Base Directory: Where your PDF files are
- Output Directory: Where generated emails are saved

**Save:**
- Click "Save Configuration" when done
- Green notification confirms save

---

### Tab 3: Email Template

**Code Editor (Left Side):**
- Edit HTML template
- Syntax highlighting
- Line numbers
- Auto-saves preview as you type

**Live Preview (Right Side):**
- Shows how email will look
- Updates automatically (1 second after you stop typing)
- Uses sample data

**Save Template:**
- Click "Save Template" button
- Or press Ctrl/Cmd + S

**Tip:** Use Jinja2 variables:
- `{{ entity_name }}`
- `{{ invoice_number }}`
- `{{ amount }}`
- `{{ due_date }}`
- `{{ custom_message }}`

---

### Tab 4: Generate

**Review Summary:**
- Shows how many rows loaded
- Explains what will happen

**Generate Emails:**
1. Click "Generate Emails" button
2. Progress bar shows status
3. Success message shows:
   - Number of emails created
   - List of filenames
4. Click "View Emails" to see them

**Download All:**
- Click "Download All" for zip file

---

### Tab 5: View Emails

**Email List (Left):**
- Lists all generated .eml files
- Click any email to preview

**Email Preview (Right):**
- Shows email headers (From, To, CC, BCC, Subject)
- Shows attachments
- Shows formatted email body
- Buttons:
  - **Download:** Save .eml file to your computer
  - **Open in Email Client:** Download and open in Outlook/Mail

**Refresh:**
- Click "Refresh" to reload list

**Download All:**
- Gets all emails as a zip file

---

## 🔧 Common Tasks

### Generate Emails from CSV

1. **Upload CSV** (Tab 1)
   - Drag & drop your CSV file
   - Wait for it to load

2. **Check Configuration** (Tab 2)
   - Verify company info is correct
   - Check attachment base path
   - Save if you made changes

3. **Preview Template** (Tab 3 - Optional)
   - See how emails will look
   - Make any design changes

4. **Generate** (Tab 4)
   - Click "Generate Emails"
   - Wait for completion
   - View results

5. **View & Download** (Tab 5)
   - Preview generated emails
   - Download individual files
   - Or download all as zip

---

### Edit Email Template

1. Go to "Email Template" tab
2. Edit HTML in left panel
3. See changes in right panel (live preview)
4. Click "Save Template" when done
5. Generate new emails with updated template

---

### Change Company Info

1. Go to "Configuration" tab
2. Update company name, sender, etc.
3. Click "Save Configuration"
4. New emails will use updated info

---

### Validate CSV Before Generating

1. Upload CSV (Tab 1)
2. Click "Validate" button
3. Review any errors:
   - ✗ Red = Errors (must fix)
   - ⚠️ Yellow = Warnings (optional)
4. Fix issues in CSV
5. Validate again until all pass

---

## 🎯 Features

### CSV Editor
✅ Spreadsheet-style editing
✅ Click to edit any cell
✅ Auto-save changes
✅ Column filters
✅ Pagination (25 rows per page)
✅ Add rows
✅ Validation

### Template Editor
✅ Syntax highlighting
✅ Line numbers
✅ Auto-completion
✅ Live preview
✅ Keyboard shortcuts (Ctrl/Cmd + S to save)

### Email Generation
✅ Progress indicator
✅ Success/error notifications
✅ Detailed file list
✅ Automatic grouping

### Email Viewer
✅ List all generated emails
✅ Preview in browser
✅ Download individual or all
✅ Open in email client

---

## 💡 Tips & Tricks

### Keyboard Shortcuts

**Template Editor:**
- `Ctrl/Cmd + S` - Save template
- `Ctrl + Space` - Auto-complete

**General:**
- Click tab names to switch views
- Use browser Back button = still works!

### CSV Editing

**Multiple Recipients:**
```csv
To,CC
john@example.com,"manager@example.com;cfo@example.com"
```
Use semicolon to separate multiple emails

**Grouping Invoices:**
```csv
Entity Name,Invoice Number,Group
ACME Widget,001,ACME
ACME Gadget,002,ACME
```
Same "Group" value = combined into 1 email

### Template Variables

**Available variables:**
- `{{ company_name }}` - Your company name
- `{{ sender_name }}` - Sender name
- `{{ entity_name }}` - Customer/entity name
- `{{ invoice_number }}` - Invoice number
- `{{ amount }}` - Invoice amount
- `{{ due_date }}` - Due date
- `{{ custom_message }}` - Custom message from CSV
- `{{ attachments }}` - List of attachment files

**For grouped emails:**
- `{{ group_name }}` - Group name
- `{{ invoices }}` - List of all invoices
  ```html
  {% for invoice in invoices %}
    {{ invoice.entity_name }} - {{ invoice.invoice_number }}
  {% endfor %}
  ```

---

## 🔍 Troubleshooting

### Can't Access Web Interface

**Problem:** Browser shows "Can't connect"

**Solution:**
1. Check terminal - is server running?
2. Look for: "Uvicorn running on http://127.0.0.1:8000"
3. If not running: `python api/app.py`
4. Try: `http://localhost:8000` instead of `http://127.0.0.1:8000`

---

### CSV Won't Upload

**Problem:** "Error uploading CSV"

**Solutions:**
1. Check file is actually .csv (not .xlsx or .xls)
2. Check CSV has required columns:
   - To
   - Entity Name
   - Invoice Number
3. Try with the sample data first:
   ```bash
   # Use the included sample
   tests/sample_data.csv
   ```

---

### Template Preview Not Showing

**Problem:** Preview area is blank or shows error

**Solutions:**
1. Check HTML syntax - look for missing `>` or unclosed tags
2. Click "Refresh Preview" button
3. Check browser console for errors (F12)

---

### Emails Not Generating

**Problem:** Click Generate but nothing happens

**Solutions:**
1. Check CSV is uploaded (Tab 1 should show table, not upload area)
2. Check terminal for error messages
3. Try validating CSV first (look for errors)
4. Check attachment paths exist
5. Check output directory is writable

---

### Attachments Not Found

**Problem:** "Attachment file not found" errors

**Solutions:**
1. Go to Configuration tab
2. Check "Attachment Base Directory" path
3. Make sure PDF files are in that directory
4. Or use absolute paths in CSV:
   ```csv
   Attachment Path
   /full/path/to/invoice.pdf
   ```

---

## 🚀 Advanced Usage

### API Documentation

The web interface includes auto-generated API docs:

```
http://localhost:8000/api/docs
```

**Features:**
- Interactive API explorer
- Try endpoints directly in browser
- See request/response schemas
- Test with your data

---

### Running on Different Port

```bash
# Change from 8000 to 5000
python -c "
import uvicorn
from api.app import app
uvicorn.run(app, host='127.0.0.1', port=5000)
"
```

Then open: `http://localhost:5000`

---

### Accessing from Other Devices (Same Network)

```bash
# Run on all network interfaces
python -c "
import uvicorn
from api.app import app
uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

Then access from other devices:
```
http://YOUR-IP-ADDRESS:8000
```

Find your IP:
- Mac: System Preferences → Network
- Windows: `ipconfig` in cmd
- Linux: `ifconfig` or `ip addr`

**⚠️ Security Note:** Only do this on trusted networks!

---

## 📁 Project Structure

```
emailcreator/
├── api/                      # NEW - Web API layer
│   ├── app.py               # FastAPI app (start here)
│   ├── routes.py            # API endpoints
│   └── models.py            # Request/response schemas
│
├── frontend/                # NEW - Web UI
│   ├── index.html           # Main page
│   ├── css/
│   │   └── styles.css       # Styling
│   └── js/
│       ├── app.js           # Main app controller
│       ├── csv-editor.js    # CSV editing
│       ├── config-editor.js # Configuration form
│       ├── template-editor.js # Template editing
│       ├── email-generator.js # Email generation
│       └── email-viewer.js  # Email viewing
│
├── src/                     # UNCHANGED - Backend code
│   ├── csv_parser.py       # (still works from CLI)
│   ├── email_generator.py
│   └── ...
│
├── config/                  # Configuration files
│   ├── config.yaml         # Settings
│   └── template.html       # Email template
│
└── output/                  # Generated emails
```

---

## 🎓 Learning Resources

### Customizing the Template

The email template uses **Jinja2** templating language:

**Official Docs:** https://jinja.palletsprojects.com/

**Common patterns:**

```html
<!-- Conditional display -->
{% if custom_message %}
  <p>{{ custom_message }}</p>
{% endif %}

<!-- Loop through list -->
{% for invoice in invoices %}
  <div>Invoice #{{ invoice.invoice_number }}</div>
{% endfor %}

<!-- Default value -->
{{ amount or '0.00' }}
```

### Modifying the UI

The frontend uses:
- **Bootstrap 5:** https://getbootstrap.com/
- **Tabulator:** https://tabulator.info/ (spreadsheet)
- **CodeMirror:** https://codemirror.net/ (code editor)

Edit files in `frontend/` to customize:
- `index.html` - Structure
- `css/styles.css` - Styling
- `js/*.js` - Functionality

---

## ✅ Quick Checklist

Before first use:

- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Started server (`python api/app.py`)
- [ ] Opened browser to `http://localhost:8000`
- [ ] Updated company info (Configuration tab)
- [ ] Set attachment base path (Configuration tab)
- [ ] Saved configuration

To generate emails:

- [ ] Upload CSV file (CSV Data tab)
- [ ] Validate CSV (check for errors)
- [ ] Review template (Email Template tab)
- [ ] Click Generate (Generate tab)
- [ ] View results (View Emails tab)

---

## 🎉 You're Ready!

The web interface makes it easy to:
✅ Upload and edit CSV files
✅ Configure company settings
✅ Customize email templates
✅ Generate emails with one click
✅ Preview and download results

**Everything your CLI tool does, now with a friendly UI!**

Need help? Check the troubleshooting section or the API docs at `/api/docs`.

**Happy emailing! 📧**
