# Contributing Guidelines

Thank you for your interest in contributing to the ERC-8004 Trustless Agents project!

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Issues

1. Check existing issues first
2. Use issue templates when available
3. Provide clear description and steps to reproduce
4. Include relevant logs and error messages

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit PR with clear description

## Development Process

### 1. Setup Development Environment

See [Development Guide](DEVELOPMENT.md) for detailed setup instructions.

### 2. Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes  
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements

Example: `feature/add-ipfs-storage`

### 3. Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Testing
- `chore`: Maintenance

Examples:
```bash
feat(agents): add IPFS storage support
fix(api): correct validation endpoint response
docs: update deployment guide for Kubernetes
```

### 4. Code Style

#### Python

- Follow PEP 8
- Use type hints
- Maximum line length: 88 (Black default)
- Format with Black and Ruff

```bash
# Format code
flox activate -- ruff format .

# Check style
flox activate -- ruff check .
```

#### Solidity

- Follow Solidity style guide
- Use clear variable names
- Document with NatSpec comments

```solidity
/**
 * @title Agent Registry
 * @dev Manages agent registration and identity
 */
contract AgentRegistry {
    // Implementation
}
```

### 5. Testing Requirements

- Write tests for new features
- Maintain >80% code coverage
- Include unit and integration tests
- Test edge cases and error conditions

```python
def test_new_feature():
    """Test description"""
    # Arrange
    setup_test_data()
    
    # Act
    result = perform_action()
    
    # Assert
    assert result == expected
```

### 6. Documentation

- Update relevant documentation
- Include docstrings for functions
- Add comments for complex logic
- Update README if needed

```python
def complex_function(param: str) -> Dict[str, Any]:
    """
    Brief description of function.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param is invalid
    """
    # Implementation
```

## Pull Request Process

### 1. Before Submitting

- [ ] Tests pass locally
- [ ] Code is formatted
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### 2. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### 3. Review Process

1. Automated checks run
2. Code review by maintainers
3. Address feedback
4. Approval and merge

## Project Structure

### Adding New Components

#### New Agent Type

1. Create agent class in `agents/`
2. Add tests in `tests/unit/`
3. Add integration tests in `tests/integration/`
4. Create API endpoints in `api/routes/`
5. Update documentation

#### New Smart Contract

1. Add contract in `contracts/src/`
2. Add deployment script in `contracts/script/`
3. Add tests in `contracts/test/`
4. Update deployment documentation

#### New API Endpoint

1. Add route in `api/routes/`
2. Add models in `api/models.py`
3. Add tests in `tests/api/`
4. Update API documentation

## Release Process

### Version Numbering

Follow Semantic Versioning (SemVer):
- MAJOR.MINOR.PATCH
- Example: 1.2.3

### Release Steps

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Deploy to production

## Getting Help

### Resources

- [Documentation](README.md)
- [Issue Tracker](../../issues)
- [Discussions](../../discussions)

### Contact

- Open an issue for bugs
- Start a discussion for questions
- Join our Discord (if available)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- GitHub contributors page
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

## Quick Commands Reference

```bash
# Setup
flox activate
make install

# Development
make anvil         # Start blockchain (terminal 1)
make tee-start     # Start TEE simulator (terminal 2)
make deploy        # Deploy contracts
make test          # Run tests
# Code formatting:
flox activate -- ruff format .  # Format code
flox activate -- ruff check .   # Check style

# Git
git checkout -b feature/my-feature
git commit -m "feat: add new feature"
git push origin feature/my-feature
```

Thank you for contributing!