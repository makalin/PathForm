/**
 * Comprehensive test suite for PathForm JavaScript parser
 */

const { parsePathform, toJSON, fromJSON, parseValue, setPath } = require('../pathform.js');
const assert = require('assert');

function test(name, fn) {
    try {
        fn();
        console.log(`✓ ${name}`);
    } catch (error) {
        console.error(`✗ ${name}`);
        console.error(`  ${error.message}`);
        process.exit(1);
    }
}

// Test simple object
test('parse simple object', () => {
    const text = `user.name = "Mehmet"
user.age = 49`;
    const result = parsePathform(text);
    assert.strictEqual(result.user.name, "Mehmet");
    assert.strictEqual(result.user.age, 49);
});

// Test array
test('parse array', () => {
    const text = `items[0] = "first"
items[1] = "second"`;
    const result = parsePathform(text);
    assert.strictEqual(result.items[0], "first");
    assert.strictEqual(result.items[1], "second");
});

// Test nested arrays
test('parse nested arrays', () => {
    const text = `config.models[0].name = gpt-4
config.models[1].name = gpt-3.5`;
    const result = parsePathform(text);
    assert.strictEqual(result.config.models[0].name, "gpt-4");
    assert.strictEqual(result.config.models[1].name, "gpt-3.5");
});

// Test booleans
test('parse booleans', () => {
    const text = `is_active = true
is_beta = false`;
    const result = parsePathform(text);
    assert.strictEqual(result.is_active, true);
    assert.strictEqual(result.is_beta, false);
});

// Test null
test('parse null', () => {
    const text = "note = null";
    const result = parsePathform(text);
    assert.strictEqual(result.note, null);
});

// Test numbers
test('parse numbers', () => {
    const text = `speed = 47
temperature = -3.5
probability = 0.82`;
    const result = parsePathform(text);
    assert.strictEqual(result.speed, 47);
    assert.strictEqual(result.temperature, -3.5);
    assert.strictEqual(result.probability, 0.82);
});

// Test bare strings
test('parse bare strings', () => {
    const text = `lang = tr
role = system`;
    const result = parsePathform(text);
    assert.strictEqual(result.lang, "tr");
    assert.strictEqual(result.role, "system");
});

// Test quoted strings
test('parse quoted strings', () => {
    const text = `message = "Hello, world!"
hint = "Don't exceed 70 km/h"`;
    const result = parsePathform(text);
    assert.strictEqual(result.message, "Hello, world!");
    assert.strictEqual(result.hint, "Don't exceed 70 km/h");
});

// Test comments
test('parse comments', () => {
    const text = `# This is a comment
user.name = "Mehmet"
# Another comment
user.age = 49`;
    const result = parsePathform(text);
    assert.strictEqual(result.user.name, "Mehmet");
    assert.strictEqual(result.user.age, 49);
});

// Test round trip
test('round trip conversion', () => {
    const original = `user.name = "Mehmet"
user.age = 49
items[0] = "first"
items[1] = "second"`;
    const parsed = parsePathform(original);
    const converted = fromJSON(parsed);
    const reparsed = parsePathform(converted);
    assert.deepStrictEqual(parsed, reparsed);
});

// Test toJSON
test('toJSON conversion', () => {
    const text = `user.name = "Mehmet"
user.age = 49`;
    const jsonStr = toJSON(text);
    const obj = JSON.parse(jsonStr);
    assert.strictEqual(obj.user.name, "Mehmet");
    assert.strictEqual(obj.user.age, 49);
});

// Test fromJSON
test('fromJSON conversion', () => {
    const jsonObj = {
        user: { name: "Mehmet", age: 49 },
        items: ["first", "second"]
    };
    const pathform = fromJSON(jsonObj);
    const reparsed = parsePathform(pathform);
    assert.deepStrictEqual(reparsed, jsonObj);
});

// Test parseValue
test('parseValue string', () => {
    assert.strictEqual(parseValue("hello"), "hello");
    assert.strictEqual(parseValue('"hello world"'), "hello world");
});

test('parseValue number', () => {
    assert.strictEqual(parseValue("42"), 42);
    assert.strictEqual(parseValue("3.14"), 3.14);
});

test('parseValue boolean', () => {
    assert.strictEqual(parseValue("true"), true);
    assert.strictEqual(parseValue("false"), false);
});

test('parseValue null', () => {
    assert.strictEqual(parseValue("null"), null);
});

console.log('\nAll tests passed! ✓');

