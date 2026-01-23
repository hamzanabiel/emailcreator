"""
Pydantic Models for API Request/Response Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    api: str

class CSVUploadResponse(BaseModel):
    """Response after CSV upload"""
    success: bool
    message: str
    rows: int
    columns: List[str]
    data: List[Dict[str, Any]]

class CSVValidationResponse(BaseModel):
    """CSV validation response"""
    valid: bool
    errors: List[str]
    warnings: List[str]

class ConfigResponse(BaseModel):
    """Configuration response"""
    config: Dict[str, Any]

class ConfigUpdateRequest(BaseModel):
    """Configuration update request"""
    config: Dict[str, Any]

class TemplateResponse(BaseModel):
    """Template response"""
    html: str
    path: str

class TemplateUpdateRequest(BaseModel):
    """Template update request"""
    html: str

class TemplatePreviewRequest(BaseModel):
    """Template preview request"""
    html: str
    sample_data: Optional[Dict[str, Any]] = None

class GenerateRequest(BaseModel):
    """Email generation request"""
    csv_data: Optional[List[Dict[str, Any]]] = None
    use_uploaded_csv: bool = True

class GenerateResponse(BaseModel):
    """Email generation response"""
    success: bool
    count: int
    files: List[str]
    errors: List[str] = []

class EmailListResponse(BaseModel):
    """List of generated emails"""
    emails: List[Dict[str, Any]]
    count: int

class EmailDetailResponse(BaseModel):
    """Details of a single email"""
    filename: str
    from_addr: str
    to: str
    cc: Optional[str]
    bcc: Optional[str]
    subject: str
    html_preview: str
    attachments: List[str]
    size: int

class AttachmentUploadResponse(BaseModel):
    """Attachment upload response"""
    success: bool
    filename: str
    path: str
    size: int

class AttachmentListResponse(BaseModel):
    """List of attachments"""
    attachments: List[Dict[str, str]]
    count: int
