// PathForm Parser for Rust
//
// Parses PathForm text format into JSON-compatible Rust values.

use std::collections::HashMap;
use serde_json::{Value, Map};

#[derive(Debug, Clone, PartialEq)]
pub enum PathFormError {
    InvalidSyntax(String),
    InvalidPath(String),
    InvalidValue(String),
    ParseError(String),
}

impl std::fmt::Display for PathFormError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            PathFormError::InvalidSyntax(msg) => write!(f, "Invalid syntax: {}", msg),
            PathFormError::InvalidPath(msg) => write!(f, "Invalid path: {}", msg),
            PathFormError::InvalidValue(msg) => write!(f, "Invalid value: {}", msg),
            PathFormError::ParseError(msg) => write!(f, "Parse error: {}", msg),
        }
    }
}

impl std::error::Error for PathFormError {}

/// Parse PathForm text into a JSON Value (JSON-compatible)
pub fn parse_pathform(text: &str) -> Result<Value, PathFormError> {
    let mut result = Value::Object(Map::new());

    for (line_num, line) in text.lines().enumerate() {
        let line = line.trim();

        // Skip blank lines and comments
        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        // Parse statement: path = value
        let parts: Vec<&str> = line.splitn(2, '=').collect();
        if parts.len() != 2 {
            return Err(PathFormError::InvalidSyntax(format!(
                "Line {}: Invalid syntax: {}",
                line_num + 1,
                line
            )));
        }

        let path_str = parts[0].trim();
        let value_str = parts[1].trim();

        // Parse value
        let value = parse_value(value_str)?;

        // Set path in result
        set_path(&mut result, path_str, value)?;
    }

    Ok(result)
}

/// Parse a value string into a JSON Value
fn parse_value(value_str: &str) -> Result<Value, PathFormError> {
    let value_str = value_str.trim();

    // null
    if value_str == "null" {
        return Ok(Value::Null);
    }

    // booleans
    if value_str == "true" {
        return Ok(Value::Bool(true));
    }
    if value_str == "false" {
        return Ok(Value::Bool(false));
    }

    // quoted string
    if value_str.starts_with('"') && value_str.ends_with('"') {
        match serde_json::from_str::<Value>(value_str) {
            Ok(Value::String(s)) => return Ok(Value::String(s)),
            _ => return Err(PathFormError::InvalidValue(format!(
                "Invalid quoted string: {}",
                value_str
            ))),
        }
    }

    // number (try to parse as number)
    if let Ok(num) = value_str.parse::<i64>() {
        return Ok(Value::Number(num.into()));
    }
    if let Ok(num) = value_str.parse::<f64>() {
        if let Some(n) = serde_json::Number::from_f64(num) {
            return Ok(Value::Number(n));
        }
    }

    // bare string (no quotes, no spaces, not a keyword)
    Ok(Value::String(value_str.to_string()))
}

#[derive(Debug, Clone)]
enum PathPart {
    Key(String),
    Index(usize),
}

/// Parse a path string into PathPart vector
fn parse_path(path_str: &str) -> Result<Vec<PathPart>, PathFormError> {
    let mut parts = Vec::new();
    let mut current = String::new();
    let mut chars = path_str.chars().peekable();

    while let Some(ch) = chars.next() {
        match ch {
            '.' => {
                if !current.is_empty() {
                    parts.push(PathPart::Key(current.clone()));
                    current.clear();
                }
            }
            '[' => {
                if !current.is_empty() {
                    parts.push(PathPart::Key(current.clone()));
                    current.clear();
                }
                // Find closing bracket
                let mut index_str = String::new();
                while let Some(ch) = chars.next() {
                    if ch == ']' {
                        break;
                    }
                    index_str.push(ch);
                }
                let index = index_str.parse::<usize>()
                    .map_err(|_| PathFormError::InvalidPath(format!(
                        "Invalid array index in path: {}",
                        path_str
                    )))?;
                parts.push(PathPart::Index(index));
            }
            _ => {
                current.push(ch);
            }
        }
    }

    if !current.is_empty() {
        parts.push(PathPart::Key(current));
    }

    if parts.is_empty() {
        return Err(PathFormError::InvalidPath(format!("Empty path: {}", path_str)));
    }

    Ok(parts)
}

/// Set a value at a given path in the JSON Value
fn set_path(obj: &mut Value, path_str: &str, value: Value) -> Result<(), PathFormError> {
    let parts = parse_path(path_str)?;

    // Navigate/create structure
    let mut current_obj = obj;
    for i in 0..parts.len() - 1 {
        let part = &parts[i];
        let next_part = &parts[i + 1];

        match part {
            PathPart::Key(key) => {
                let obj_map = current_obj.as_object_mut()
                    .ok_or_else(|| PathFormError::InvalidPath(format!(
                        "Path {}: Cannot access key on non-object",
                        path_str
                    )))?;

                if !obj_map.contains_key(key) {
                    // Determine next type based on next part
                    let next_value = match next_part {
                        PathPart::Index(_) => Value::Array(Vec::new()),
                        PathPart::Key(_) => Value::Object(Map::new()),
                    };
                    obj_map.insert(key.clone(), next_value);
                }
                current_obj = obj_map.get_mut(key)
                    .ok_or_else(|| PathFormError::InvalidPath(format!(
                        "Path {}: Key not found",
                        path_str
                    )))?;
            }
            PathPart::Index(index) => {
                let obj_array = current_obj.as_array_mut()
                    .ok_or_else(|| PathFormError::InvalidPath(format!(
                        "Path {}: Cannot index into non-array",
                        path_str
                    )))?;

                // Extend array if needed
                while obj_array.len() <= *index {
                    let next_value = match next_part {
                        PathPart::Index(_) => Value::Array(Vec::new()),
                        PathPart::Key(_) => Value::Object(Map::new()),
                    };
                    obj_array.push(next_value);
                }
                current_obj = obj_array.get_mut(*index)
                    .ok_or_else(|| PathFormError::InvalidPath(format!(
                        "Path {}: Index out of bounds",
                        path_str
                    )))?;
            }
        }
    }

    // Set final value
    let final_part = &parts[parts.len() - 1];
    match final_part {
        PathPart::Key(key) => {
            let obj_map = current_obj.as_object_mut()
                .ok_or_else(|| PathFormError::InvalidPath(format!(
                    "Path {}: Cannot set key on non-object",
                    path_str
                )))?;
            obj_map.insert(key.clone(), value);
        }
        PathPart::Index(index) => {
            let obj_array = current_obj.as_array_mut()
                .ok_or_else(|| PathFormError::InvalidPath(format!(
                    "Path {}: Cannot set index on non-array",
                    path_str
                )))?;

            // Extend array if needed
            while obj_array.len() <= *index {
                obj_array.push(Value::Null);
            }
            obj_array[*index] = value;
        }
    }

    Ok(())
}

/// Convert PathForm text to JSON string
pub fn to_json(pathform_text: &str, indent: usize) -> Result<String, PathFormError> {
    let obj = parse_pathform(pathform_text)?;
    if indent > 0 {
        serde_json::to_string_pretty(&obj)
            .map_err(|e| PathFormError::ParseError(e.to_string()))
    } else {
        serde_json::to_string(&obj)
            .map_err(|e| PathFormError::ParseError(e.to_string()))
    }
}

/// Convert JSON Value to PathForm text
pub fn from_json(json_obj: &Value, flat: bool) -> String {
    let mut lines = Vec::new();
    emit_path("", json_obj, &mut lines);

    if !flat {
        lines.sort();
    }

    lines.join("\n")
}

/// Recursively emit PathForm lines from a JSON Value
fn emit_path(prefix: &str, value: &Value, lines: &mut Vec<String>) {
    match value {
        Value::Object(map) => {
            for (key, val) in map {
                let new_prefix = if prefix.is_empty() {
                    key.clone()
                } else {
                    format!("{}.{}", prefix, key)
                };
                emit_path(&new_prefix, val, lines);
            }
        }
        Value::Array(arr) => {
            for (i, val) in arr.iter().enumerate() {
                let new_prefix = format!("{}[{}]", prefix, i);
                emit_path(&new_prefix, val, lines);
            }
        }
        _ => {
            // Leaf value
            let value_str = match value {
                Value::String(s) => {
                    // Check if needs quotes
                    let needs_quotes = s.contains(' ') || 
                        s.contains('=') || s.contains('#') || s.contains('"') || 
                        s.contains('\\') || s.contains('\n') || s.contains('\r') || s.contains('\t');
                    if needs_quotes {
                        serde_json::to_string(s).unwrap()
                    } else {
                        s.clone()
                    }
                }
                Value::Null => "null".to_string(),
                Value::Bool(b) => {
                    if *b {
                        "true".to_string()
                    } else {
                        "false".to_string()
                    }
                }
                _ => value.to_string(),
            };

            lines.push(format!("{} = {}", prefix, value_str));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_simple() {
        let text = r#"
user.name = "Mehmet"
user.age = 49
"#;
        let result = parse_pathform(text).unwrap();
        assert_eq!(result["user"]["name"], "Mehmet");
        assert_eq!(result["user"]["age"], 49);
    }

    #[test]
    fn test_parse_array() {
        let text = r#"
items[0] = "first"
items[1] = "second"
"#;
        let result = parse_pathform(text).unwrap();
        assert_eq!(result["items"][0], "first");
        assert_eq!(result["items"][1], "second");
    }
}

