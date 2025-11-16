# Contributing to PathForm

Thank you for your interest in contributing to PathForm! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/pathform.git`
3. Create a branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Python
```bash
pip install -e .
python test_pathform.py
```

### JavaScript/Node.js
```bash
npm install
npm test
```

### Go
```bash
go mod download
go test ./...
```

## Making Changes

1. **Code Style**
   - Python: Follow PEP 8
   - JavaScript: Follow the existing style, use ESLint
   - Go: Use `gofmt`

2. **Tests**
   - Add tests for new features
   - Ensure all existing tests pass
   - Run: `make test`

3. **Documentation**
   - Update README.md if adding features
   - Add docstrings/comments to code
   - Update examples if needed

## Submitting Changes

1. Commit your changes: `git commit -m "Add feature X"`
2. Push to your fork: `git push origin feature/your-feature-name`
3. Create a Pull Request on GitHub

## Implementation Guidelines

### Adding a New Language Parser

1. Create `pathform.{ext}` with:
   - `parse_pathform()` / `parsePathform()` function
   - `to_json()` / `toJSON()` function
   - `from_json()` / `fromJSON()` function

2. Add CLI tools:
   - `pathform2json.{ext}`
   - `json2pathform.{ext}`

3. Add tests in `test/` directory

4. Update README.md with the new language

### Testing Requirements

- All parsers must pass the same test suite
- Round-trip conversion must work (PathForm → JSON → PathForm)
- Edge cases must be handled (empty files, comments, etc.)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Questions?

Open an issue on GitHub or contact the maintainer.

Thank you for contributing! 🎉

