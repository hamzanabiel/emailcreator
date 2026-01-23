#!/usr/bin/env python3
"""
Email Viewer - View generated .eml files in readable format
"""

import sys
import email
from email import policy
from pathlib import Path
import re

def decode_html(html_content):
    """Decode HTML to show key information"""
    # Extract text content (simplified)
    text = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

def view_email(eml_path):
    """View email file content"""
    with open(eml_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    print("="*70)
    print(f"EMAIL FILE: {Path(eml_path).name}")
    print("="*70)
    print(f"From:    {msg['From']}")
    print(f"To:      {msg['To']}")
    if msg['Cc']:
        print(f"Cc:      {msg['Cc']}")
    if msg['Bcc']:
        print(f"Bcc:     {msg['Bcc']}")
    print(f"Subject: {msg['Subject']}")
    print("-"*70)

    # Get attachments
    attachments = []
    html_body = None

    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition"))

        if "attachment" in content_disposition:
            filename = part.get_filename()
            if filename:
                attachments.append(filename)
        elif part.get_content_type() == "text/html":
            html_body = part.get_content()

    if attachments:
        print(f"Attachments: {', '.join(attachments)}")
        print("-"*70)

    if html_body:
        # Show just the text preview (first 1000 chars)
        text_preview = decode_html(html_body)
        if len(text_preview) > 800:
            print(text_preview[:800] + "\n... (content truncated)")
        else:
            print(text_preview)

    print("="*70)
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python view_email.py <email_file.eml>")
        sys.exit(1)

    eml_file = sys.argv[1]
    if not Path(eml_file).exists():
        print(f"Error: File not found: {eml_file}")
        sys.exit(1)

    view_email(eml_file)
