#!/usr/bin/env python3
"""
Attachment Diagnostic Tool
Checks if attachment files exist and are accessible
"""

import sys
import pandas as pd
from pathlib import Path
import yaml
from colorama import init, Fore, Style

init(autoreset=True)

def load_config(config_path='config/config.yaml'):
    """Load configuration"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def check_attachments(csv_path, config):
    """Check all attachments in CSV"""

    # Read CSV
    df = pd.read_csv(csv_path)

    # Get configuration
    attachment_col = config.get('csv_columns', {}).get('attachment', 'Attachment Path')
    attachment_base = config.get('paths', {}).get('attachment_base', '')

    print(f"\n{Fore.CYAN}Attachment Diagnostic Report{Style.RESET_ALL}")
    print("="*70)
    print(f"CSV File: {csv_path}")
    print(f"Attachment Base: {attachment_base or '(not set)'}")
    print(f"Attachment Column: {attachment_col}")
    print("="*70 + "\n")

    if attachment_col not in df.columns:
        print(f"{Fore.RED}ERROR: Column '{attachment_col}' not found in CSV{Style.RESET_ALL}")
        print(f"Available columns: {', '.join(df.columns)}")
        return

    found_count = 0
    missing_count = 0
    total_count = 0

    for idx, row in df.iterrows():
        attachment_value = row.get(attachment_col, '')

        if pd.isna(attachment_value) or str(attachment_value).strip() == '':
            continue

        # Split multiple attachments
        attachments = [a.strip() for a in str(attachment_value).replace(';', ',').split(',')]

        for attachment in attachments:
            if not attachment:
                continue

            total_count += 1

            # Resolve path
            attachment_path = Path(attachment)

            # If absolute path, use as-is
            if attachment_path.is_absolute():
                resolved_path = attachment_path
            # If relative and base_path provided, join them
            elif attachment_base:
                resolved_path = Path(attachment_base) / attachment_path
            else:
                resolved_path = attachment_path

            # Check if exists
            if resolved_path.exists():
                print(f"{Fore.GREEN}✓{Style.RESET_ALL} Row {idx + 2}: {attachment}")
                print(f"  → Resolved to: {resolved_path}")
                print(f"  → File size: {resolved_path.stat().st_size:,} bytes")
                found_count += 1
            else:
                print(f"{Fore.RED}✗{Style.RESET_ALL} Row {idx + 2}: {attachment}")
                print(f"  → Resolved to: {resolved_path}")
                print(f"  → {Fore.RED}FILE NOT FOUND{Style.RESET_ALL}")
                missing_count += 1

                # Suggest fixes
                if attachment_path.is_absolute():
                    print(f"  → Fix: Verify the absolute path is correct")
                else:
                    print(f"  → Fix: Check 'attachment_base' in config.yaml")
                    print(f"  →      Current base: '{attachment_base}'")
                    if not attachment_base:
                        print(f"  →      Or use absolute path in CSV")

            print()

    # Summary
    print("="*70)
    print(f"{Fore.CYAN}Summary{Style.RESET_ALL}")
    print("="*70)
    print(f"Total attachments: {total_count}")
    print(f"{Fore.GREEN}Found: {found_count}{Style.RESET_ALL}")
    print(f"{Fore.RED}Missing: {missing_count}{Style.RESET_ALL}")

    if missing_count > 0:
        print(f"\n{Fore.YELLOW}⚠ Action Required:{Style.RESET_ALL}")
        print("1. Verify attachment files exist at the specified paths")
        print("2. Check 'attachment_base' setting in config/config.yaml")
        print("3. Use absolute paths in CSV if files are in different locations")
        print("4. Or move files to the attachment_base directory")
    else:
        print(f"\n{Fore.GREEN}✓ All attachments found! Ready to generate emails.{Style.RESET_ALL}")

    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_attachments.py <csv_file>")
        print("Example: python check_attachments.py data.csv")
        sys.exit(1)

    csv_file = sys.argv[1]

    if not Path(csv_file).exists():
        print(f"Error: CSV file not found: {csv_file}")
        sys.exit(1)

    config = load_config()
    check_attachments(csv_file, config)
