"""
Utility Functions Module
Contains helper functions for grouping, formatting, and validation.
"""

import pandas as pd
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EmailGrouper:
    """Handles grouping of emails based on CSV data."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email grouper with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.csv_columns = config.get('csv_columns', {})
        self.grouping = config.get('grouping', {})

    def group_emails(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Group DataFrame rows into individual or grouped emails.

        Args:
            df: DataFrame with email data

        Returns:
            List of email group dictionaries
        """
        email_groups = []
        group_col = self.csv_columns.get('group')

        # Check if grouping column exists and has values
        has_groups = group_col and group_col in df.columns

        if has_groups:
            # Process groups
            grouped_df = df.groupby(group_col)

            for group_name, group_data in grouped_df:
                if pd.isna(group_name) or str(group_name).strip() == '':
                    # No group specified - create individual emails
                    for _, row in group_data.iterrows():
                        email_groups.append(self._create_single_email(row))
                else:
                    # Create grouped email
                    email_groups.append(self._create_group_email(group_name, group_data))
        else:
            # No grouping column - create individual emails for all rows
            for _, row in df.iterrows():
                email_groups.append(self._create_single_email(row))

        logger.info(f"Created {len(email_groups)} email groups")
        return email_groups

    def _create_single_email(self, row: pd.Series) -> Dict[str, Any]:
        """
        Create email data dictionary for a single invoice.

        Args:
            row: DataFrame row

        Returns:
            Email data dictionary
        """
        entity_name = str(row.get(self.csv_columns.get('entity_name', ''), ''))
        invoice_number = str(row.get(self.csv_columns.get('invoice_number', ''), ''))

        # Get subject line (use custom if provided, otherwise generate)
        subject_col = self.csv_columns.get('subject')
        if subject_col and row.get(subject_col):
            subject = str(row[subject_col])
        else:
            # Generate subject: "EntityName Invoice 0001"
            subject = self._format_single_subject(entity_name, invoice_number)

        # Parse attachment path
        attachments = self._parse_attachments(row)

        return {
            'type': 'single',
            'to': self._get_email_field(row, 'to'),
            'cc': self._get_email_field(row, 'cc'),
            'bcc': self._get_email_field(row, 'bcc'),
            'subject': subject,
            'entity_name': entity_name,
            'invoice_number': invoice_number,
            'amount': str(row.get(self.csv_columns.get('amount', ''), '')),
            'due_date': str(row.get(self.csv_columns.get('due_date', ''), '')),
            'custom_message': str(row.get(self.csv_columns.get('custom_message', ''), '')),
            'attachments': attachments,
            'is_group': False
        }

    def _create_group_email(self, group_name: str, group_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Create email data dictionary for grouped invoices.

        Args:
            group_name: Name of the group
            group_data: DataFrame containing group rows

        Returns:
            Email data dictionary
        """
        # Use first row for common fields (To, CC, BCC)
        first_row = group_data.iloc[0]

        # Collect all invoice numbers
        invoice_numbers = [
            str(row.get(self.csv_columns.get('invoice_number', ''), ''))
            for _, row in group_data.iterrows()
        ]

        # Generate subject: "GroupName Invoices 0001 / 0002 / 0003"
        subject = self._format_group_subject(group_name, invoice_numbers)

        # Collect invoices data
        invoices = []
        all_attachments = []

        for _, row in group_data.iterrows():
            invoices.append({
                'entity_name': str(row.get(self.csv_columns.get('entity_name', ''), '')),
                'invoice_number': str(row.get(self.csv_columns.get('invoice_number', ''), '')),
                'amount': str(row.get(self.csv_columns.get('amount', ''), '')),
                'due_date': str(row.get(self.csv_columns.get('due_date', ''), ''))
            })

            # Collect all attachments
            attachments = self._parse_attachments(row)
            all_attachments.extend(attachments)

        return {
            'type': 'group',
            'to': self._get_email_field(first_row, 'to'),
            'cc': self._get_email_field(first_row, 'cc'),
            'bcc': self._get_email_field(first_row, 'bcc'),
            'subject': subject,
            'group_name': str(group_name),
            'invoices': invoices,
            'custom_message': str(first_row.get(self.csv_columns.get('custom_message', ''), '')),
            'attachments': all_attachments,
            'is_group': True
        }

    def _format_single_subject(self, entity_name: str, invoice_number: str) -> str:
        """
        Format subject line for single invoice.

        Args:
            entity_name: Entity name
            invoice_number: Invoice number

        Returns:
            Formatted subject line
        """
        template = self.config.get('email', {}).get('subject_single', '{entity_name} Invoice {invoice_number}')
        return template.format(entity_name=entity_name, invoice_number=invoice_number)

    def _format_group_subject(self, group_name: str, invoice_numbers: List[str]) -> str:
        """
        Format subject line for grouped invoices.

        Args:
            group_name: Group name
            invoice_numbers: List of invoice numbers

        Returns:
            Formatted subject line
        """
        # Join invoice numbers with " / "
        invoice_numbers_str = ' / '.join(invoice_numbers)
        template = self.config.get('email', {}).get('subject_group', '{group_name} Invoices {invoice_numbers}')
        return template.format(group_name=group_name, invoice_numbers=invoice_numbers_str)

    def _get_email_field(self, row: pd.Series, field: str) -> str:
        """
        Get email field value from row.

        Args:
            row: DataFrame row
            field: Field name ('to', 'cc', 'bcc')

        Returns:
            Email addresses as string
        """
        col = self.csv_columns.get(field)
        if col and col in row.index:
            value = row[col]
            return str(value) if pd.notna(value) and str(value) != '' else ''
        return ''

    def _parse_attachments(self, row: pd.Series) -> List[str]:
        """
        Parse attachment paths from row.

        Args:
            row: DataFrame row

        Returns:
            List of attachment paths
        """
        attachment_col = self.csv_columns.get('attachment')
        if not attachment_col or attachment_col not in row.index:
            return []

        attachment_value = row.get(attachment_col, '')
        if pd.isna(attachment_value) or str(attachment_value).strip() == '':
            return []

        # Split by semicolon or comma
        attachments = [a.strip() for a in str(attachment_value).replace(';', ',').split(',')]
        return [a for a in attachments if a]


def resolve_attachment_path(attachment: str, base_path: str = None) -> Path:
    """
    Resolve attachment path to absolute path.

    Args:
        attachment: Attachment file path
        base_path: Base directory for relative paths

    Returns:
        Resolved Path object
    """
    attachment_path = Path(attachment)

    # If absolute path, use as-is
    if attachment_path.is_absolute():
        return attachment_path

    # If relative path and base_path provided, join them
    if base_path:
        return Path(base_path) / attachment_path

    # Otherwise, use as-is
    return attachment_path


def get_attachment_filename(path: Path) -> str:
    """
    Get filename from attachment path.

    Args:
        path: Path object

    Returns:
        Filename
    """
    return path.name


def format_timestamp() -> str:
    """
    Generate timestamp string for filenames.

    Returns:
        Timestamp string (YYYYMMDD_HHMMSS)
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Replace invalid characters with underscore
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove multiple underscores
    while '__' in filename:
        filename = filename.replace('__', '_')

    return filename.strip('_')
