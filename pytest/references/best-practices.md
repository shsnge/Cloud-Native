# pytest Best Practices

## Test Organization

### Directory Structure

```
project/
├── src/
│   └── mymodule/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
└── pytest.ini
```

### File Naming

- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*`
- Test functions: `test_*`

## Test Design

### AAA Pattern (Arrange-Act-Assert)

```python
def test_user_creation():
    # Arrange
    username = "testuser"
    email = "test@example.com"

    # Act
    user = create_user(username, email)

    # Assert
    assert user.username == username
    assert user.email == email
    assert user.id is not None
```

### Descriptive Test Names

```python
# Good: descriptive
def test_login_with_invalid_credentials_returns_401():
    ...

def test_checkout_with_empty_cart_raises_error():
    ...

# Avoid: vague
def test_login():
    ...

def test_it_works():
    ...
```

### Test Independence

Each test should be runnable in isolation:

```python
# Bad: tests depend on execution order
def test_step_1_create_user():
    global user_id
    user_id = create_user("test")

def test_step_2_delete_user():
    delete_user(user_id)  # Fails if run alone

# Good: each test is independent
def test_create_user():
    user = create_user("test")
    assert user.id is not None

def test_delete_user():
    user = create_user("test")
    result = delete_user(user.id)
    assert result is True
```

## Fixture Best Practices

### Scope Appropriately

```python
# Fast: function scope (default)
@pytest.fixture
def temp_file():
    with NamedTemporaryFile() as f:
        yield f

# Medium: module scope
@pytest.fixture(scope="module")
def database():
    db = Database(":memory:")
    yield db
    db.close()

# Slow: session scope (use sparingly)
@pytest.fixture(scope="session")
def api_client():
    return APIClient()
```

### Fixture Composition

```python
@pytest.fixture
def user():
    return User(name="test")

@pytest.fixture
def admin_user(user):
    user.is_admin = True
    return user

def test_admin_action(admin_user):
    assert admin_user.is_admin
```

## Assertion Patterns

### Specific Assertions

```python
# Good: specific
assert response.status_code == 200
assert user.age >= 18
assert "error" not in result

# Avoid: generic truthiness
assert response
assert user
assert result
```

### Comparison with Tolerance

```python
# For floating point
assert abs(result - expected) < 0.001

# Or use pytest's approx
assert result == pytest.approx(expected, abs=0.001)
```

### Exception Testing

```python
def test_invalid_input_raises_error():
    with pytest.raises(ValueError, match="must be positive"):
        process(-1)

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        open("nonexistent.txt")
```

## Markers

### Define Markers

In `pytest.ini`:

```ini
[pytest]
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    network: marks tests that require network access
    unit: marks tests as unit tests
```

### Use Markers

```python
import pytest

@pytest.mark.slow
def test_long_running_operation():
    ...

@pytest.mark.integration
def test_database_integration():
    ...

@pytest.mark.unit
def test_pure_function():
    ...
```

### Run Marked Tests

```bash
pytest -m unit              # Only unit tests
pytest -m "not slow"        # Everything except slow
pytest -m "network and integration"  # Both markers
```

## Parametrization

### Data-Driven Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected
```

### Parametrize with IDs

```python
@pytest.mark.parametrize("input,expected", [
    ("valid@email.com", True),
    ("invalid", False),
    ("@missing.com", False),
], ids=["valid", "no_at", "no_user"])
def test_email_validation(input, expected):
    assert is_valid_email(input) == expected
```

## Test Configuration

### Minimal pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
```

### With Markers and Coverage

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=src
    --cov-report=term-missing
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

## Avoid Common Pitfalls

### Don't Use assert in try/except

```python
# Bad: swallows assertion errors
try:
    assert x == y
except AssertionError:
    pass

# Good: let pytest handle it
assert x == y
```

### Don't Catch Generic Exceptions

```python
# Bad: hides errors
try:
    result = risky_operation()
except:
    result = None

# Good: be specific or let it fail
try:
    result = risky_operation()
except ValueError:
    result = None
```

### Don't Modify Global State

```python
# Bad: affects other tests
def test_sets_global():
    global CONFIG
    CONFIG["debug"] = True

# Good: use fixtures or monkeypatch
def test_with_config(monkeypatch):
    monkeypatch.setitem(CONFIG, "debug", True)
```
