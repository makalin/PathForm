package pathform

import (
	"encoding/json"
	"fmt"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

// PathFormValue represents any valid PathForm value
type PathFormValue interface{}

// ParsePathform parses PathForm text into a map[string]interface{} (JSON-compatible)
func ParsePathform(text string) (map[string]interface{}, error) {
	result := make(map[string]interface{})
	lines := strings.Split(text, "\n")

	for lineNum, line := range lines {
		line = strings.TrimSpace(line)

		// Skip blank lines and comments
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		// Parse statement: path = value
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			return nil, fmt.Errorf("line %d: invalid syntax: %s", lineNum+1, line)
		}

		pathStr := strings.TrimSpace(parts[0])
		valueStr := strings.TrimSpace(parts[1])

		// Parse value
		value, err := parseValue(valueStr)
		if err != nil {
			return nil, fmt.Errorf("line %d: %v", lineNum+1, err)
		}

		// Set path in result
		if err := setPath(result, pathStr, value); err != nil {
			return nil, fmt.Errorf("line %d: %v", lineNum+1, err)
		}
	}

	return result, nil
}

// parseValue parses a value string into a Go value
func parseValue(valueStr string) (PathFormValue, error) {
	valueStr = strings.TrimSpace(valueStr)

	// null
	if valueStr == "null" {
		return nil, nil
	}

	// booleans
	if valueStr == "true" {
		return true, nil
	}
	if valueStr == "false" {
		return false, nil
	}

	// quoted string
	if strings.HasPrefix(valueStr, `"`) && strings.HasSuffix(valueStr, `"`) {
		var result string
		if err := json.Unmarshal([]byte(valueStr), &result); err != nil {
			return nil, fmt.Errorf("invalid quoted string: %v", err)
		}
		return result, nil
	}

	// number (try to parse as number)
	numberRegex := regexp.MustCompile(`^-?\d+(\.\d+)?([eE][+-]?\d+)?$`)
	if numberRegex.MatchString(valueStr) {
		// Try integer first
		if !strings.Contains(valueStr, ".") && !strings.ContainsAny(valueStr, "eE") {
			if intVal, err := strconv.Atoi(valueStr); err == nil {
				return intVal, nil
			}
		}
		// Try float
		if floatVal, err := strconv.ParseFloat(valueStr, 64); err == nil {
			return floatVal, nil
		}
	}

	// bare string (no quotes, no spaces, not a keyword)
	return valueStr, nil
}

// PathPart represents a part of a path (either a key or an index)
type PathPart struct {
	Type  string // "key" or "index"
	Value interface{}
}

// setPath sets a value at a given path in the object
func setPath(obj map[string]interface{}, pathStr string, value PathFormValue) error {
	// Parse path into segments and indices
	parts, err := parsePath(pathStr)
	if err != nil {
		return err
	}

	if len(parts) == 0 {
		return fmt.Errorf("empty path: %s", pathStr)
	}

	// Navigate/create structure
	currentObj := interface{}(obj)
	for i := 0; i < len(parts)-1; i++ {
		part := parts[i]
		nextPart := parts[i+1]

		if part.Type == "key" {
			key := part.Value.(string)
			currentMap, ok := currentObj.(map[string]interface{})
			if !ok {
				return fmt.Errorf("path %s: cannot access key on non-object", pathStr)
			}

			if _, exists := currentMap[key]; !exists {
				// Determine next type based on next part
				if nextPart.Type == "index" {
					currentMap[key] = make([]interface{}, 0)
				} else {
					currentMap[key] = make(map[string]interface{})
				}
			}
			currentObj = currentMap[key]
		} else if part.Type == "index" {
			index := part.Value.(int)
			currentArray, ok := currentObj.([]interface{})
			if !ok {
				return fmt.Errorf("path %s: cannot index into non-array", pathStr)
			}

			// Extend array if needed
			for len(currentArray) <= index {
				if nextPart.Type == "index" {
					currentArray = append(currentArray, make([]interface{}, 0))
				} else {
					currentArray = append(currentArray, make(map[string]interface{}))
				}
			}
			currentObj = currentArray[index]
		}
	}

	// Set final value
	finalPart := parts[len(parts)-1]
	if finalPart.Type == "key" {
		key := finalPart.Value.(string)
		currentMap, ok := currentObj.(map[string]interface{})
		if !ok {
			return fmt.Errorf("path %s: cannot set key on non-object", pathStr)
		}
		currentMap[key] = value
	} else { // index
		index := finalPart.Value.(int)
		currentArray, ok := currentObj.([]interface{})
		if !ok {
			return fmt.Errorf("path %s: cannot set index on non-array", pathStr)
		}

		// Extend array if needed
		for len(currentArray) <= index {
			currentArray = append(currentArray, nil)
		}
		currentArray[index] = value
	}

	return nil
}

// parsePath parses a path string into PathPart slices
func parsePath(pathStr string) ([]PathPart, error) {
	parts := []PathPart{}
	current := ""
	i := 0

	for i < len(pathStr) {
		if pathStr[i] == '.' {
			if current != "" {
				parts = append(parts, PathPart{Type: "key", Value: current})
				current = ""
			}
		} else if pathStr[i] == '[' {
			if current != "" {
				parts = append(parts, PathPart{Type: "key", Value: current})
				current = ""
			}
			// Find closing bracket
			j := i + 1
			for j < len(pathStr) && pathStr[j] != ']' {
				j++
			}
			if j >= len(pathStr) {
				return nil, fmt.Errorf("unclosed bracket in path: %s", pathStr)
			}
			indexStr := pathStr[i+1 : j]
			index, err := strconv.Atoi(indexStr)
			if err != nil || index < 0 {
				return nil, fmt.Errorf("invalid array index in path: %s", pathStr)
			}
			parts = append(parts, PathPart{Type: "index", Value: index})
			i = j
		} else {
			current += string(pathStr[i])
		}
		i++
	}

	if current != "" {
		parts = append(parts, PathPart{Type: "key", Value: current})
	}

	return parts, nil
}

// ToJSON converts PathForm text to JSON string
func ToJSON(pathformText string, indent int) (string, error) {
	obj, err := ParsePathform(pathformText)
	if err != nil {
		return "", err
	}

	var jsonBytes []byte
	if indent > 0 {
		jsonBytes, err = json.MarshalIndent(obj, "", strings.Repeat(" ", indent))
	} else {
		jsonBytes, err = json.Marshal(obj)
	}
	if err != nil {
		return "", err
	}

	return string(jsonBytes), nil
}

// FromJSON converts JSON object to PathForm text
func FromJSON(jsonObj interface{}, flat bool) (string, error) {
	var obj map[string]interface{}

	// Handle string input
	if jsonStr, ok := jsonObj.(string); ok {
		if err := json.Unmarshal([]byte(jsonStr), &obj); err != nil {
			return "", err
		}
	} else if objMap, ok := jsonObj.(map[string]interface{}); ok {
		obj = objMap
	} else {
		return "", fmt.Errorf("invalid JSON object type")
	}

	lines := []string{}
	emitPath("", obj, &lines)

	if !flat {
		// Sort lines by prefix for better readability
		sort.Strings(lines)
	}

	return strings.Join(lines, "\n"), nil
}

// emitPath recursively emits PathForm lines from a JSON object
func emitPath(prefix string, value interface{}, lines *[]string) {
	switch v := value.(type) {
	case map[string]interface{}:
		// Object
		for key, val := range v {
			newPrefix := key
			if prefix != "" {
				newPrefix = prefix + "." + key
			}
			emitPath(newPrefix, val, lines)
		}
	case []interface{}:
		// Array
		for i, val := range v {
			newPrefix := fmt.Sprintf("%s[%d]", prefix, i)
			emitPath(newPrefix, val, lines)
		}
	default:
		// Leaf value
		var valueStr string
		switch val := v.(type) {
		case string:
			// Check if needs quotes
			if strings.Contains(val, " ") || regexp.MustCompile(`[=#"\\\n\r\t]`).MatchString(val) {
				jsonBytes, _ := json.Marshal(val)
				valueStr = string(jsonBytes)
			} else {
				valueStr = val
			}
		case nil:
			valueStr = "null"
		case bool:
			if val {
				valueStr = "true"
			} else {
				valueStr = "false"
			}
		default:
			valueStr = fmt.Sprintf("%v", val)
		}

		*lines = append(*lines, fmt.Sprintf("%s = %s", prefix, valueStr))
	}
}

