/**
 * PathForm Integration Example - Node.js
 * 
 * Demonstrates how to use PathForm in a Node.js application.
 */

const { parsePathform, fromJSON, toJSON } = require('../pathform.js');

// Example 1: Parse PathForm from file or string
const pathformText = `
user.name = "Mehmet"
user.age = 49
user.preferences.theme = dark
user.preferences.notifications = true
items[0] = "first"
items[1] = "second"
`;

console.log('=== Example 1: Parsing PathForm ===');
const data = parsePathform(pathformText);
console.log(JSON.stringify(data, null, 2));
console.log();

// Example 2: Convert JSON to PathForm
const jsonData = {
    task: {
        id: "task_001",
        type: "summarize",
        lang: "tr"
    },
    constraints: [
        "Max 2 sentences",
        "Use friendly language"
    ]
};

console.log('=== Example 2: Converting JSON to PathForm ===');
const pathformOutput = fromJSON(jsonData);
console.log(pathformOutput);
console.log();

// Example 3: Round-trip conversion
console.log('=== Example 3: Round-trip conversion ===');
const original = parsePathform(pathformText);
const pathform = fromJSON(original);
const reparsed = parsePathform(pathform);
console.log('Round-trip successful!');
console.log();

// Example 4: Using with LLM prompts
console.log('=== Example 4: LLM Integration ===');
const llmPrompt = `
You must respond ONLY in PathForm format.

Define a task configuration:
${pathformOutput}

Now modify it for a new task.
`;
console.log(llmPrompt);

