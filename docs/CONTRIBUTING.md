# Contributing to Vernachain

We love your input! We want to make contributing to Vernachain as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Pull Request Process

1. Update the README.md with details of changes to the interface, if applicable.
2. Update the docs/ folder with any new documentation or changes to existing docs.
3. The PR will be merged once you have the sign-off of two other developers.

## Any Contributions You Make Will Be Under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](../LICENSE) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report Bugs Using GitHub's [Issue Tracker](https://github.com/BronzonTech-Cloud/vernachain/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/BronzonTech-Cloud/vernachain/issues/new).

## Write Bug Reports with Detail, Background, and Sample Code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Code Style

* Use 4 spaces for indentation
* Maximum line length is 88 characters
* Follow PEP 8 guidelines
* Use type hints for function arguments and return values
* Write docstrings for all public functions and classes

## Testing

* Write unit tests for all new code
* Tests should be in the `tests/` directory
* Use pytest for testing
* Aim for high test coverage

## Documentation

* Update documentation for any changed functionality
* Write clear docstrings for all functions, classes, and modules
* Keep the [API Reference](api-reference.md) up to date
* Add examples for new features

## Community

* Be welcoming to newcomers
* Be respectful of differing viewpoints and experiences
* Gracefully accept constructive criticism
* Focus on what is best for the community
* Show empathy towards other community members

## Getting Help

* Check the [documentation](README.md)
* Ask in GitHub Issues
* Contact the maintainers

## Project Structure

```
vernachain/
├── src/
│   ├── blockchain/      # Core blockchain implementation
│   ├── networking/      # P2P networking code
│   ├── wallet/          # Wallet implementation
│   ├── explorer/        # Block explorer
│   └── sdk/            # Python SDK
├── tests/              # Test files
├── docs/              # Documentation
└── examples/          # Example code
```

## Development Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src tests/

# Run specific test file
pytest tests/test_blockchain.py
```

## Code Review Process

1. The maintainers look at Pull Requests on a regular basis.
2. After feedback has been given we expect responses within two weeks.
3. After two weeks we may close the PR if it isn't showing any activity.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/BronzonTech-Cloud/vernachain/tags).

## License

By contributing, you agree that your contributions will be licensed under its MIT License. 