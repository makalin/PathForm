#!/usr/bin/env python3
"""
PathForm Diff Tool

Shows differences between two PathForm files.
"""

import sys
import argparse
from pathform import parse_pathform
import json


def diff_pathform(file1_text, file2_text, file1_name="file1", file2_name="file2"):
    """
    Compare two PathForm files and show differences.
    """
    try:
        obj1 = parse_pathform(file1_text)
        obj2 = parse_pathform(file2_text)
    except Exception as e:
        print(f"Error parsing: {e}", file=sys.stderr)
        return 1
    
    # Convert to JSON for comparison
    json1 = json.dumps(obj1, sort_keys=True, indent=2)
    json2 = json.dumps(obj2, sort_keys=True, indent=2)
    
    if json1 == json2:
        print("Files are identical")
        return 0
    
    # Simple diff output
    print(f"=== Differences between {file1_name} and {file2_name} ===\n")
    
    # Find keys only in file1
    keys1 = set(_get_all_keys(obj1))
    keys2 = set(_get_all_keys(obj2))
    
    only_in_1 = keys1 - keys2
    only_in_2 = keys2 - keys1
    
    if only_in_1:
        print(f"Keys only in {file1_name}:")
        for key in sorted(only_in_1):
            print(f"  + {key}")
        print()
    
    if only_in_2:
        print(f"Keys only in {file2_name}:")
        for key in sorted(only_in_2):
            print(f"  - {key}")
        print()
    
    # Find value differences
    common_keys = keys1 & keys2
    differences = []
    for key in sorted(common_keys):
        val1 = _get_value_by_path(obj1, key)
        val2 = _get_value_by_path(obj2, key)
        if val1 != val2:
            differences.append((key, val1, val2))
    
    if differences:
        print("Value differences:")
        for key, val1, val2 in differences:
            print(f"  {key}:")
            print(f"    {file1_name}: {val1}")
            print(f"    {file2_name}: {val2}")
        print()
    
    return 1


def _get_all_keys(obj, prefix=""):
    """Get all keys from a nested object."""
    keys = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            keys.append(new_prefix)
            keys.extend(_get_all_keys(value, new_prefix))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            new_prefix = f"{prefix}[{i}]"
            keys.append(new_prefix)
            keys.extend(_get_all_keys(value, new_prefix))
    return keys


def _get_value_by_path(obj, path):
    """Get value by dot/bracket path."""
    parts = _parse_path(path)
    current = obj
    for part in parts:
        if isinstance(part, int):
            current = current[part]
        else:
            current = current[part]
    return current


def _parse_path(path_str):
    """Parse a path string into parts."""
    parts = []
    current = ""
    i = 0
    while i < len(path_str):
        if path_str[i] == '.':
            if current:
                parts.append(current)
                current = ""
        elif path_str[i] == '[':
            if current:
                parts.append(current)
                current = ""
            j = i + 1
            while j < len(path_str) and path_str[j] != ']':
                j += 1
            index = int(path_str[i+1:j])
            parts.append(index)
            i = j
        else:
            current += path_str[i]
        i += 1
    if current:
        parts.append(current)
    return parts


def main():
    parser = argparse.ArgumentParser(
        description='Compare two PathForm files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'file1',
        type=argparse.FileType('r'),
        help='First PathForm file'
    )
    parser.add_argument(
        'file2',
        type=argparse.FileType('r'),
        help='Second PathForm file'
    )

    args = parser.parse_args()

    file1_text = args.file1.read()
    file2_text = args.file2.read()
    
    file1_name = args.file1.name if hasattr(args.file1, 'name') else 'file1'
    file2_name = args.file2.name if hasattr(args.file2, 'name') else 'file2'
    
    sys.exit(diff_pathform(file1_text, file2_text, file1_name, file2_name))


if __name__ == '__main__':
    main()

