#!/usr/bin/env python3
"""
Comprehensive test suite for PathForm Python parser
"""

import unittest
import json
from pathform import parse_pathform, to_json, from_json, parse_value, set_path


class TestPathFormParser(unittest.TestCase):
    
    def test_parse_simple_object(self):
        text = """user.name = "Mehmet"
user.age = 49"""
        result = parse_pathform(text)
        self.assertEqual(result["user"]["name"], "Mehmet")
        self.assertEqual(result["user"]["age"], 49)
    
    def test_parse_array(self):
        text = """items[0] = "first"
items[1] = "second"
items[2] = "third\""""
        result = parse_pathform(text)
        self.assertEqual(result["items"][0], "first")
        self.assertEqual(result["items"][1], "second")
        self.assertEqual(result["items"][2], "third")
    
    def test_parse_nested_arrays(self):
        text = """config.models[0].name = gpt-4
config.models[1].name = gpt-3.5"""
        result = parse_pathform(text)
        self.assertEqual(result["config"]["models"][0]["name"], "gpt-4")
        self.assertEqual(result["config"]["models"][1]["name"], "gpt-3.5")
    
    def test_parse_booleans(self):
        text = """is_active = true
is_beta = false"""
        result = parse_pathform(text)
        self.assertEqual(result["is_active"], True)
        self.assertEqual(result["is_beta"], False)
    
    def test_parse_null(self):
        text = "note = null"
        result = parse_pathform(text)
        self.assertIsNone(result["note"])
    
    def test_parse_numbers(self):
        text = """speed = 47
temperature = -3.5
probability = 0.82
learning_rate = 1e-4"""
        result = parse_pathform(text)
        self.assertEqual(result["speed"], 47)
        self.assertEqual(result["temperature"], -3.5)
        self.assertEqual(result["probability"], 0.82)
        self.assertEqual(result["learning_rate"], 1e-4)
    
    def test_parse_bare_strings(self):
        text = """lang = tr
role = system
model = gpt-5.1"""
        result = parse_pathform(text)
        self.assertEqual(result["lang"], "tr")
        self.assertEqual(result["role"], "system")
        self.assertEqual(result["model"], "gpt-5.1")
    
    def test_parse_quoted_strings(self):
        text = """message = "Hello, world!"
hint = "Don't exceed 70 km/h\""""
        result = parse_pathform(text)
        self.assertEqual(result["message"], "Hello, world!")
        self.assertEqual(result["hint"], "Don't exceed 70 km/h")
    
    def test_parse_comments(self):
        text = """# This is a comment
user.name = "Mehmet"
# Another comment
user.age = 49"""
        result = parse_pathform(text)
        self.assertEqual(result["user"]["name"], "Mehmet")
        self.assertEqual(result["user"]["age"], 49)
        self.assertNotIn("#", str(result))
    
    def test_parse_blank_lines(self):
        text = """user.name = "Mehmet"

user.age = 49"""
        result = parse_pathform(text)
        self.assertEqual(result["user"]["name"], "Mehmet")
        self.assertEqual(result["user"]["age"], 49)
    
    def test_parse_complex_example(self):
        text = """task.id = "green_wave_istanbul_001"
task.type = route_plan
task.lang = tr
driver.id = 987654
constraints[0] = "Use friendly language"
constraints[1] = "Max 2 sentences"
output.fields[0].name = "advice"
output.fields[0].type = "string\""""
        result = parse_pathform(text)
        self.assertEqual(result["task"]["id"], "green_wave_istanbul_001")
        self.assertEqual(result["task"]["type"], "route_plan")
        self.assertEqual(result["driver"]["id"], 987654)
        self.assertEqual(len(result["constraints"]), 2)
        self.assertEqual(result["output"]["fields"][0]["name"], "advice")
    
    def test_round_trip(self):
        original = """user.name = "Mehmet"
user.age = 49
items[0] = "first"
items[1] = "second"
config.enabled = true"""
        parsed = parse_pathform(original)
        converted = from_json(parsed)
        reparsed = parse_pathform(converted)
        self.assertEqual(parsed, reparsed)
    
    def test_to_json(self):
        text = """user.name = "Mehmet"
user.age = 49"""
        json_str = to_json(text)
        obj = json.loads(json_str)
        self.assertEqual(obj["user"]["name"], "Mehmet")
        self.assertEqual(obj["user"]["age"], 49)
    
    def test_from_json(self):
        json_obj = {
            "user": {"name": "Mehmet", "age": 49},
            "items": ["first", "second"]
        }
        pathform = from_json(json_obj)
        reparsed = parse_pathform(pathform)
        self.assertEqual(reparsed, json_obj)
    
    def test_parse_value_string(self):
        self.assertEqual(parse_value("hello"), "hello")
        self.assertEqual(parse_value('"hello world"'), "hello world")
    
    def test_parse_value_number(self):
        self.assertEqual(parse_value("42"), 42)
        self.assertEqual(parse_value("3.14"), 3.14)
        self.assertEqual(parse_value("1e-4"), 1e-4)
    
    def test_parse_value_boolean(self):
        self.assertEqual(parse_value("true"), True)
        self.assertEqual(parse_value("false"), False)
    
    def test_parse_value_null(self):
        self.assertIsNone(parse_value("null"))
    
    def test_set_path_simple(self):
        obj = {}
        set_path(obj, "user.name", "Mehmet")
        self.assertEqual(obj["user"]["name"], "Mehmet")
    
    def test_set_path_array(self):
        obj = {}
        set_path(obj, "items[0]", "first")
        set_path(obj, "items[1]", "second")
        self.assertEqual(obj["items"][0], "first")
        self.assertEqual(obj["items"][1], "second")
    
    def test_invalid_syntax(self):
        text = "invalid line without equals"
        with self.assertRaises(ValueError):
            parse_pathform(text)


if __name__ == '__main__':
    unittest.main()

