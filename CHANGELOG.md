# Changelog

All notable changes to PathForm will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-XX

### Added
- Initial release of PathForm specification
- Python parser (`pathform.py`)
- JavaScript/Node.js parser (`pathform.js`)
- JavaScript/Browser parser (`pathform.browser.js`)
- TypeScript parser (`pathform.ts`)
- Go parser (`pathform.go`)
- Rust parser (`pathform.rs`)
- CLI tools:
  - `pathform2json` (Python, Node.js, Go)
  - `json2pathform` (Python, Node.js, Go)
- Validation tool (`pathform_validator.py`)
- Formatter tool (`pathform_formatter.py`)
- Diff tool (`pathform_diff.py`)
- Benchmark tool (`benchmark.py`)
- Comprehensive test suites for all parsers
- Example files and integration examples
- Package configurations:
  - `package.json` for npm
  - `setup.py` for PyPI
  - `go.mod` for Go modules
  - `Cargo.toml` for Rust
- Makefile for build automation
- GitHub Actions CI/CD workflow
- TypeScript type definitions (`pathform.d.ts`)
- Documentation:
  - README.md with full specification
  - CONTRIBUTING.md
  - CHANGELOG.md

### Features
- Parse PathForm text to JSON-compatible objects
- Convert JSON to PathForm text
- Round-trip conversion support
- Support for nested objects and arrays
- Support for all JSON value types (string, number, boolean, null)
- Comment support (lines starting with `#`)
- Blank line support
- Path syntax: `key.subkey[index]`

### Supported Languages
- Python 3.6+
- JavaScript/Node.js 12+
- TypeScript
- Go 1.19+
- Rust (with serde_json)

