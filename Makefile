.PHONY: install dev test lint format clean build docker docs

# Default target
all: install

# Install production dependencies
install:
pip install -e .
python -m playwright install chromium

# Install development dependencies
dev: install
pip install -e ".[dev]"
python -m playwright install-deps chromium

# Run tests
test:
pytest tests/ -v --tb=short

# Run tests with coverage
coverage:
pytest tests/ -v --tb=short --cov=web_all --cov-report=html --cov-report=term-missing

# Lint code
lint:
ruff check web_all tests
black --check web_all tests

# Format code
format:
black web_all tests
ruff check --fix web_all tests

# Clean build artifacts
clean:
rm -rf build/ dist/ *.egg-info __pycache__/ .pytest_cache/ .coverage htmlcov/
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf output/*

# Build package
build:
python -m build

# Build Docker image
docker:
docker build -t web-all:latest .

# Run Docker container
docker-run:
docker run -p 8000:8000 -v $(PWD)/output:/app/output web-all:latest

# Start development server
serve:
web-all serve --port 8000

# Start API only
api:
web-all serve --no-gui --port 8000

# Help
help:
@echo "Available targets:"
@echo "  install   - Install production dependencies"
@echo "  dev       - Install development dependencies"
@echo "  test      - Run tests"
@echo "  coverage  - Run tests with coverage report"
@echo "  lint      - Run linters"
@echo "  format    - Format code"
@echo "  clean     - Clean build artifacts"
@echo "  build     - Build package"
@echo "  docker    - Build Docker image"
@echo "  docker-run - Run Docker container"
@echo "  serve     - Start development server"
@echo "  api       - Start API server only"
