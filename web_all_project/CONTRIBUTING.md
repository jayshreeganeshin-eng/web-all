# Contributing to web-all

Thank you for considering contributing to web-all! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Welcome newcomers and help them learn

## How to Contribute

### 1. Fork and Clone

```bash
git clone https://github.com/your-username/web-all.git
cd web-all
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Make Changes

- Follow existing code style
- Add tests for new features
- Update documentation as needed
- Use type hints where appropriate

### 5. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=web_all

# Run linting
black .
ruff check .
mypy web_all/
```

### 6. Commit Changes

We use conventional commits:

```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in cloner"
git commit -m "docs: update README"
git commit -m "test: add tests for API"
git commit -m "refactor: improve error handling"
```

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub with:
- Clear description of changes
- Link to related issues
- Screenshots if applicable
- Test results

## Development Guidelines

### Code Style

- Use Black for formatting (line length: 100)
- Use Ruff for linting
- Add type hints to function signatures
- Write docstrings for public APIs

### Testing

- Write unit tests for new functionality
- Aim for >80% code coverage
- Use pytest fixtures for common setup
- Mock external services in tests

### Documentation

- Update README for user-facing changes
- Add docstrings to functions/classes
- Include examples in docstrings
- Update CHANGELOG.md

### Performance

- Use async/await for I/O operations
- Implement proper connection pooling
- Add caching where appropriate
- Profile before optimizing

## Reporting Issues

When reporting bugs, include:
- Python version
- OS and version
- Steps to reproduce
- Expected vs actual behavior
- Error messages/tracebacks

## Feature Requests

Feature requests are welcome! Please include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Potential impact

## Questions?

- Check existing documentation
- Search closed issues
- Ask in GitHub Discussions

Thank you for contributing to web-all! 🕷️
