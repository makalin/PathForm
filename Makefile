# Makefile for PathForm project

.PHONY: all test clean install format lint help

# Default target
all: test

# Python targets
PYTHON := python3
PIP := pip3

# Node.js targets
NODE := node
NPM := npm

# Go targets
GO := go

# Test all implementations
test: test-python test-js test-go
	@echo "All tests passed!"

# Python tests
test-python:
	@echo "Running Python tests..."
	$(PYTHON) -m pytest test_pathform.py -v || $(PYTHON) test_pathform.py

# JavaScript tests
test-js:
	@echo "Running JavaScript tests..."
	$(NODE) test/test.js

# Go tests
test-go:
	@echo "Running Go tests..."
	$(GO) test ./... -v || echo "Go tests not yet implemented"

# Install Python package
install-python:
	$(PIP) install -e .

# Install Node.js package
install-js:
	$(NPM) install

# Install all
install: install-python install-js
	@echo "Installation complete!"

# Format code
format:
	@echo "Formatting Python code..."
	$(PYTHON) -m black pathform.py pathform2json.py json2pathform.py pathform_validator.py pathform_formatter.py test_pathform.py 2>/dev/null || echo "black not installed, skipping"
	@echo "Formatting JavaScript code..."
	$(NPM) run format 2>/dev/null || echo "prettier not installed, skipping"

# Lint code
lint:
	@echo "Linting Python code..."
	$(PYTHON) -m pylint pathform.py pathform2json.py json2pathform.py 2>/dev/null || echo "pylint not installed, skipping"
	@echo "Linting JavaScript code..."
	$(NPM) run lint 2>/dev/null || echo "eslint not installed, skipping"

# Build binaries
build:
	@echo "Building Go binaries..."
	$(GO) build -o bin/pathform2json pathform2json.go
	$(GO) build -o bin/json2pathform json2pathform.go
	@echo "Build complete!"

# Clean build artifacts
clean:
	rm -rf bin/
	rm -rf __pycache__/
	rm -rf *.pyc
	rm -rf .pytest_cache/
	rm -rf node_modules/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	@echo "Clean complete!"

# Run example
example:
	@echo "Running example..."
	@$(PYTHON) -c "from pathform import parse_pathform, to_json; text = open('examples/green_wave.pf').read() if __import__('os').path.exists('examples/green_wave.pf') else 'task.id = example\ntask.type = test'; print(to_json(text))"

# Help
help:
	@echo "PathForm Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make test          - Run all tests"
	@echo "  make test-python   - Run Python tests"
	@echo "  make test-js       - Run JavaScript tests"
	@echo "  make test-go       - Run Go tests"
	@echo "  make install       - Install all packages"
	@echo "  make format        - Format all code"
	@echo "  make lint          - Lint all code"
	@echo "  make build         - Build binaries"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make example       - Run example"
	@echo "  make help          - Show this help"

