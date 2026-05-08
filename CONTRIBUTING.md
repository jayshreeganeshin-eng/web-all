# Contributing to web-all

Thank you for your interest in contributing to web-all! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Welcome newcomers and help them learn

## How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Open an issue describing the feature
2. Explain the use case
3. Discuss implementation approach

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes** following code style guidelines
4. **Write tests** for new functionality
5. **Run tests** to ensure everything passes:
   ```bash
   make test
   ```
6. **Lint code**:
   ```bash
   make lint
   ```
7. **Format code**:
   ```bash
   make format
   ```
8. **Commit** with clear messages:
   ```bash
   git commit -m "feat: add new feature"
   ```
9. **Push** to your fork
10. **Open a Pull Request**

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/web-all.git
   cd web-all
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

3. Install development dependencies:
   ```bash
   make dev
   ```

4. Install Playwright browsers:
   ```bash
   python -m playwright install chromium
   ```

## Code Style

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use Ruff for linting
- Write docstrings for public functions/classes
- Type hints are encouraged

## Testing

- Write unit tests for new features
- Maintain >80% code coverage
- Run tests before submitting PR:
  ```bash
  pytest tests/ -v --cov=web_all
  ```

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

Example:
```
feat: add AI-powered content summarization

- Implement summarize_content method in AIEngine
- Add support for multiple AI providers
- Include tests for summarization feature
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to code
- Update API documentation if needed

## Questions?

Feel free to open an issue for any questions or discussions.

Thank you for contributing! 🎉
