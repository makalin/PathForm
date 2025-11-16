/**
 * PathForm Parser for Browser
 * 
 * Parses PathForm text format into JSON-compatible JavaScript objects.
 * Works in browsers without Node.js dependencies.
 */

(function(global) {
    'use strict';
    
    /**
     * Parse PathForm text into a JavaScript object (JSON-compatible).
     * 
     * @param {string} text - PathForm text string
     * @returns {Object} Object representing the parsed PathForm structure
     */
    function parsePathform(text) {
        const result = {};
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
     * Parse a value string into a JavaScript value.
     * 
     * Handles: numbers, booleans, null, strings (bare or quoted)
     * 
     * @param {string} valueStr - Value string to parse
     * @returns {*} Parsed value
     */
    function parseValue(valueStr) {
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
            if (valueStr.indexOf('.') !== -1 || /[eE]/.test(valueStr)) {
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
     * @param {Object} obj - Object to modify
     * @param {string} pathStr - Path string
     * @param {*} value - Value to set
     */
    function setPath(obj, pathStr, value) {
        // Parse path into segments and indices
        const parts = [];
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
        let currentObj = obj;
        for (let i = 0; i < parts.length - 1; i++) {
            const part = parts[i];
            const nextPart = parts[i + 1];
            
            if (part.type === 'key') {
                if (!(part.value in currentObj)) {
                    // Determine next type based on next part
                    if (nextPart.type === 'index') {
                        currentObj[part.value] = [];
                    } else {
                        currentObj[part.value] = {};
                    }
                }
                currentObj = currentObj[part.value];
            } else if (part.type === 'index') {
                // Ensure it's an array
                if (!Array.isArray(currentObj)) {
                    throw new Error(`Path ${pathStr}: Cannot index into non-array`);
                }
                // Extend array if needed
                while (currentObj.length <= part.value) {
                    if (nextPart.type === 'index') {
                        currentObj.push([]);
                    } else {
                        currentObj.push({});
                    }
                }
                currentObj = currentObj[part.value];
            }
        }
        
        // Set final value
        const finalPart = parts[parts.length - 1];
        if (finalPart.type === 'key') {
            currentObj[finalPart.value] = value;
        } else { // index
            if (!Array.isArray(currentObj)) {
                throw new Error(`Path ${pathStr}: Cannot index into non-array`);
            }
            // Extend array if needed
            while (currentObj.length <= finalPart.value) {
                currentObj.push(null);
            }
            currentObj[finalPart.value] = value;
        }
    }
    
    /**
     * Convert PathForm text to JSON string.
     * 
     * @param {string} pathformText - PathForm text string
     * @param {number} indent - JSON indentation (default: 2)
     * @returns {string} JSON string
     */
    function toJSON(pathformText, indent) {
        indent = indent === undefined ? 2 : indent;
        const obj = parsePathform(pathformText);
        return JSON.stringify(obj, null, indent);
    }
    
    /**
     * Convert JSON object to PathForm text.
     * 
     * @param {Object|string} jsonObj - JSON object or string
     * @param {boolean} flat - If true, emit all paths fully qualified (not grouped)
     * @returns {string} PathForm text string
     */
    function fromJSON(jsonObj, flat) {
        flat = flat === undefined ? false : flat;
        const obj = typeof jsonObj === 'string' ? JSON.parse(jsonObj) : jsonObj;
        const lines = [];
        
        function emitPath(prefix, value) {
            if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                // Object
                for (const key in value) {
                    if (value.hasOwnProperty(key)) {
                        const newPrefix = prefix ? prefix + '.' + key : key;
                        emitPath(newPrefix, value[key]);
                    }
                }
            } else if (Array.isArray(value)) {
                // Array
                for (let i = 0; i < value.length; i++) {
                    const newPrefix = prefix + '[' + i + ']';
                    emitPath(newPrefix, value[i]);
                }
            } else {
                // Leaf value
                let valueStr;
                if (typeof value === 'string') {
                    // Check if needs quotes
                    if (value.indexOf(' ') !== -1 || /[=#"\\\n\r\t]/.test(value)) {
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
                
                lines.push(prefix + ' = ' + valueStr);
            }
        }
        
        emitPath('', obj);
        
        if (!flat) {
            // Sort lines by prefix for better readability
            lines.sort();
        }
        
        return lines.join('\n');
    }
    
    // Export to global scope
    if (typeof global !== 'undefined') {
        global.PathForm = {
            parse: parsePathform,
            parseValue: parseValue,
            setPath: setPath,
            toJSON: toJSON,
            fromJSON: fromJSON
        };
    }
    
    // Also support AMD and CommonJS if available
    if (typeof define === 'function' && define.amd) {
        define(function() {
            return {
                parse: parsePathform,
                parseValue: parseValue,
                setPath: setPath,
                toJSON: toJSON,
                fromJSON: fromJSON
            };
        });
    }
    
})(typeof window !== 'undefined' ? window : typeof global !== 'undefined' ? global : this);

