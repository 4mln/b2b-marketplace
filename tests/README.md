# B2B Marketplace Tests

This directory contains tests for the B2B Marketplace application. The tests are written using pytest and are organized by functionality.

## Test Structure

- `conftest.py`: Contains pytest fixtures and configuration
- `test_auth.py`: Tests for authentication functionality
- `test_orders.py`: Tests for order management
- `test_products.py`: Tests for product management

## Running Tests

To run all tests:

```bash
pytest
```

To run specific test files:

```bash
pytest tests/test_auth.py
pytest tests/test_orders.py
pytest tests/test_products.py
```

To run tests with specific markers:

```bash
pytest -m unit
pytest -m integration
pytest -m api
```

To run tests with verbose output:

```bash
pytest -v
```

## Test Database

The tests use a separate test database (`test_b2b_marketplace`) to avoid affecting the production database. The test database is created and dropped automatically during test execution.

## Authentication

Many tests require authentication. The `auth_headers` fixture in `conftest.py` provides the necessary authentication headers for test requests.

## Adding New Tests

When adding new tests:

1. Create a new test file in the `tests` directory with the prefix `test_`
2. Use the appropriate fixtures from `conftest.py`
3. Use pytest markers to categorize tests (unit, integration, api)
4. Follow the existing test patterns for consistency