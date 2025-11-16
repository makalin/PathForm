#!/usr/bin/env python3
"""
PathForm Validator

Validates PathForm syntax and reports errors.
"""

import sys
import argparse
from pathform import parse_pathform


def validate_pathform(text, filename="<stdin>"):
    """
    Validate PathForm text and return (is_valid, errors)
    """
    errors = []
    
    try:
        parse_pathform(text)
        return True, []
    except Exception as e:
        errors.append(f"{filename}: {str(e)}")
        return False, errors


def main():
    parser = argparse.ArgumentParser(
        description='Validate PathForm syntax',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'files',
        nargs='*',
        type=argparse.FileType('r'),
        default=[sys.stdin] if sys.stdin.isatty() else [sys.stdin],
        help='PathForm files to validate (default: stdin)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Exit with error code on any validation failure'
    )

    args = parser.parse_args()

    all_valid = True
    total_errors = 0

    for file in args.files:
        filename = file.name if hasattr(file, 'name') else '<stdin>'
        text = file.read()
        
        is_valid, errors = validate_pathform(text, filename)
        
        if not is_valid:
            all_valid = False
            total_errors += len(errors)
            for error in errors:
                print(error, file=sys.stderr)
        else:
            print(f"{filename}: OK")

    if args.strict and not all_valid:
        sys.exit(1)
    
    sys.exit(0 if all_valid else 1)


if __name__ == '__main__':
    main()

