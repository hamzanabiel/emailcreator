#!/usr/bin/env python3
"""
CSV Email Tool - Main Entry Point
Generates Outlook .msg or .eml files from CSV data with attachments.
"""

import argparse
import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, Any
from colorama import init, Fore, Style

from src.csv_parser import CSVParser
from src.utils import EmailGrouper
from src.email_generator import EmailGenerator

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def setup_logging(config: Dict[str, Any]) -> None:
    """
    Setup logging configuration.

    Args:
        config: Configuration dictionary
    """
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file', 'email_tool.log')
    console_output = log_config.get('console', True)

    # Configure logging
    handlers = []

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        handlers.append(file_handler)

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(levelname)s - %(message)s')
        )
        handlers.append(console_handler)

    logging.basicConfig(
        level=log_level,
        handlers=handlers
    )


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)

    if not config_file.exists():
        print(f"{Fore.RED}Error: Configuration file not found: {config_path}{Style.RESET_ALL}")
        sys.exit(1)

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"{Fore.RED}Error loading configuration: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


def print_banner():
    """Print application banner."""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════╗
║         CSV Email Tool - Invoice Email Generator     ║
║                    Version 1.0.0                      ║
╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_summary(email_groups: list, generated_files: list, config: Dict[str, Any]):
    """
    Print summary of generated emails.

    Args:
        email_groups: List of email groups
        generated_files: List of generated file paths
        config: Configuration dictionary
    """
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Generation Complete!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")

    print(f"📧 Total emails generated: {Fore.CYAN}{len(generated_files)}{Style.RESET_ALL}")

    # Count single vs group emails
    single_count = sum(1 for eg in email_groups if not eg.get('is_group'))
    group_count = sum(1 for eg in email_groups if eg.get('is_group'))

    print(f"   - Single invoice emails: {single_count}")
    print(f"   - Grouped invoice emails: {group_count}")

    # Show output directory
    output_dir = Path(config.get('paths', {}).get('output', 'output'))
    print(f"\n📁 Output directory: {Fore.CYAN}{output_dir.absolute()}{Style.RESET_ALL}")

    # List generated files
    if generated_files and len(generated_files) <= 10:
        print(f"\n📄 Generated files:")
        for file in generated_files:
            print(f"   - {file.name}")
    elif len(generated_files) > 10:
        print(f"\n📄 Generated files: (showing first 10)")
        for file in generated_files[:10]:
            print(f"   - {file.name}")
        print(f"   ... and {len(generated_files) - 10} more")


def validate_csv_data(parser: CSVParser, df, config: Dict[str, Any]) -> bool:
    """
    Validate CSV data and print errors.

    Args:
        parser: CSVParser instance
        df: DataFrame to validate
        config: Configuration dictionary

    Returns:
        True if validation passed, False otherwise
    """
    print(f"\n{Fore.YELLOW}Validating CSV data...{Style.RESET_ALL}")

    # Validate emails
    email_errors = parser.validate_emails(df)
    if email_errors:
        print(f"\n{Fore.RED}Email validation errors:{Style.RESET_ALL}")
        for error in email_errors[:10]:  # Show first 10 errors
            print(f"  ❌ {error}")
        if len(email_errors) > 10:
            print(f"  ... and {len(email_errors) - 10} more errors")

    # Validate attachments
    attachment_base = config.get('paths', {}).get('attachment_base')
    attachment_errors = parser.validate_attachments(df, attachment_base)
    if attachment_errors:
        print(f"\n{Fore.RED}Attachment validation errors:{Style.RESET_ALL}")
        for error in attachment_errors[:10]:  # Show first 10 errors
            print(f"  ❌ {error}")
        if len(attachment_errors) > 10:
            print(f"  ... and {len(attachment_errors) - 10} more errors")

    total_errors = len(email_errors) + len(attachment_errors)

    if total_errors > 0:
        print(f"\n{Fore.RED}Validation failed with {total_errors} error(s).{Style.RESET_ALL}")
        return False
    else:
        print(f"{Fore.GREEN}✓ Validation passed!{Style.RESET_ALL}")
        return True


def main():
    """Main application entry point."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Generate Outlook .msg or .eml files from CSV data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main data.csv
  python -m src.main data.csv --config custom_config.yaml
  python -m src.main data.csv --skip-validation
        """
    )

    parser.add_argument(
        'csv_file',
        help='Path to input CSV file'
    )

    parser.add_argument(
        '-c', '--config',
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )

    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip validation checks'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Load configuration
    print(f"Loading configuration from: {args.config}")
    config = load_config(args.config)

    # Override log level if verbose
    if args.verbose:
        config['logging']['level'] = 'DEBUG'

    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)

    logger.info("="*60)
    logger.info("CSV Email Tool Started")
    logger.info("="*60)

    try:
        # Initialize components
        csv_parser = CSVParser(config)
        email_grouper = EmailGrouper(config)
        email_generator = EmailGenerator(config)

        # Parse CSV
        print(f"\n📂 Reading CSV file: {Fore.CYAN}{args.csv_file}{Style.RESET_ALL}")
        df = csv_parser.parse_csv(args.csv_file)
        print(f"✓ Loaded {len(df)} rows")

        # Validate CSV data
        if not args.skip_validation:
            if not validate_csv_data(csv_parser, df, config):
                response = input(f"\n{Fore.YELLOW}Continue anyway? (y/N): {Style.RESET_ALL}")
                if response.lower() != 'y':
                    print("Aborted.")
                    sys.exit(1)
        else:
            print(f"{Fore.YELLOW}⚠ Skipping validation{Style.RESET_ALL}")

        # Group emails
        print(f"\n🔄 Grouping emails...")
        email_groups = email_grouper.group_emails(df)
        print(f"✓ Created {len(email_groups)} email group(s)")

        # Generate emails
        print(f"\n⚙️  Generating email files...")
        generated_files = email_generator.generate_batch(email_groups)

        # Print summary
        print_summary(email_groups, generated_files, config)

        logger.info("CSV Email Tool Completed Successfully")
        return 0

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠ Operation cancelled by user{Style.RESET_ALL}")
        logger.warning("Operation cancelled by user")
        return 1

    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
