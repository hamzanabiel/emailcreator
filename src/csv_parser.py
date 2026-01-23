"""
CSV Parser Module
Handles reading and validating CSV files for email generation.
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class CSVParser:
    """Parses and validates CSV files for email generation."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize CSV parser with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.csv_columns = config.get('csv_columns', {})
        self.validation = config.get('validation', {})

    def parse_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Parse CSV file and return DataFrame.

        Args:
            csv_path: Path to CSV file

        Returns:
            Parsed DataFrame

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV has invalid format
        """
        csv_file = Path(csv_path)

        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        logger.info(f"Reading CSV file: {csv_path}")

        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")

        # Validate required columns
        self._validate_columns(df)

        # Clean and normalize data
        df = self._clean_data(df)

        logger.info(f"Successfully parsed {len(df)} rows from CSV")

        return df

    def _validate_columns(self, df: pd.DataFrame) -> None:
        """
        Validate that required columns exist in DataFrame.

        Args:
            df: DataFrame to validate

        Raises:
            ValueError: If required columns are missing
        """
        required_columns = [
            self.csv_columns.get('to'),
            self.csv_columns.get('entity_name'),
            self.csv_columns.get('invoice_number'),
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}\n"
                f"Available columns: {', '.join(df.columns)}"
            )

        logger.debug("All required columns present")

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize DataFrame data.

        Args:
            df: DataFrame to clean

        Returns:
            Cleaned DataFrame
        """
        # Strip whitespace from string columns
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()

        # Replace 'nan' strings with empty strings
        df = df.replace('nan', '')
        df = df.fillna('')

        return df

    def validate_emails(self, df: pd.DataFrame) -> List[str]:
        """
        Validate email addresses in DataFrame.

        Args:
            df: DataFrame to validate

        Returns:
            List of validation errors
        """
        if not self.validation.get('validate_emails', True):
            return []

        errors = []
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        for idx, row in df.iterrows():
            # Validate To addresses
            to_col = self.csv_columns.get('to')
            if to_col and row.get(to_col):
                to_emails = self._split_emails(row[to_col])
                for email in to_emails:
                    if email and not re.match(email_pattern, email):
                        errors.append(f"Row {idx + 2}: Invalid To email: {email}")

            # Validate CC addresses
            cc_col = self.csv_columns.get('cc')
            if cc_col and row.get(cc_col):
                cc_emails = self._split_emails(row[cc_col])
                for email in cc_emails:
                    if email and not re.match(email_pattern, email):
                        errors.append(f"Row {idx + 2}: Invalid CC email: {email}")

            # Validate BCC addresses
            bcc_col = self.csv_columns.get('bcc')
            if bcc_col and row.get(bcc_col):
                bcc_emails = self._split_emails(row[bcc_col])
                for email in bcc_emails:
                    if email and not re.match(email_pattern, email):
                        errors.append(f"Row {idx + 2}: Invalid BCC email: {email}")

        return errors

    def validate_attachments(self, df: pd.DataFrame, base_path: str = None) -> List[str]:
        """
        Validate that attachment files exist.

        Args:
            df: DataFrame to validate
            base_path: Base directory for attachment paths

        Returns:
            List of validation errors
        """
        if not self.validation.get('check_attachments', True):
            return []

        errors = []
        attachment_col = self.csv_columns.get('attachment')

        if not attachment_col or attachment_col not in df.columns:
            return []

        for idx, row in df.iterrows():
            attachment_path = row.get(attachment_col, '')
            if attachment_path and attachment_path != '':
                # Resolve path (absolute or relative to base_path)
                if base_path:
                    full_path = Path(base_path) / attachment_path
                else:
                    full_path = Path(attachment_path)

                if not full_path.exists():
                    errors.append(
                        f"Row {idx + 2}: Attachment file not found: {attachment_path}"
                    )

        return errors

    @staticmethod
    def _split_emails(email_string: str) -> List[str]:
        """
        Split multiple email addresses from a string.

        Args:
            email_string: String containing one or more email addresses

        Returns:
            List of email addresses
        """
        if not email_string or email_string == '':
            return []

        # Split by semicolon or comma
        emails = re.split(r'[;,]', email_string)
        return [email.strip() for email in emails if email.strip()]
