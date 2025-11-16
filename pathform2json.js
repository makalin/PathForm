#!/usr/bin/env node
/**
 * PathForm to JSON CLI Tool (Node.js)
 * 
 * Converts PathForm text files to JSON format.
 */

const fs = require('fs');
const path = require('path');
const { parsePathform, toJSON } = require('./pathform.js');

function main() {
    const args = process.argv.slice(2);
    
    // Simple argument parsing
    let inputFile = null;
    let outputFile = null;
    let indent = 2;
    let compact = false;
    
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg === '-o' || arg === '--output') {
            outputFile = args[++i];
        } else if (arg === '--indent') {
            indent = parseInt(args[++i], 10);
        } else if (arg === '--compact') {
            compact = true;
            indent = 0;
        } else if (arg === '-h' || arg === '--help') {
            console.log(`
Usage: pathform2json [options] [input]

Convert PathForm text to JSON.

Options:
  -o, --output FILE    Output JSON file (default: stdout)
  --indent N           JSON indentation (default: 2, use 0 for compact)
  --compact             Output compact JSON (no indentation)
  -h, --help           Show this help message

Examples:
  pathform2json input.pf > output.json
  pathform2json input.pf -o output.json
  pathform2json input.pf --indent 4
  cat input.pf | pathform2json
            `);
            process.exit(0);
        } else if (!arg.startsWith('-')) {
            inputFile = arg;
        }
    }
    
    try {
        // Read input
        const text = inputFile 
            ? fs.readFileSync(inputFile, 'utf8')
            : fs.readFileSync(0, 'utf8');
        
        // Parse and convert
        const jsonOutput = toJSON(text, compact ? 0 : indent);
        
        // Write output
        if (outputFile) {
            fs.writeFileSync(outputFile, jsonOutput + '\n', 'utf8');
        } else {
            process.stdout.write(jsonOutput);
        }
        
        process.exit(0);
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

