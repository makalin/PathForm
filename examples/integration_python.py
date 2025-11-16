#!/usr/bin/env python3
"""
PathForm Integration Example - Python

Demonstrates how to use PathForm in a Python application.
"""

from pathform import parse_pathform, from_json, to_json
import json

# Example 1: Parse PathForm from file or string
pathform_text = """
user.name = "Mehmet"
user.age = 49
user.preferences.theme = dark
user.preferences.notifications = true
items[0] = "first"
items[1] = "second"
"""

print("=== Example 1: Parsing PathForm ===")
data = parse_pathform(pathform_text)
print(json.dumps(data, indent=2))
print()

# Example 2: Convert JSON to PathForm
json_data = {
    "task": {
        "id": "task_001",
        "type": "summarize",
        "lang": "tr"
    },
    "constraints": [
        "Max 2 sentences",
        "Use friendly language"
    ]
}

print("=== Example 2: Converting JSON to PathForm ===")
pathform_output = from_json(json_data)
print(pathform_output)
print()

# Example 3: Round-trip conversion
print("=== Example 3: Round-trip conversion ===")
original = parse_pathform(pathform_text)
pathform = from_json(original)
reparsed = parse_pathform(pathform)
assert original == reparsed
print("Round-trip successful!")
print()

# Example 4: Using with LLM prompts
print("=== Example 4: LLM Integration ===")
llm_prompt = f"""
You must respond ONLY in PathForm format.

Define a task configuration:
{pathform_output}

Now modify it for a new task.
"""
print(llm_prompt)

