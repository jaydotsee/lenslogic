# Contributing to LensLogic

Thank you for your interest in contributing to LensLogic! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic knowledge of Python and CLI development

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/lenslogic.git
   cd lenslogic
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests**
   ```bash
   pytest tests/
   ```

5. **Run the application**
   ```bash
   python src/main.py --help
   ```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Sample files** (if applicable and non-sensitive)
- **Log output** (with `--verbose` flag)

### Suggesting Features

Feature requests are welcome! Please include:

- **Clear description** of the feature
- **Use case** - why is this feature needed?
- **Proposed implementation** (if you have ideas)
- **Potential impact** on existing functionality

### Pull Requests

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

3. **Commit your changes**
   ```bash
   git commit -m "feat: add feature description"
   ```

4. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Write descriptive docstrings for functions and classes
- Keep functions focused and reasonably sized

### Testing

- Write tests for new functionality
- Ensure tests pass before submitting PR
- Use descriptive test names
- Include both unit tests and integration tests

### Documentation

- Update README.md for new features
- Add docstrings to new functions/classes
- Update relevant documentation files
- Include examples for new features

### Commit Messages

Use conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/modifications
- `refactor:` for code refactoring
- `chore:` for maintenance tasks

## Areas for Contribution

### Priority Areas

1. **Cross-platform compatibility** - Testing on different OS
2. **Performance optimization** - Large file handling
3. **Additional metadata sources** - New camera/format support
4. **UI/UX improvements** - Interactive menu enhancements
5. **Documentation** - Examples, tutorials, guides

### Good First Issues

- Add support for new camera models
- Improve error messages
- Add new file format support
- Create example configurations
- Improve test coverage

### Advanced Contributions

- Video metadata extraction enhancements
- Machine learning for photo categorization
- Cloud storage integration
- GUI application development
- Performance profiling and optimization

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_enhanced_exif_extractor.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v
```

### Test Structure

- Unit tests in `tests/` directory
- Integration tests marked with `@pytest.mark.integration`
- Use fixtures for common test data
- Mock external dependencies

## Code Review Process

1. **Automated checks** must pass (tests, linting)
2. **Code review** by maintainers
3. **Documentation review** for user-facing changes
4. **Testing** on different platforms if needed

## Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Documentation** - Check existing docs first

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Documentation credits

## License

By contributing to LensLogic, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to LensLogic! 🚀