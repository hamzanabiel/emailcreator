"""
API Routes - REST Endpoints for Frontend
All routes wrap existing backend functionality without modifying it
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import yaml
import logging
import shutil
import zipfile
import io
import email
from email import policy
import tempfile
import os

# Import existing backend modules (UNCHANGED)
from src.csv_parser import CSVParser
from src.utils import EmailGrouper
from src.email_generator import EmailGenerator

from api.models import *

logger = logging.getLogger(__name__)
router = APIRouter()

# Global storage for uploaded CSV (in-memory for MVP)
uploaded_csv_data = None
uploaded_csv_df = None

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    config_path = Path("config/config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def save_config(config: Dict[str, Any]):
    """Save configuration to config.yaml"""
    config_path = Path("config/config.yaml")
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

# ============================================================================
# CSV MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/csv/upload", response_model=CSVUploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload and parse CSV file
    Returns preview data for spreadsheet editor
    """
    global uploaded_csv_data, uploaded_csv_df

    try:
        # Read file content
        content = await file.read()

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb')
        temp_file.write(content)
        temp_file.close()

        # Parse CSV using existing backend
        config = load_config()
        parser = CSVParser(config)
        df = parser.parse_csv(temp_file.name)

        # Store in memory
        uploaded_csv_df = df
        uploaded_csv_data = df.to_dict('records')

        # Clean up temp file
        os.unlink(temp_file.name)

        logger.info(f"CSV uploaded: {len(df)} rows, {len(df.columns)} columns")

        return CSVUploadResponse(
            success=True,
            message=f"Successfully uploaded {file.filename}",
            rows=len(df),
            columns=df.columns.tolist(),
            data=uploaded_csv_data
        )

    except Exception as e:
        logger.error(f"Error uploading CSV: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/csv/validate", response_model=CSVValidationResponse)
async def validate_csv():
    """
    Validate uploaded CSV data
    Checks email addresses and attachments
    """
    global uploaded_csv_df

    if uploaded_csv_df is None:
        raise HTTPException(status_code=400, detail="No CSV uploaded")

    try:
        config = load_config()
        parser = CSVParser(config)

        # Validate emails
        email_errors = parser.validate_emails(uploaded_csv_df)

        # Validate attachments
        attachment_base = config.get('paths', {}).get('attachment_base', '')
        attachment_errors = parser.validate_attachments(uploaded_csv_df, attachment_base)

        all_errors = email_errors + attachment_errors

        return CSVValidationResponse(
            valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=[]
        )

    except Exception as e:
        logger.error(f"Error validating CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/csv/update")
async def update_csv(data: List[Dict[str, Any]]):
    """
    Update CSV data from spreadsheet editor
    """
    global uploaded_csv_data, uploaded_csv_df

    try:
        # Update stored data
        uploaded_csv_data = data
        uploaded_csv_df = pd.DataFrame(data)

        logger.info(f"CSV updated: {len(data)} rows")

        return {"success": True, "message": "CSV data updated", "rows": len(data)}

    except Exception as e:
        logger.error(f"Error updating CSV: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/csv/data")
async def get_csv_data():
    """Get current CSV data"""
    global uploaded_csv_data

    if uploaded_csv_data is None:
        return {"data": [], "rows": 0}

    return {"data": uploaded_csv_data, "rows": len(uploaded_csv_data)}

# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """Get current configuration"""
    try:
        config = load_config()
        return ConfigResponse(config=config)
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config")
async def update_config(request: ConfigUpdateRequest):
    """Update configuration"""
    try:
        save_config(request.config)
        logger.info("Configuration updated")
        return {"success": True, "message": "Configuration saved"}
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TEMPLATE ENDPOINTS
# ============================================================================

@router.get("/template", response_model=TemplateResponse)
async def get_template():
    """Get current email template"""
    try:
        config = load_config()
        template_path = Path(config.get('paths', {}).get('template', 'config/template.html'))

        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()

        return TemplateResponse(html=html, path=str(template_path))
    except Exception as e:
        logger.error(f"Error loading template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/template")
async def update_template(request: TemplateUpdateRequest):
    """Update email template"""
    try:
        config = load_config()
        template_path = Path(config.get('paths', {}).get('template', 'config/template.html'))

        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(request.html)

        logger.info("Template updated")
        return {"success": True, "message": "Template saved"}
    except Exception as e:
        logger.error(f"Error saving template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/template/preview")
async def preview_template(request: TemplatePreviewRequest):
    """
    Preview template with sample data
    Renders the template and returns HTML
    """
    try:
        from jinja2 import Template
        from datetime import datetime

        # Default sample data
        sample = request.sample_data or {
            'company_name': 'Your Company Name',
            'sender_name': 'Accounts Receivable',
            'sender_title': 'Billing Department',
            'current_year': datetime.now().year,
            'is_group': False,
            'entity_name': 'ACME Corporation',
            'invoice_number': '0001',
            'amount': '2,500.00',
            'due_date': '2026-02-15',
            'custom_message': 'Thank you for your business',
            'attachments': ['invoice_0001.pdf'],
            'recipient_name': 'John Doe'
        }

        # Render template
        template = Template(request.html)
        rendered = template.render(**sample)

        return {"html": rendered}

    except Exception as e:
        logger.error(f"Error previewing template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# EMAIL GENERATION ENDPOINT
# ============================================================================

@router.post("/generate", response_model=GenerateResponse)
async def generate_emails():
    """
    Generate email files from uploaded CSV
    Uses existing backend functionality
    """
    global uploaded_csv_df

    if uploaded_csv_df is None:
        raise HTTPException(status_code=400, detail="No CSV data available. Please upload a CSV file first.")

    try:
        # Load configuration
        config = load_config()

        # Use existing backend code (UNCHANGED)
        logger.info("Starting email generation...")

        # Group emails
        grouper = EmailGrouper(config)
        email_groups = grouper.group_emails(uploaded_csv_df)
        logger.info(f"Created {len(email_groups)} email groups")

        # Generate emails
        generator = EmailGenerator(config)
        files = generator.generate_batch(email_groups)
        logger.info(f"Generated {len(files)} email files")

        return GenerateResponse(
            success=True,
            count=len(files),
            files=[f.name for f in files],
            errors=[]
        )

    except Exception as e:
        logger.error(f"Error generating emails: {str(e)}", exc_info=True)
        return GenerateResponse(
            success=False,
            count=0,
            files=[],
            errors=[str(e)]
        )

# ============================================================================
# EMAIL VIEWING ENDPOINTS
# ============================================================================

@router.get("/emails", response_model=EmailListResponse)
async def list_emails():
    """List all generated email files"""
    try:
        config = load_config()
        output_dir = Path(config.get('paths', {}).get('output', 'output'))

        if not output_dir.exists():
            return EmailListResponse(emails=[], count=0)

        emails = []
        for file in output_dir.glob('*.eml'):
            emails.append({
                'filename': file.name,
                'size': file.stat().st_size,
                'modified': file.stat().st_mtime
            })

        # Sort by modification time (newest first)
        emails.sort(key=lambda x: x['modified'], reverse=True)

        return EmailListResponse(emails=emails, count=len(emails))

    except Exception as e:
        logger.error(f"Error listing emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emails/{filename}")
async def get_email_details(filename: str):
    """Get details of a specific email file"""
    try:
        config = load_config()
        output_dir = Path(config.get('paths', {}).get('output', 'output'))
        email_path = output_dir / filename

        if not email_path.exists():
            raise HTTPException(status_code=404, detail="Email file not found")

        # Parse email file
        with open(email_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=policy.default)

        # Extract HTML body
        html_preview = ""
        attachments = []

        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                html_preview = part.get_content()
            elif part.get_filename():
                attachments.append(part.get_filename())

        return EmailDetailResponse(
            filename=filename,
            from_addr=msg.get('From', ''),
            to=msg.get('To', ''),
            cc=msg.get('Cc', ''),
            bcc=msg.get('Bcc', ''),
            subject=msg.get('Subject', ''),
            html_preview=html_preview,
            attachments=attachments,
            size=email_path.stat().st_size
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting email details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emails/{filename}/download")
async def download_email(filename: str):
    """Download a specific email file"""
    try:
        config = load_config()
        output_dir = Path(config.get('paths', {}).get('output', 'output'))
        email_path = output_dir / filename

        if not email_path.exists():
            raise HTTPException(status_code=404, detail="Email file not found")

        return FileResponse(
            email_path,
            media_type='message/rfc822',
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emails/download-all/zip")
async def download_all_emails():
    """Download all emails as a zip file"""
    try:
        config = load_config()
        output_dir = Path(config.get('paths', {}).get('output', 'output'))

        if not output_dir.exists():
            raise HTTPException(status_code=404, detail="No emails found")

        # Create zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for email_file in output_dir.glob('*.eml'):
                zip_file.write(email_file, email_file.name)

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type='application/zip',
            headers={'Content-Disposition': 'attachment; filename=emails.zip'}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating zip: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ATTACHMENT ENDPOINTS
# ============================================================================

@router.post("/attachments/upload", response_model=AttachmentUploadResponse)
async def upload_attachment(file: UploadFile = File(...)):
    """Upload an attachment file (PDF)"""
    try:
        config = load_config()
        attachment_base = Path(config.get('paths', {}).get('attachment_base', 'attachments'))
        attachment_base.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = attachment_base / file.filename
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)

        logger.info(f"Attachment uploaded: {file.filename}")

        return AttachmentUploadResponse(
            success=True,
            filename=file.filename,
            path=str(file_path),
            size=file_path.stat().st_size
        )

    except Exception as e:
        logger.error(f"Error uploading attachment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/attachments", response_model=AttachmentListResponse)
async def list_attachments():
    """List all available attachments"""
    try:
        config = load_config()
        attachment_base = Path(config.get('paths', {}).get('attachment_base', 'attachments'))

        if not attachment_base.exists():
            return AttachmentListResponse(attachments=[], count=0)

        attachments = []
        for file in attachment_base.glob('*.pdf'):
            attachments.append({
                'filename': file.name,
                'path': str(file),
                'size': file.stat().st_size
            })

        return AttachmentListResponse(attachments=attachments, count=len(attachments))

    except Exception as e:
        logger.error(f"Error listing attachments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/attachments/{filename}")
async def delete_attachment(filename: str):
    """Delete an attachment file"""
    try:
        config = load_config()
        attachment_base = Path(config.get('paths', {}).get('attachment_base', 'attachments'))
        file_path = attachment_base / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Attachment not found")

        file_path.unlink()
        logger.info(f"Attachment deleted: {filename}")

        return {"success": True, "message": f"Deleted {filename}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting attachment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/stats")
async def get_stats():
    """Get statistics about generated emails"""
    try:
        config = load_config()
        output_dir = Path(config.get('paths', {}).get('output', 'output'))

        if not output_dir.exists():
            return {"total_emails": 0, "total_size": 0}

        emails = list(output_dir.glob('*.eml'))
        total_size = sum(f.stat().st_size for f in emails)

        return {
            "total_emails": len(emails),
            "total_size": total_size,
            "csv_loaded": uploaded_csv_df is not None,
            "csv_rows": len(uploaded_csv_df) if uploaded_csv_df is not None else 0
        }

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
