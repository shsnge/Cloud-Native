# pytest Assertions Guide

## Basic Assertions

### Simple Comparisons

```python
def test_equality():
    assert 1 + 1 == 2
    assert "hello" == "hello"
    assert [1, 2, 3] == [1, 2, 3]

def test_inequality():
    assert 1 != 2
    assert "hello" != "world"

def test_ordering():
    assert 1 < 2
    assert 2 <= 2
    assert 3 > 2
    assert 3 >= 3

def test_membership():
    assert 1 in [1, 2, 3]
    assert "key" in {"key": "value"}
    assert "x" not in "abc"
```

### Boolean Assertions

```python
def test_truthiness():
    assert True
    assert "text"  # Non-empty strings are truthy
    assert [1]     # Non-empty lists are truthy
    assert {"a": 1}  # Non-empty dicts are truthy

def test_falsiness():
    assert not False
    assert not ""      # Empty strings are falsy
    assert not []      # Empty lists are falsy
    assert not {}      # Empty dicts are falsy
    assert not None
```

### Identity Assertions

```python
def test_identity():
    a = [1, 2, 3]
    b = a
    assert a is b

    c = [1, 2, 3]
    assert a is not c  # Same content, different objects
    assert a == c      # Same content
```

## Exception Testing

### pytest.raises()

```python
def test_raises_exception():
    with pytest.raises(ValueError):
        raise ValueError("error message")

def test_exception_message():
    with pytest.raises(ValueError, match="must be positive"):
        process(-1)

def test_exception_attributes():
    with pytest.raises(ValueError) as exc_info:
        raise ValueError("error code: 42")

    assert "error code: 42" in str(exc_info.value)
    assert exc_info.type is ValueError
```

### Specific Exception Type

```python
def test_specific_exception():
    with pytest.raises(ValueError):
        int("not a number")

def test_exception_hierarchy():
    with pytest.raises(Exception):  # Catches any Exception
        raise ValueError("error")
```

### No Exception

```python
def test_no_exception():
    # If no exception is raised, test passes
    calculate(1, 2)  # Should not raise
```

## Warning Testing

### pytest.warns()

```python
def test_warning():
    with pytest.warns(UserWarning):
        deprecated_function()

def test_warning_message():
    with pytest.warns(UserWarning, match="deprecated"):
        deprecated_function()
```

## Approximate Comparisons

### pytest.approx()

```python
def test_float_approximation():
    result = 0.1 + 0.2
    assert result == pytest.approx(0.3)

def test_with_tolerance():
    assert 3.149 == pytest.approx(3.15, abs=0.01)
    assert 3.14 == pytest.approx(3.15, rel=0.01)

def test_sequence_approximation():
    assert [0.1 + 0.2, 0.3 + 0.4] == pytest.approx([0.3, 0.7])

def test_dict_approximation():
    assert {"a": 0.1 + 0.2, "b": 0.3} == pytest.approx({"a": 0.3, "b": 0.3})
```

## Custom Assertions

### Assertion with Context

```python
def test_with_custom_message():
    age = 15
    assert age >= 18, f"User must be 18+, got {age}"
```

### Multiple Assertions

```python
def test_user_attributes(user):
    assert user.name == "test"
    assert user.email == "test@example.com"
    assert user.age >= 18
```

### Grouped Assertions

```python
def test_response_schema(response):
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "created_at" in data
```

## Collection Assertions

### List Contents

```python
def test_list_contents():
    items = [1, 2, 3, 4, 5]

    assert len(items) == 5
    assert 3 in items
    assert items[0] == 1
    assert items[-1] == 5
```

### All/Any

```python
def test_all():
    numbers = [2, 4, 6, 8]
    assert all(n % 2 == 0 for n in numbers)

def test_any():
    values = [1, 2, 3, 4]
    assert any(v > 3 for v in values)
```

### List Ordering

```python
def test_sorted():
    items = [1, 2, 3]
    assert items == sorted(items)

def test_unsorted():
    items = [3, 1, 2]
    assert items != sorted(items)
```

## Dictionary Assertions

### Key Existence

```python
def test_dict_keys():
    data = {"name": "test", "age": 30}

    assert "name" in data
    assert "email" not in data
    assert set(data.keys()) >= {"name", "age"}
```

### Values

```python
def test_dict_values():
    data = {"name": "test", "age": 30}

    assert data["name"] == "test"
    assert data.get("age") == 30
    assert data.get("email", "default") == "default"
```

### Schema Validation

```python
def test_dict_schema():
    response = {
        "id": 1,
        "name": "test",
        "active": True,
    }

    assert isinstance(response["id"], int)
    assert isinstance(response["name"], str)
    assert isinstance(response["active"], bool)
```

## String Assertions

### Substring

```python
def test_substring():
    text = "Hello, World!"
    assert "World" in text
    assert "world" not in text  # Case sensitive
```

### Prefix/Suffix

```python
def test_prefix_suffix():
    filename = "test_file.txt"

    assert filename.startswith("test_")
    assert filename.endswith(".txt")
```

### Regular Expressions

```python
import re

def test_regex_match():
    email = "user@example.com"
    assert re.match(r"[\w.]+@[\w.]+", email)

def test_regex_in_string():
    text = "Error: code 42"
    assert re.search(r"code \d+", text)
```

## Type Assertions

### isinstance()

```python
def test_types():
    assert isinstance(42, int)
    assert isinstance("hello", str)
    assert isinstance([1, 2], list)
    assert isinstance({"a": 1}, dict)
```

### Type Checking Multiple

```python
def test_multiple_types():
    value = 42
    assert isinstance(value, (int, float))

    text = "hello"
    assert isinstance(text, (str, bytes))
```

## None Assertions

```python
def test_none():
    result = None
    assert result is None

def test_not_none():
    result = "something"
    assert result is not None
```

## Object Comparison

### Custom __eq__

```python
class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __eq__(self, other):
        return self.id == other.id

def test_custom_equality():
    user1 = User(1, "Alice")
    user2 = User(1, "Bob")
    assert user1 == user2  # Same ID
```

### Dataclasses

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

def test_dataclass_equality():
    p1 = Point(1.0, 2.0)
    p2 = Point(1.0, 2.0)
    assert p1 == p2
```

## Assertion Introspection

pytest provides detailed failure messages:

```python
def test_introspection():
    a = {"name": "Alice", "age": 30}
    b = {"name": "Alice", "age": 25}

    # Fails with detailed output showing the difference
    assert a == b
```

Output shows:
```python
assert {'name': 'Alice', 'age': 30} == {'name': 'Alice', 'age': 25}
  At index 1:
  - 30
  + 25
```

## Troubleshooting Assertions

### Assertion Always Passes

```python
# Bad: assert with no comparison
def test_bad():
    assert calculate(1, 2)  # Always passes if no exception

# Good: compare result
def test_good():
    result = calculate(1, 2)
    assert result == 3
```

### Comparing Floats Directly

```python
# Bad: direct float comparison
def test_float_bad():
    assert 0.1 + 0.2 == 0.3  # May fail due to floating point

# Good: use approx
def test_float_good():
    assert 0.1 + 0.2 == pytest.approx(0.3)
```

### Asserting on None

```python
# Bad: truthiness check
def test_none_bad():
    result = None
    assert not result  # Passes for None, "", [], etc.

# Good: explicit check
def test_none_good():
    result = None
    assert result is None
```
