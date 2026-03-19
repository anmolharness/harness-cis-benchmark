# Test Suite

Comprehensive unit and integration tests for the Harness CIS Benchmark tool.

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
# Test data collector
pytest tests/test_data_collector.py

# Test database
pytest tests/test_database.py

# Test check functions
pytest tests/test_harness_platform_optimized.py

# Test dashboard API
pytest tests/test_dashboard.py

# Test Harness API wrapper
pytest tests/test_harness_api.py
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Coverage Report

```bash
# Generate coverage report
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Verbose Output

```bash
pytest -v
```

## Test Structure

```
tests/
├── __init__.py                          # Test package
├── conftest.py                          # Shared fixtures
├── test_data_collector.py               # Data collector tests
├── test_database.py                     # Database persistence tests
├── test_harness_platform_optimized.py   # Check function tests
├── test_dashboard.py                    # Flask API tests
└── test_harness_api.py                  # API wrapper tests
```

## Test Coverage

- **data_collector.py**: Data fetching, caching, error handling
- **database.py**: SQLite operations, remediation tracking, scan history
- **harness_platform_optimized.py**: All 41 check functions
- **dashboard.py**: Flask routes, API endpoints, error handling
- **harness_api.py**: API calls, fallback endpoints, pagination

## Writing New Tests

### Adding a New Test

1. Create test file in `tests/` directory
2. Import required fixtures from `conftest.py`
3. Use `@pytest.mark.unit` or `@pytest.mark.integration` markers
4. Follow naming convention: `test_<functionality>.py`

### Example Test

```python
import pytest

@pytest.mark.unit
def test_example_function(mock_api_key):
    """Test description."""
    # Arrange
    expected = "result"

    # Act
    result = some_function(mock_api_key)

    # Assert
    assert result == expected
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Scheduled nightly builds

## Troubleshooting

### Import Errors

Ensure you're running from the project root:
```bash
cd /path/to/harness-cis-benchmark
pytest
```

### Mock API Errors

Check that `responses` library is installed:
```bash
pip install responses
```

### Database Lock Errors

Tests use temporary databases. If locks occur:
```bash
rm -f *.db
pytest
```
