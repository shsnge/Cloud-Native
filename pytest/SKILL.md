---
name: pytest
description: Python testing framework for writing small, readable tests that scale to complex functional testing. Use when Claude needs to: (1) Generate pytest test code from source code or requirements, (2) Run pytest and interpret results, (3) Debug failing tests with detailed assertion introspection, (4) Create and manage fixtures and parametrized tests, (5) Set up pytest configuration and project structure, (6) Apply pytest best practices and patterns, or (7) Integrate pytest with CI/CD pipelines.
---

# pytest

Comprehensive testing framework for Python that enables writing simple unit tests and complex functional tests with minimal boilerplate.

## Quick Start

### Generate Tests from Code

Use the test generator script to scaffold tests:

```bash
python scripts/generate_test.py <source_file> --output tests/
```

### Run Tests

Execute pytest with standard options:

```bash
python scripts/run_pytest.py
```

With specific options:

```bash
python scripts/run_pytest.py --verbose --cov
```

### Test Coverage

Generate coverage reports:

```bash
python scripts/coverage_report.py --html
```

## Writing Tests

### Basic Structure

Tests are functions starting with `test_`:

```python
def test_function_name():
    result = function_under_test(input)
    assert result == expected
```

### Use Assets

Copy templates for quick setup:

- `assets/test_template.py` - New test file template
- `assets/conftest_template.py` - Shared fixtures template
- `assets/pytest.ini` - Configuration template

## Fixtures

Use fixtures for test dependencies:

```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

See `references/fixtures-guide.md` for patterns including:
- Session/module/class scoped fixtures
- Fixture parametrization
- Fixture composition and dependency injection
- Built-in fixtures (tmp_path, capsys, monkeypatch)

## Parametrization

Run tests with multiple inputs:

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert double(input) == expected
```

## Assertions

Use plain `assert` - pytest provides detailed introspection:

```python
assert x == y  # Shows: assert 3 == 5
```

See `references/assertions.md` for:
- Assertion patterns
- Approximate comparisons
- Exception testing with `pytest.raises()`
- Warning testing with `pytest.warns()`

## Best Practices

For production-quality tests, see `references/best-practices.md`:
- Test isolation and independence
- Descriptive test names
- Arrangement-Act-Assert (AAA) pattern
- Avoiding test interdependence
- Effective fixture usage

## Running Tests

### Discovery

pytest automatically discovers:
- Files named `test_*.py` or `*_test.py`
- Functions/classes starting with `test_`

### Common Options

```bash
# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run specific test
pytest tests/test_module.py::test_function

# Run by keyword expression
pytest -k "test_login"

# Show print output
pytest -s
```

## Markers

Organize tests with markers:

```python
@pytest.mark.slow
def test_slow_operation():
    ...

@pytest.mark.integration
def test_database():
    ...
```

Run marked tests:

```bash
pytest -m slow
pytest -m "not slow"
```

## Configuration

Configure pytest in `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

## Troubleshooting Failing Tests

When tests fail, leverage pytest's introspection:

1. **Assertion errors**: pytest shows the exact values
2. **Import errors**: Check `PYTHONPATH` and `conftest.py`
3. **Fixture errors**: Verify fixture scope and dependencies
4. **Collection errors**: Ensure test discovery patterns match

Use `--pdb` to drop into debugger on failure:

```bash
pytest --pdb
```

## References

For detailed information, see:
- `references/fixtures-guide.md` - Complete fixture patterns
- `references/assertions.md` - Assertion techniques
- `references/best-practices.md` - Production test patterns
