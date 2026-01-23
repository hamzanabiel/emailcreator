"""
Email Generator Module
Handles email template rendering and generation.
"""

from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

from src.msg_creator import EmailFileCreator
from src.utils import resolve_attachment_path, get_attachment_filename, format_timestamp, sanitize_filename

logger = logging.getLogger(__name__)


class EmailGenerator:
    """Generates email files from templates and data."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email generator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.template_path = config.get('paths', {}).get('template', 'config/template.html')
        self.output_dir = Path(config.get('paths', {}).get('output', 'output'))
        self.attachment_base = config.get('paths', {}).get('attachment_base', '')

        # Initialize Jinja2 environment
        template_file = Path(self.template_path)
        template_dir = template_file.parent
        template_name = template_file.name

        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.template = self.jinja_env.get_template(template_name)

        # Initialize email file creator
        self.email_creator = EmailFileCreator(config)

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Email generator initialized. Output: {self.output_dir}")

    def generate_email(self, email_data: Dict[str, Any]) -> Path:
        """
        Generate email file from email data.

        Args:
            email_data: Dictionary containing email information

        Returns:
            Path to generated email file
        """
        # Render HTML body
        html_body = self._render_template(email_data)

        # Resolve attachment paths
        attachment_paths = self._resolve_attachments(email_data.get('attachments', []))

        # Generate output filename
        output_path = self._generate_output_path(email_data)

        # Create email file
        email_file = self.email_creator.create_email_file(
            output_path=output_path,
            to=email_data.get('to', ''),
            subject=email_data.get('subject', 'Invoice Notification'),
            html_body=html_body,
            cc=email_data.get('cc', ''),
            bcc=email_data.get('bcc', ''),
            from_email=self.config.get('email', {}).get('from', ''),
            attachments=attachment_paths
        )

        logger.info(f"Generated email: {email_file.name}")
        return email_file

    def _render_template(self, email_data: Dict[str, Any]) -> str:
        """
        Render HTML email template with data.

        Args:
            email_data: Dictionary containing email information

        Returns:
            Rendered HTML string
        """
        # Prepare template context
        context = {
            'company_name': self.config.get('company', {}).get('name', 'Your Company'),
            'sender_name': self.config.get('company', {}).get('sender_name', 'Accounts Receivable'),
            'sender_title': self.config.get('company', {}).get('sender_title', 'Billing Department'),
            'current_year': datetime.now().year,
            'is_group': email_data.get('is_group', False),
            'custom_message': email_data.get('custom_message', ''),
        }

        # Add banner path if exists
        banner_path = self.config.get('paths', {}).get('banner')
        if banner_path and Path(banner_path).exists():
            context['banner_path'] = banner_path

        # Add attachments list (filenames only)
        attachments = email_data.get('attachments', [])
        if attachments:
            context['attachments'] = [Path(a).name for a in attachments]

        if email_data.get('is_group'):
            # Group email context
            context.update({
                'group_name': email_data.get('group_name', ''),
                'invoices': email_data.get('invoices', [])
            })
        else:
            # Single invoice context
            context.update({
                'entity_name': email_data.get('entity_name', ''),
                'invoice_number': email_data.get('invoice_number', ''),
                'amount': email_data.get('amount', ''),
                'due_date': email_data.get('due_date', ''),
                'recipient_name': self._extract_recipient_name(email_data.get('to', ''))
            })

        # Render template
        return self.template.render(**context)

    def _resolve_attachments(self, attachment_list: List[str]) -> List[Path]:
        """
        Resolve attachment paths to absolute paths.

        Args:
            attachment_list: List of attachment file paths

        Returns:
            List of resolved Path objects
        """
        resolved = []

        for attachment in attachment_list:
            if not attachment:
                continue

            resolved_path = resolve_attachment_path(attachment, self.attachment_base)

            if resolved_path.exists():
                resolved.append(resolved_path)
            else:
                logger.warning(f"Attachment not found: {attachment}")

        return resolved

    def _generate_output_path(self, email_data: Dict[str, Any]) -> Path:
        """
        Generate output file path for email.

        Args:
            email_data: Dictionary containing email information

        Returns:
            Path object for output file (without extension)
        """
        # Get filename pattern from config
        pattern = self.config.get('output', {}).get('filename_pattern', '{entity}_{invoice}_{timestamp}')
        add_timestamp = self.config.get('output', {}).get('timestamp', True)

        # Prepare variables
        if email_data.get('is_group'):
            entity = email_data.get('group_name', 'Group')
            invoice = 'Multiple'
        else:
            entity = email_data.get('entity_name', 'Entity')
            invoice = email_data.get('invoice_number', '0000')

        # Format filename
        filename = pattern.format(
            entity=sanitize_filename(entity),
            group=sanitize_filename(email_data.get('group_name', 'Group')),
            invoice=sanitize_filename(invoice),
            timestamp=format_timestamp() if add_timestamp else ''
        )

        # Remove trailing underscores
        filename = filename.rstrip('_')

        # Create full path
        return self.output_dir / filename

    @staticmethod
    def _extract_recipient_name(email: str) -> str:
        """
        Extract recipient name from email address.

        Args:
            email: Email address

        Returns:
            Recipient name or 'Valued Customer'
        """
        if not email or '@' not in email:
            return 'Valued Customer'

        # Get first email if multiple
        first_email = email.split(',')[0].split(';')[0].strip()

        # Extract name part before @
        name_part = first_email.split('@')[0]

        # Replace dots and underscores with spaces, capitalize
        name = name_part.replace('.', ' ').replace('_', ' ').title()

        return name if name else 'Valued Customer'

    def generate_batch(self, email_groups: List[Dict[str, Any]]) -> List[Path]:
        """
        Generate multiple email files from list of email groups.

        Args:
            email_groups: List of email data dictionaries

        Returns:
            List of generated email file paths
        """
        generated_files = []

        logger.info(f"Generating {len(email_groups)} email files...")

        for i, email_data in enumerate(email_groups, 1):
            try:
                email_file = self.generate_email(email_data)
                generated_files.append(email_file)
                logger.debug(f"Progress: {i}/{len(email_groups)}")
            except Exception as e:
                logger.error(f"Error generating email {i}: {str(e)}")
                continue

        logger.info(f"Successfully generated {len(generated_files)} email files")
        return generated_files
