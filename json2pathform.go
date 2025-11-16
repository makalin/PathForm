package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"

	"github.com/makalin/pathform"
)

func main() {
	var (
		outputFile = flag.String("o", "", "Output PathForm file (default: stdout)")
		flat       = flag.Bool("flat", false, "Emit all paths fully qualified (not grouped)")
		help       = flag.Bool("h", false, "Show help message")
		helpLong   = flag.Bool("help", false, "Show help message")
	)

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, `Usage: json2pathform [options] [input]

Convert JSON to PathForm text.

Options:
  -o FILE          Output PathForm file (default: stdout)
  -flat            Emit all paths fully qualified (not grouped)
  -h, -help        Show this help message

Examples:
  json2pathform input.json > output.pf
  json2pathform input.json -o output.pf
  json2pathform input.json -flat
  cat input.json | json2pathform
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

	// Read and parse JSON
	jsonText, err := io.ReadAll(input)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading input: %v\n", err)
		os.Exit(1)
	}

	var jsonObj map[string]interface{}
	if err := json.Unmarshal(jsonText, &jsonObj); err != nil {
		fmt.Fprintf(os.Stderr, "JSON parse error: %v\n", err)
		os.Exit(1)
	}

	// Convert to PathForm
	pathformOutput, err := pathform.FromJSON(jsonObj, *flat)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	// Write output
	if *outputFile != "" {
		err = os.WriteFile(*outputFile, []byte(pathformOutput+"\n"), 0644)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error writing output: %v\n", err)
			os.Exit(1)
		}
	} else {
		fmt.Print(pathformOutput)
	}
}

