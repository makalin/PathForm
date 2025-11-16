#!/usr/bin/env python3
"""
PathForm to JSON CLI Tool

Converts PathForm text files to JSON format.
"""

import sys
import json
import argparse
from pathform import parse_pathform, to_json


def main():
    parser = argparse.ArgumentParser(
        description='Convert PathForm text to JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pathform2json input.pf > output.json
  pathform2json input.pf -o output.json
  pathform2json input.pf --indent 4
  cat input.pf | pathform2json
        """
    )
    parser.add_argument(
        'input',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='Input PathForm file (default: stdin)'
    )
    parser.add_argument(
        '-o', '--output',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='Output JSON file (default: stdout)'
    )
    parser.add_argument(
        '--indent',
        type=int,
        default=2,
        help='JSON indentation (default: 2, use 0 for compact)'
    )
    parser.add_argument(
        '--compact',
        action='store_true',
        help='Output compact JSON (no indentation)'
    )

    args = parser.parse_args()

    try:
        # Read input
        text = args.input.read()
        
        # Parse and convert
        indent = 0 if args.compact else args.indent
        json_output = to_json(text, indent=indent)
        
        # Write output
        args.output.write(json_output)
        if args.output != sys.stdout:
            args.output.write('\n')
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

