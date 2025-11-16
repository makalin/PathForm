"""
PathForm Parser for Python

Parses PathForm text format into JSON-compatible Python objects.
"""

import json
import re
from typing import Any, Dict, Union


def parse_pathform(text: str) -> Dict[str, Any]:
    """
    Parse PathForm text into a Python dictionary (JSON-compatible).
    
    Args:
        text: PathForm text string
        
    Returns:
        Dictionary representing the parsed PathForm structure
    """
    result = {}
    
    for line_num, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        
        # Skip blank lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Parse statement: path = value
        match = re.match(r'^([^=]+?)\s*=\s*(.+)$', line)
        if not match:
            raise ValueError(f"Line {line_num}: Invalid syntax: {line}")
        
        path_str = match.group(1).strip()
        value_str = match.group(2).strip()
        
        # Parse value
        value = parse_value(value_str)
        
        # Set path in result
        set_path(result, path_str, value)
    
    return result


def parse_value(value_str: str) -> Any:
    """
    Parse a value string into a Python value.
    
    Handles: numbers, booleans, null, strings (bare or quoted)
    """
    value_str = value_str.strip()
    
    # null
    if value_str == 'null':
        return None
    
    # booleans
    if value_str == 'true':
        return True
    if value_str == 'false':
        return False
    
    # quoted string
    if value_str.startswith('"') and value_str.endswith('"'):
        # Use JSON decoder for proper escaping
        return json.loads(value_str)
    
    # number (try to parse as number)
    try:
        # Try integer first
        if '.' not in value_str and 'e' not in value_str.lower():
            return int(value_str)
        # Then float
        return float(value_str)
    except ValueError:
        pass
    
    # bare string (no quotes, no spaces, not a keyword)
    return value_str


def set_path(obj: Dict[str, Any], path_str: str, value: Any) -> None:
    """
    Set a value at a given path in the object.
    
    Path format: segment(.segment|\[index\])*
    Examples: user.name, items[0], config.models[1].name
    """
    # Parse path into segments and indices
    parts = []
    current = ''
    i = 0
    
    while i < len(path_str):
        if path_str[i] == '.':
            if current:
                parts.append(('key', current))
                current = ''
        elif path_str[i] == '[':
            if current:
                parts.append(('key', current))
                current = ''
            # Find closing bracket
            j = i + 1
            while j < len(path_str) and path_str[j] != ']':
                j += 1
            if j >= len(path_str):
                raise ValueError(f"Unclosed bracket in path: {path_str}")
            index_str = path_str[i+1:j]
            try:
                index = int(index_str)
                if index < 0:
                    raise ValueError(f"Negative array index in path: {path_str}")
                parts.append(('index', index))
            except ValueError:
                raise ValueError(f"Invalid array index in path: {path_str}")
            i = j
        else:
            current += path_str[i]
        i += 1
    
    if current:
        parts.append(('key', current))
    
    if not parts:
        raise ValueError(f"Empty path: {path_str}")
    
    # Navigate/create structure
    current_obj = obj
    for i, (part_type, part_value) in enumerate(parts[:-1]):
        next_part = parts[i + 1]
        
        if part_type == 'key':
            if part_value not in current_obj:
                # Determine next type based on next part
                if next_part[0] == 'index':
                    current_obj[part_value] = []
                else:
                    current_obj[part_value] = {}
            current_obj = current_obj[part_value]
        elif part_type == 'index':
            # Ensure it's a list
            if not isinstance(current_obj, list):
                raise ValueError(f"Path {path_str}: Cannot index into non-array")
            # Extend array if needed
            while len(current_obj) <= part_value:
                if next_part[0] == 'index':
                    current_obj.append([])
                else:
                    current_obj.append({})
            current_obj = current_obj[part_value]
    
    # Set final value
    final_part_type, final_part_value = parts[-1]
    if final_part_type == 'key':
        current_obj[final_part_value] = value
    else:  # index
        if not isinstance(current_obj, list):
            raise ValueError(f"Path {path_str}: Cannot index into non-array")
        # Extend array if needed
        while len(current_obj) <= final_part_value:
            current_obj.append(None)
        current_obj[final_part_value] = value


def to_json(pathform_text: str, indent: int = 2) -> str:
    """
    Convert PathForm text to JSON string.
    
    Args:
        pathform_text: PathForm text string
        indent: JSON indentation (default: 2)
        
    Returns:
        JSON string
    """
    obj = parse_pathform(pathform_text)
    return json.dumps(obj, indent=indent, ensure_ascii=False)


def from_json(json_obj: Union[str, Dict], flat: bool = False) -> str:
    """
    Convert JSON object to PathForm text.
    
    Args:
        json_obj: JSON string or Python dict
        flat: If True, emit all paths fully qualified (not grouped)
        
    Returns:
        PathForm text string
    """
    if isinstance(json_obj, str):
        obj = json.loads(json_obj)
    else:
        obj = json_obj
    
    lines = []
    
    def emit_path(prefix: str, value: Any) -> None:
        if isinstance(value, dict):
            for key, val in value.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                emit_path(new_prefix, val)
        elif isinstance(value, list):
            for i, val in enumerate(value):
                new_prefix = f"{prefix}[{i}]"
                emit_path(new_prefix, val)
        else:
            # Leaf value
            if isinstance(value, str):
                # Check if needs quotes
                if ' ' in value or any(c in value for c in '=#"\n\r\t'):
                    value_str = json.dumps(value)
                else:
                    value_str = value
            elif value is None:
                value_str = 'null'
            elif isinstance(value, bool):
                value_str = 'true' if value else 'false'
            else:
                value_str = str(value)
            
            lines.append(f"{prefix} = {value_str}")
    
    emit_path('', obj)
    
    if not flat:
        # Sort lines by prefix for better readability
        lines.sort()
    
    return '\n'.join(lines)


if __name__ == '__main__':
    # Example usage
    example = """# Metadata
task.id = "green_wave_istanbul_001"
task.type = route_plan
task.lang = tr

# Driver / context
driver.id = 987654
driver.experience_level = "intermediate"

city.name = "Istanbul"
city.zone = "Kadikoy"
city.country = "TR"

# Sensor-like inputs
input.current_speed_kmh = 43
input.distance_to_next_light_m = 250
input.next_light_state = green
input.next_light_time_to_change_sec = 18

# Model config
model.name = gpt-5.1
model.temperature = 0.1
model.max_tokens = 256

# Constraints
constraints[0] = "Use friendly, non-technical Turkish"
constraints[1] = "Max 2 short sentences"
constraints[2] = "Recommend safe and legal speeds only"

# Output hints
output.type = object
output.fields[0].name = "advice"
output.fields[0].type = "string"
output.fields[1].name = "recommended_speed_kmh"
output.fields[1].type = "number"
output.fields[2].name = "justification"
output.fields[2].type = "string"
"""
    
    print("Parsing PathForm...")
    result = parse_pathform(example)
    print("\nParsed JSON:")
    print(to_json(example))
    
    print("\n\nRound-trip test:")
    pathform_again = from_json(result)
    print(pathform_again)

