#!/usr/bin/env node
/**
 * JSON to PathForm CLI Tool (Node.js)
 * 
 * Converts JSON files to PathForm format.
 */

const fs = require('fs');
const { fromJSON } = require('./pathform.js');

function main() {
    const args = process.argv.slice(2);
    
    // Simple argument parsing
    let inputFile = null;
    let outputFile = null;
    let flat = false;
    
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg === '-o' || arg === '--output') {
            outputFile = args[++i];
        } else if (arg === '--flat') {
            flat = true;
        } else if (arg === '-h' || arg === '--help') {
            console.log(`
Usage: json2pathform [options] [input]

Convert JSON to PathForm text.

Options:
  -o, --output FILE    Output PathForm file (default: stdout)
  --flat               Emit all paths fully qualified (not grouped)
  -h, --help           Show this help message

Examples:
  json2pathform input.json > output.pf
  json2pathform input.json -o output.pf
  json2pathform input.json --flat
  cat input.json | json2pathform
            `);
            process.exit(0);
        } else if (!arg.startsWith('-')) {
            inputFile = arg;
        }
    }
    
    try {
        // Read and parse JSON
        const jsonText = inputFile
            ? fs.readFileSync(inputFile, 'utf8')
            : fs.readFileSync(0, 'utf8');
        
        const jsonObj = JSON.parse(jsonText);
        
        // Convert to PathForm
        const pathformOutput = fromJSON(jsonObj, flat);
        
        // Write output
        if (outputFile) {
            fs.writeFileSync(outputFile, pathformOutput + '\n', 'utf8');
        } else {
            process.stdout.write(pathformOutput);
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

