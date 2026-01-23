#!/usr/bin/env python3
"""
Automated Testing Script for CSV Email Tool
Runs comprehensive tests and generates a report
"""

import subprocess
import sys
from pathlib import Path
import email
from email import policy
from colorama import init, Fore, Style

init(autoreset=True)

def print_header(text):
    """Print section header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Style.RESET_ALL}\n")

def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_info(text):
    """Print info message"""
    print(f"{Fore.YELLOW}ℹ {text}{Style.RESET_ALL}")

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{Fore.CYAN}Running: {description}{Style.RESET_ALL}")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print_success(f"{description} completed successfully")
        return True
    else:
        print_error(f"{description} failed")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print_success(f"{description}: {filepath}")
        return True
    else:
        print_error(f"{description} not found: {filepath}")
        return False

def analyze_email(eml_path):
    """Analyze an email file and return details"""
    try:
        with open(eml_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=policy.default)

        attachments = []
        for part in msg.walk():
            filename = part.get_filename()
            if filename:
                attachments.append(filename)

        return {
            'from': msg['From'],
            'to': msg['To'],
            'cc': msg.get('Cc', ''),
            'bcc': msg.get('Bcc', ''),
            'subject': msg['Subject'],
            'attachments': attachments
        }
    except Exception as e:
        print_error(f"Error analyzing {eml_path}: {str(e)}")
        return None

def main():
    """Run all tests"""
    print_header("CSV Email Tool - Automated Testing")

    passed = 0
    failed = 0

    # Test 1: Check dependencies
    print_header("Test 1: Dependencies Check")
    dependencies = ['pandas', 'yaml', 'jinja2', 'colorama']
    for dep in dependencies:
        try:
            __import__(dep if dep != 'yaml' else 'yaml')
            print_success(f"Module '{dep}' installed")
            passed += 1
        except ImportError:
            print_error(f"Module '{dep}' missing")
            failed += 1

    # Test 2: Check file structure
    print_header("Test 2: Project Structure Check")
    required_files = [
        'config/config.yaml',
        'config/template.html',
        'src/main.py',
        'src/csv_parser.py',
        'src/utils.py',
        'src/msg_creator.py',
        'src/email_generator.py',
        'tests/sample_data.csv'
    ]

    for filepath in required_files:
        if check_file_exists(filepath, filepath):
            passed += 1
        else:
            failed += 1

    # Test 3: Run tool with sample data
    print_header("Test 3: Generate Emails from Sample Data")

    # Clean output directory
    output_dir = Path('output')
    if output_dir.exists():
        for file in output_dir.glob('*.eml'):
            file.unlink()
        print_info("Cleaned output directory")

    # Run the tool
    cmd = [sys.executable, '-m', 'src.main', 'tests/sample_data.csv', '--skip-validation']
    if run_command(cmd, "Generate emails"):
        passed += 1
    else:
        failed += 1
        print_error("Email generation failed - aborting further tests")
        print_summary(passed, failed)
        return 1

    # Test 4: Verify output files
    print_header("Test 4: Verify Generated Email Files")

    output_files = list(Path('output').glob('*.eml'))
    print_info(f"Found {len(output_files)} email files")

    if len(output_files) >= 6:  # Should have at least 6 emails
        print_success(f"Generated {len(output_files)} emails (expected 6-8)")
        passed += 1
    else:
        print_error(f"Only {len(output_files)} emails generated (expected 6-8)")
        failed += 1

    # Test 5: Analyze email content
    print_header("Test 5: Email Content Analysis")

    # Check for at least one email
    if output_files:
        sample_email = output_files[0]
        print_info(f"Analyzing: {sample_email.name}")

        details = analyze_email(sample_email)
        if details:
            print(f"\n{Fore.CYAN}Email Details:{Style.RESET_ALL}")
            print(f"  From:    {details['from']}")
            print(f"  To:      {details['to']}")
            print(f"  Subject: {details['subject']}")
            if details['attachments']:
                print(f"  Attachments: {', '.join(details['attachments'])}")

            # Verify essential fields
            checks = [
                (details['from'], "From field populated"),
                (details['to'], "To field populated"),
                (details['subject'], "Subject field populated")
            ]

            for value, description in checks:
                if value:
                    print_success(description)
                    passed += 1
                else:
                    print_error(description)
                    failed += 1
        else:
            print_error("Failed to analyze email content")
            failed += 1
    else:
        print_error("No emails to analyze")
        failed += 1

    # Test 6: Check for grouped emails
    print_header("Test 6: Email Grouping Verification")

    # Look for BigCorp group email
    group_emails = [f for f in output_files if 'Group' in f.name or 'Multiple' in f.name]

    if group_emails:
        print_success(f"Found {len(group_emails)} grouped email(s)")
        passed += 1

        # Analyze first group email
        group_email = group_emails[0]
        print_info(f"Analyzing grouped email: {group_email.name}")
        details = analyze_email(group_email)
        if details:
            print(f"  Subject: {details['subject']}")
            if 'Invoices' in details['subject']:
                print_success("Group subject contains 'Invoices'")
                passed += 1
            else:
                print_error("Group subject doesn't contain 'Invoices'")
                failed += 1
    else:
        print_error("No grouped emails found")
        failed += 1

    # Test 7: Attachment verification
    print_header("Test 7: Attachment Verification")

    emails_with_attachments = 0
    for eml_file in output_files[:3]:  # Check first 3 emails
        details = analyze_email(eml_file)
        if details and details['attachments']:
            emails_with_attachments += 1
            print_success(f"{eml_file.name}: {len(details['attachments'])} attachment(s)")

    if emails_with_attachments > 0:
        print_success(f"{emails_with_attachments} emails have attachments")
        passed += 1
    else:
        print_error("No emails have attachments")
        failed += 1

    # Print summary
    print_summary(passed, failed)

    return 0 if failed == 0 else 1

def print_summary(passed, failed):
    """Print test summary"""
    total = passed + failed
    percentage = (passed / total * 100) if total > 0 else 0

    print_header("Test Summary")
    print(f"Total Tests:  {total}")
    print(f"{Fore.GREEN}Passed:       {passed}{Style.RESET_ALL}")
    print(f"{Fore.RED}Failed:       {failed}{Style.RESET_ALL}")
    print(f"Success Rate: {percentage:.1f}%")

    if failed == 0:
        print(f"\n{Fore.GREEN}🎉 All tests passed! The tool is working correctly.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠ Some tests failed. Please review the output above.{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}Next Steps:{Style.RESET_ALL}")
    print("1. Review generated emails in the output/ directory")
    print("2. Open emails in your email client to verify formatting")
    print("3. Check TESTING_GUIDE.md for detailed testing instructions")
    print("4. Customize config/config.yaml with your company details")
    print("5. Edit config/template.html to match your branding")

if __name__ == '__main__':
    sys.exit(main())
