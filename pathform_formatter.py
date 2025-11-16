#!/usr/bin/env python3
"""
PathForm Formatter

Formats PathForm files with consistent styling.
"""

import sys
import argparse
from pathform import parse_pathform, from_json


def format_pathform(text, indent="  ", sort=True, group=True):
    """
    Format PathForm text with consistent styling.
    
    Args:
        text: PathForm text to format
        indent: Indentation string (default: 2 spaces)
        sort: Whether to sort paths (default: True)
        group: Whether to group by prefix (default: True)
    
    Returns:
        Formatted PathForm text
    """
    # Parse and regenerate
    obj = parse_pathform(text)
    formatted = from_json(obj, flat=not group)
    
    # Apply custom indentation if needed
    if indent != "  ":
        lines = formatted.split('\n')
        # Simple indentation based on depth
        formatted_lines = []
        for line in lines:
            if not line.strip() or line.strip().startswith('#'):
                formatted_lines.append(line)
            else:
                # Count depth by dots and brackets
                depth = line.count('.') + line.count('[')
                formatted_lines.append(indent * depth + line.lstrip())
        formatted = '\n'.join(formatted_lines)
    
    return formatted


def main():
    parser = argparse.ArgumentParser(
        description='Format PathForm files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'files',
        nargs='*',
        type=argparse.FileType('r'),
        default=[sys.stdin] if sys.stdin.isatty() else [sys.stdin],
        help='PathForm files to format (default: stdin)'
    )
    parser.add_argument(
        '-i', '--in-place',
        action='store_true',
        help='Edit files in place'
    )
    parser.add_argument(
        '--indent',
        type=str,
        default='  ',
        help='Indentation string (default: 2 spaces)'
    )
    parser.add_argument(
        '--no-sort',
        action='store_true',
        help='Do not sort paths'
    )
    parser.add_argument(
        '--no-group',
        action='store_true',
        help='Do not group by prefix'
    )

    args = parser.parse_args()

    for file in args.files:
        filename = file.name if hasattr(file, 'name') else '<stdin>'
        text = file.read()
        
        try:
            formatted = format_pathform(
                text,
                indent=args.indent,
                sort=not args.no_sort,
                group=not args.no_group
            )
            
            if args.in_place and filename != '<stdin>':
                with open(filename, 'w') as f:
                    f.write(formatted)
                    if not formatted.endswith('\n'):
                        f.write('\n')
            else:
                sys.stdout.write(formatted)
                if not formatted.endswith('\n'):
                    sys.stdout.write('\n')
        except Exception as e:
            print(f"Error formatting {filename}: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()

