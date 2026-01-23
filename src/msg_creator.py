"""
MSG/EML Creator Module
Handles cross-platform creation of Outlook .msg and .eml files.
"""

import platform
import logging
from pathlib import Path
from typing import List, Dict, Any
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)


class EmailFileCreator:
    """Creates email files in .msg (Windows) or .eml (cross-platform) format."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email file creator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.email_format = config.get('email', {}).get('format', 'auto')
        self.platform = platform.system()

        # Determine which format to use
        if self.email_format == 'auto':
            self.use_msg = self.platform == 'Windows'
        elif self.email_format == 'msg':
            self.use_msg = True
        else:
            self.use_msg = False

        logger.info(f"Email format: {'MSG' if self.use_msg else 'EML'} (Platform: {self.platform})")

    def create_email_file(
        self,
        output_path: Path,
        to: str,
        subject: str,
        html_body: str,
        cc: str = '',
        bcc: str = '',
        from_email: str = '',
        attachments: List[Path] = None
    ) -> Path:
        """
        Create email file (.msg or .eml).

        Args:
            output_path: Path for output file (without extension)
            to: To email addresses
            subject: Email subject
            html_body: HTML body content
            cc: CC email addresses
            bcc: BCC email addresses
            from_email: From email address
            attachments: List of attachment file paths

        Returns:
            Path to created email file
        """
        if self.use_msg and self.platform == 'Windows':
            return self._create_msg_file(
                output_path, to, subject, html_body, cc, bcc, from_email, attachments
            )
        else:
            return self._create_eml_file(
                output_path, to, subject, html_body, cc, bcc, from_email, attachments
            )

    def _create_eml_file(
        self,
        output_path: Path,
        to: str,
        subject: str,
        html_body: str,
        cc: str,
        bcc: str,
        from_email: str,
        attachments: List[Path]
    ) -> Path:
        """
        Create .eml file (cross-platform).

        Args:
            output_path: Path for output file (without extension)
            to: To email addresses
            subject: Email subject
            html_body: HTML body content
            cc: CC email addresses
            bcc: BCC email addresses
            from_email: From email address
            attachments: List of attachment file paths

        Returns:
            Path to created .eml file
        """
        # Create multipart message
        msg = MIMEMultipart()

        # Set headers
        msg['Subject'] = subject
        msg['To'] = to
        if cc:
            msg['Cc'] = cc
        if bcc:
            msg['Bcc'] = bcc
        if from_email:
            msg['From'] = from_email
        else:
            msg['From'] = self.config.get('email', {}).get('from', 'noreply@example.com')

        # Add HTML body
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # Add attachments
        if attachments:
            for attachment_path in attachments:
                if attachment_path.exists():
                    self._attach_file_to_mime(msg, attachment_path)
                else:
                    logger.warning(f"Attachment not found: {attachment_path}")

        # Write to file
        eml_path = output_path.with_suffix('.eml')
        with open(eml_path, 'w', encoding='utf-8') as f:
            f.write(msg.as_string())

        logger.debug(f"Created EML file: {eml_path}")
        return eml_path

    def _create_msg_file(
        self,
        output_path: Path,
        to: str,
        subject: str,
        html_body: str,
        cc: str,
        bcc: str,
        from_email: str,
        attachments: List[Path]
    ) -> Path:
        """
        Create .msg file using Outlook COM (Windows only).

        Args:
            output_path: Path for output file (without extension)
            to: To email addresses
            subject: Email subject
            html_body: HTML body content
            cc: CC email addresses
            bcc: BCC email addresses
            from_email: From email address
            attachments: List of attachment file paths

        Returns:
            Path to created .msg file
        """
        try:
            import win32com.client
        except ImportError:
            logger.warning("pywin32 not available. Falling back to EML format.")
            return self._create_eml_file(
                output_path, to, subject, html_body, cc, bcc, from_email, attachments
            )

        try:
            # Create Outlook application object
            outlook = win32com.client.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)  # 0 = MailItem

            # Set email properties
            mail.To = to
            if cc:
                mail.CC = cc
            if bcc:
                mail.BCC = bcc
            mail.Subject = subject
            mail.HTMLBody = html_body

            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    if attachment_path.exists():
                        mail.Attachments.Add(str(attachment_path.absolute()))
                    else:
                        logger.warning(f"Attachment not found: {attachment_path}")

            # Save as .msg file
            msg_path = output_path.with_suffix('.msg')
            mail.SaveAs(str(msg_path.absolute()), 3)  # 3 = olMSG format

            logger.debug(f"Created MSG file: {msg_path}")
            return msg_path

        except Exception as e:
            logger.error(f"Error creating MSG file: {str(e)}")
            logger.warning("Falling back to EML format.")
            return self._create_eml_file(
                output_path, to, subject, html_body, cc, bcc, from_email, attachments
            )

    @staticmethod
    def _attach_file_to_mime(msg: MIMEMultipart, file_path: Path) -> None:
        """
        Attach file to MIME message.

        Args:
            msg: MIME message object
            file_path: Path to file to attach
        """
        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={file_path.name}'
        )
        msg.attach(part)

    def get_file_extension(self) -> str:
        """
        Get the file extension that will be used.

        Returns:
            File extension ('.msg' or '.eml')
        """
        return '.msg' if self.use_msg else '.eml'
