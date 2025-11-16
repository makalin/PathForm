/**
 * PathForm Parser for TypeScript
 * 
 * Parses PathForm text format into JSON-compatible TypeScript objects.
 */

type PathFormValue = string | number | boolean | null | PathFormObject | PathFormArray;
type PathFormObject = { [key: string]: PathFormValue };
type PathFormArray = PathFormValue[];

interface PathPart {
    type: 'key' | 'index';
    value: string | number;
}

/**
 * Parse PathForm text into a TypeScript object (JSON-compatible).
 * 
 * @param text - PathForm text string
 * @returns Object representing the parsed PathForm structure
 */
export function parsePathform(text: string): PathFormObject {
    const result: PathFormObject = {};
    const lines = text.split('\n');
    
    for (let lineNum = 0; lineNum < lines.length; lineNum++) {
        let line = lines[lineNum].trim();
        
        // Skip blank lines and comments
        if (!line || line.startsWith('#')) {
            continue;
        }
        
        // Parse statement: path = value
        const match = line.match(/^([^=]+?)\s*=\s*(.+)$/);
        if (!match) {
            throw new Error(`Line ${lineNum + 1}: Invalid syntax: ${line}`);
        }
        
        const pathStr = match[1].trim();
        const valueStr = match[2].trim();
        
        // Parse value
        const value = parseValue(valueStr);
        
        // Set path in result
        setPath(result, pathStr, value);
    }
    
    return result;
}

/**
 * Parse a value string into a TypeScript value.
 * 
 * Handles: numbers, booleans, null, strings (bare or quoted)
 * 
 * @param valueStr - Value string to parse
 * @returns Parsed value
 */
export function parseValue(valueStr: string): PathFormValue {
    valueStr = valueStr.trim();
    
    // null
    if (valueStr === 'null') {
        return null;
    }
    
    // booleans
    if (valueStr === 'true') {
        return true;
    }
    if (valueStr === 'false') {
        return false;
    }
    
    // quoted string
    if (valueStr.startsWith('"') && valueStr.endsWith('"')) {
        // Use JSON.parse for proper escaping
        return JSON.parse(valueStr);
    }
    
    // number (try to parse as number)
    // Check if it looks like a number
    const numberMatch = valueStr.match(/^-?\d+(\.\d+)?([eE][+-]?\d+)?$/);
    if (numberMatch) {
        // Parse as float if it has decimal or exponent, otherwise integer
        if (valueStr.includes('.') || /[eE]/.test(valueStr)) {
            return parseFloat(valueStr);
        }
        return parseInt(valueStr, 10);
    }
    
    // bare string (no quotes, no spaces, not a keyword)
    return valueStr;
}

/**
 * Set a value at a given path in the object.
 * 
 * Path format: segment(.segment|\[index\])*
 * Examples: user.name, items[0], config.models[1].name
 * 
 * @param obj - Object to modify
 * @param pathStr - Path string
 * @param value - Value to set
 */
export function setPath(obj: PathFormObject, pathStr: string, value: PathFormValue): void {
    // Parse path into segments and indices
    const parts: PathPart[] = [];
    let current = '';
    let i = 0;
    
    while (i < pathStr.length) {
        if (pathStr[i] === '.') {
            if (current) {
                parts.push({ type: 'key', value: current });
                current = '';
            }
        } else if (pathStr[i] === '[') {
            if (current) {
                parts.push({ type: 'key', value: current });
                current = '';
            }
            // Find closing bracket
            let j = i + 1;
            while (j < pathStr.length && pathStr[j] !== ']') {
                j++;
            }
            if (j >= pathStr.length) {
                throw new Error(`Unclosed bracket in path: ${pathStr}`);
            }
            const indexStr = pathStr.substring(i + 1, j);
            const index = parseInt(indexStr, 10);
            if (isNaN(index) || index < 0) {
                throw new Error(`Invalid array index in path: ${pathStr}`);
            }
            parts.push({ type: 'index', value: index });
            i = j;
        } else {
            current += pathStr[i];
        }
        i++;
    }
    
    if (current) {
        parts.push({ type: 'key', value: current });
    }
    
    if (parts.length === 0) {
        throw new Error(`Empty path: ${pathStr}`);
    }
    
    // Navigate/create structure
    let currentObj: any = obj;
    for (let i = 0; i < parts.length - 1; i++) {
        const part = parts[i];
        const nextPart = parts[i + 1];
        
        if (part.type === 'key') {
            const key = part.value as string;
            if (!(key in currentObj)) {
                // Determine next type based on next part
                if (nextPart.type === 'index') {
                    currentObj[key] = [];
                } else {
                    currentObj[key] = {};
                }
            }
            currentObj = currentObj[key];
        } else if (part.type === 'index') {
            // Ensure it's an array
            if (!Array.isArray(currentObj)) {
                throw new Error(`Path ${pathStr}: Cannot index into non-array`);
            }
            // Extend array if needed
            const index = part.value as number;
            while (currentObj.length <= index) {
                if (nextPart.type === 'index') {
                    currentObj.push([]);
                } else {
                    currentObj.push({});
                }
            }
            currentObj = currentObj[index];
        }
    }
    
    // Set final value
    const finalPart = parts[parts.length - 1];
    if (finalPart.type === 'key') {
        (currentObj as PathFormObject)[finalPart.value as string] = value;
    } else { // index
        if (!Array.isArray(currentObj)) {
            throw new Error(`Path ${pathStr}: Cannot index into non-array`);
        }
        // Extend array if needed
        const index = finalPart.value as number;
        while (currentObj.length <= index) {
            currentObj.push(null);
        }
        currentObj[index] = value;
    }
}

/**
 * Convert PathForm text to JSON string.
 * 
 * @param pathformText - PathForm text string
 * @param indent - JSON indentation (default: 2)
 * @returns JSON string
 */
export function toJSON(pathformText: string, indent: number = 2): string {
    const obj = parsePathform(pathformText);
    return JSON.stringify(obj, null, indent);
}

/**
 * Convert JSON object to PathForm text.
 * 
 * @param jsonObj - JSON object or string
 * @param flat - If true, emit all paths fully qualified (not grouped)
 * @returns PathForm text string
 */
export function fromJSON(jsonObj: PathFormObject | string, flat: boolean = false): string {
    const obj: PathFormObject = typeof jsonObj === 'string' ? JSON.parse(jsonObj) : jsonObj;
    const lines: string[] = [];
    
    function emitPath(prefix: string, value: PathFormValue): void {
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            // Object
            for (const key in value) {
                if (value.hasOwnProperty(key)) {
                    const newPrefix = prefix ? `${prefix}.${key}` : key;
                    emitPath(newPrefix, value[key]);
                }
            }
        } else if (Array.isArray(value)) {
            // Array
            for (let i = 0; i < value.length; i++) {
                const newPrefix = `${prefix}[${i}]`;
                emitPath(newPrefix, value[i]);
            }
        } else {
            // Leaf value
            let valueStr: string;
            if (typeof value === 'string') {
                // Check if needs quotes
                if (value.includes(' ') || /[=#"\\\n\r\t]/.test(value)) {
                    valueStr = JSON.stringify(value);
                } else {
                    valueStr = value;
                }
            } else if (value === null) {
                valueStr = 'null';
            } else if (typeof value === 'boolean') {
                valueStr = value ? 'true' : 'false';
            } else {
                valueStr = String(value);
            }
            
            lines.push(`${prefix} = ${valueStr}`);
        }
    }
    
    emitPath('', obj);
    
    if (!flat) {
        // Sort lines by prefix for better readability
        lines.sort();
    }
    
    return lines.join('\n');
}

// Default export
export default {
    parse: parsePathform,
    parseValue,
    setPath,
    toJSON,
    fromJSON
};

