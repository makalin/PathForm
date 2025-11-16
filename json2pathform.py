#!/usr/bin/env python3
"""
JSON to PathForm CLI Tool

Converts JSON files to PathForm format.
"""

import sys
import json
import argparse
from pathform import from_json


def main():
    parser = argparse.ArgumentParser(
        description='Convert JSON to PathForm text',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  json2pathform input.json > output.pf
  json2pathform input.json -o output.pf
  json2pathform input.json --flat
  cat input.json | json2pathform
        """
    )
    parser.add_argument(
        'input',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='Input JSON file (default: stdin)'
    )
    parser.add_argument(
        '-o', '--output',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='Output PathForm file (default: stdout)'
    )
    parser.add_argument(
        '--flat',
        action='store_true',
        help='Emit all paths fully qualified (not grouped)'
    )

    args = parser.parse_args()

    try:
        # Read and parse JSON
        json_text = args.input.read()
        json_obj = json.loads(json_text)
        
        # Convert to PathForm
        pathform_output = from_json(json_obj, flat=args.flat)
        
        # Write output
        args.output.write(pathform_output)
        if args.output != sys.stdout:
            args.output.write('\n')
        
        return 0
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

