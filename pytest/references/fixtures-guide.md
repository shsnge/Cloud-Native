# pytest Fixtures Guide

## Fixture Basics

### Defining Fixtures

```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "test", "value": 42}

def test_with_fixture(sample_data):
    assert sample_data["value"] == 42
```

### Fixture with Setup/Teardown

```python
@pytest.fixture
def database():
    # Setup
    db = Database(":memory:")
    db.create_tables()

    yield db

    # Teardown
    db.close()
```

## Fixture Scopes

### Function Scope (Default)

```python
@pytest.fixture
def temp_file():
    """Created for each test function"""
    with NamedTemporaryFile() as f:
        yield f

def test_a(temp_file):
    ...  # Gets fresh temp_file

def test_b(temp_file):
    ...  # Gets different temp_file
```

### Module Scope

```python
@pytest.fixture(scope="module")
def shared_resource():
    """Created once per module"""
    resource = Resource()
    yield resource
    resource.cleanup()
```

### Class Scope

```python
@pytest.fixture(scope="class")
def class_resource():
    """Created once per test class"""
    resource = Resource()
    yield resource
    resource.cleanup()

class TestGroup:
    def test_one(self, class_resource):
        ...

    def test_two(self, class_resource):
        ...  # Same resource as test_one
```

### Session Scope

```python
@pytest.fixture(scope="session")
def database():
    """Created once per test session"""
    db = connect_to_test_db()
    yield db
    db.disconnect()
```

## Built-in Fixtures

### tmp_path - Temporary Directory

```python
def test_with_temp_dir(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("content")
    assert file.read_text() == "content"
```

### tmp_path_factory - Session-wide Temp Directory

```python
@pytest.fixture(scope="session")
def shared_temp_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("shared")
```

### capsys - Capture stdout/stderr

```python
def test_print_output(capsys):
    print("hello")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"
```

### capfd - Capture file descriptors

```python
def test_fd_output(capfd):
    os.write(1, b"hello")
    out, err = capfd.readouterr()
    assert out == "hello"
```

### monkeypatch - Modify Objects/Environment

```python
def test_with_mock(monkeypatch):
    def mock_return():
        return 42

    monkeypatch.setattr("module.function", mock_return)
    assert module.function() == 42
```

Environment variables:

```python
def test_env_var(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    assert os.getenv("API_KEY") == "test-key"
```

Sys.path modification:

```python
def test_sys_path(monkeypatch):
    monkeypatch.syspath_prepend("/extra/path")
```

## Fixture Parametrization

### Single Value

```python
@pytest.fixture(params=["value1", "value2", "value3"])
def sample(request):
    return request.param

def test_with_params(sample):
    # Runs 3 times, once for each param
    assert sample in ["value1", "value2", "value3"]
```

### With IDs

```python
@pytest.fixture(
    params=[
        ("user", "pass"),
        ("admin", "admin"),
    ],
    ids=["user-login", "admin-login"]
)
def credentials(request):
    return request.param
```

## Fixture Composition

### Chaining Fixtures

```python
@pytest.fixture
def database():
    return Database(":memory:")

@pytest.fixture
def session(database):
    return database.create_session()

@pytest.fixture
def user(session):
    return session.create_user("test")

def test_user_actions(user):
    # user fixture uses session, which uses database
    assert user.name == "test"
```

### Optional Fixtures

```python
@pytest.fixture
def opt_config(request):
    if request.config.getoption("--config"):
        return load_config(request.config.getoption("--config"))
    return default_config()
```

## Conftest.py - Shared Fixtures

### Directory Structure

```
tests/
├── conftest.py          # Shared by all tests
├── unit/
│   └── conftest.py      # Shared by unit tests only
└── integration/
    └── conftest.py      # Shared by integration tests only
```

### Example conftest.py

```python
import pytest

@pytest.fixture
def test_database():
    """Available to all tests"""
    db = Database(":memory:")
    yield db
    db.close()

@pytest.fixture(scope="session")
def api_client():
    """Available to all tests, created once"""
    return APIClient()

def pytest_configure(config):
    """Hook called before test session"""
    config.addinivalue_line("markers", "slow: slow tests")
```

## Autouse Fixtures

Run automatically without requesting:

```python
@pytest.fixture(autouse=True)
def reset_state():
    """Runs before every test"""
    setup_state()
    yield
    cleanup_state()

# No need to request - runs automatically
def test_anything():
    ...
```

## Common Patterns

### Database Fixtures

```python
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

### HTTP Client Fixtures

```python
@pytest.fixture
def http_client():
    client = TestClient(app)
    return client

@pytest.fixture
def authenticated_client(http_client):
    http_client.login("user", "pass")
    return http_client
```

### Mock Time

```python
@pytest.fixture
def frozen_time(monkeypatch):
    frozen = datetime(2024, 1, 1)
    monkeypatch.setattr("datetime.datetime", lambda *args, **kw: frozen)
    return frozen
```

### Clean Directory

```python
@pytest.fixture
def clean_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path
```

## Advanced Fixture Features

### Indirect Parametrization

```python
@pytest.fixture
def database(request):
    param = request.param
    return Database(param)

@pytest.mark.parametrize("database", [":memory:", "test.db"], indirect=True)
def test_with_databases(database):
    assert database.is_connected()
```

### Fixture Factory

```python
@pytest.fixture
def make_user():
    def _make_user(name="test", admin=False):
        return User(name=name, is_admin=admin)
    return _make_user

def test_with_factory(make_user):
    admin = make_user("admin", admin=True)
    user = make_user("user")
    assert admin.is_admin
    assert not user.is_admin
```

### Conditional Skip

```python
@pytest.fixture
def remote_resource():
    try:
        resource = connect_to_remote()
    except ConnectionError:
        pytest.skip("Remote unavailable")
    yield resource
```

## Fixture Troubleshooting

### Fixture Not Found

Ensure the fixture is:
1. In `conftest.py` or the same module
2. Defined with `@pytest.fixture`
3. In the correct scope (directory)

### Fixture Loop

Avoid circular dependencies:

```python
# Bad: circular
@pytest.fixture
def a(b):
    ...

@pytest.fixture
def b(a):
    ...

# Good: extract common
@pytest.fixture
def common():
    ...

@pytest.fixture
def a(common):
    ...

@pytest.fixture
def b(common):
    ...
```
