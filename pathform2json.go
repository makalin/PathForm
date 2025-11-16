package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"github.com/makalin/pathform"
)

func main() {
	var (
		outputFile = flag.String("o", "", "Output JSON file (default: stdout)")
		indent     = flag.Int("indent", 2, "JSON indentation (default: 2, use 0 for compact)")
		compact    = flag.Bool("compact", false, "Output compact JSON (no indentation)")
		help       = flag.Bool("h", false, "Show help message")
		helpLong   = flag.Bool("help", false, "Show help message")
	)

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, `Usage: pathform2json [options] [input]

Convert PathForm text to JSON.

Options:
  -o FILE          Output JSON file (default: stdout)
  -indent N        JSON indentation (default: 2, use 0 for compact)
  -compact         Output compact JSON (no indentation)
  -h, -help        Show this help message

Examples:
  pathform2json input.pf > output.json
  pathform2json input.pf -o output.json
  pathform2json input.pf -indent 4
  cat input.pf | pathform2json
`)
	}

	flag.Parse()

	if *help || *helpLong {
		flag.Usage()
		os.Exit(0)
	}

	// Determine input
	var input io.Reader
	if flag.NArg() > 0 {
		file, err := os.Open(flag.Arg(0))
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error opening input file: %v\n", err)
			os.Exit(1)
		}
		defer file.Close()
		input = file
	} else {
		input = os.Stdin
	}

	// Read input
	text, err := io.ReadAll(input)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading input: %v\n", err)
		os.Exit(1)
	}

	// Parse and convert
	indentValue := *indent
	if *compact {
		indentValue = 0
	}

	jsonOutput, err := pathform.ToJSON(string(text), indentValue)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	// Write output
	if *outputFile != "" {
		err = os.WriteFile(*outputFile, []byte(jsonOutput+"\n"), 0644)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error writing output: %v\n", err)
			os.Exit(1)
		}
	} else {
		fmt.Print(jsonOutput)
	}
}

