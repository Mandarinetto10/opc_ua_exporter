## Testing

### Overview

The project includes a **comprehensive test suite with 100% code coverage** for all critical modules. Tests are organized using pytest with async support, extensive mocking, and detailed coverage reporting.

### Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared pytest fixtures (mocks, sample data)
├── test_browser.py             # Browser module tests (100% coverage)
├── test_client.py              # Client connection tests (96% coverage)
├── test_models.py              # Data models tests (100% coverage)
├── test_strategies.py          # Export strategies tests (100% coverage)
├── test_exporter.py            # Export context tests (94% coverage)
├── test_cli.py                 # CLI interface tests (90% coverage)
├── test_generate_cert.py       # Certificate generation tests (97% coverage)
└── test_integration.py         # Integration tests with real OPC UA server (optional)
```

### Quick Start Testing

```bash
# Install test dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests with coverage - Complete test suite
pytest

# Run all tests with verbose output and detailed coverage
pytest -v --cov=src/opc_browser --cov-report=term-missing --cov-report=html --cov-branch

# Run tests and open HTML coverage report in browser
pytest --cov-report=html && open htmlcov/index.html  # macOS
pytest --cov-report=html && start htmlcov/index.html  # Windows
pytest --cov-report=html && xdg-open htmlcov/index.html  # Linux
```

### Running Tests - Basic Commands

#### Single-Line Test Execution Examples

```bash
# Complete test suite with coverage report
pytest -v --cov=src/opc_browser --cov-report=term-missing --cov-branch

# All unit tests (skip integration) with HTML coverage
pytest -v -m "not integration" --cov=src/opc_browser --cov-report=html --cov-report=term-missing

# Full test suite with XML + HTML + terminal coverage
pytest -v --cov=src/opc_browser --cov-report=xml --cov-report=html --cov-report=term-missing --cov-branch

# Quick test run (no coverage, just pass/fail)
pytest -v --no-cov -x

# Verbose tests with short traceback on failure
pytest -v --tb=short --cov-report=term-missing

# Run tests and show slowest 10 tests
pytest -v --durations=10 --cov-report=term-missing

# Parallel test execution (requires pytest-xdist)
pytest -v -n auto --cov=src/opc_browser --cov-report=html

# Watch mode - rerun tests on file changes (requires pytest-watch)
ptw -- -v --cov=src/opc_browser --cov-report=term-missing
```

#### Standard Testing Commands

```bash
# Run all tests
pytest

# Run all tests with verbose output
pytest -v

# Run tests with detailed coverage report
pytest --cov=src/opc_browser --cov-report=term-missing

# Run specific test file
pytest tests/test_browser.py

# Run only unit tests (skip integration tests)
pytest -m "not integration"

# Run only integration tests (requires OPC UA server)
pytest -m integration

# Run specific test class
pytest tests/test_browser.py::TestBrowseOperation

# Run specific test function
pytest tests/test_browser.py::TestBrowseOperation::test_browse_success

# Run tests matching pattern
pytest -k "test_browse"

# Run only async tests
pytest -m asyncio

# Skip slow tests
pytest -m "not slow"

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Quiet mode (less output)
pytest -q
```

### Coverage Reports

#### Generate Different Coverage Report Types

```bash
# Terminal report with missing lines
pytest --cov-report=term-missing

# HTML coverage report (open in browser)
pytest --cov-report=html
# Then open: htmlcov/index.html

# XML coverage report (for CI/CD, Codecov, SonarQube)
pytest --cov-report=xml

# Generate all report types at once
pytest --cov-report=term-missing --cov-report=html --cov-report=xml

# Coverage with branch analysis
pytest --cov-branch --cov-report=term-missing

# Detailed coverage with annotated source
pytest --cov-report=annotate

# Run without coverage (faster for debugging)
pytest --no-cov
```

### Module-Specific Testing

#### Test Individual Modules

```bash
# Browser module only
pytest tests/test_browser.py -v --cov=src/opc_browser/browser.py --cov-report=term-missing

# Client module only
pytest tests/test_client.py -v --cov=src/opc_browser/client.py --cov-report=term-missing

# All export strategies
pytest tests/test_strategies.py -v --cov=src/opc_browser/strategies --cov-report=term-missing

# Models data classes
pytest tests/test_models.py -v --cov=src/opc_browser/models.py --cov-report=term-missing

# CLI interface
pytest tests/test_cli.py -v --cov=src/opc_browser/cli.py --cov-report=term-missing

# Certificate generation
pytest tests/test_generate_cert.py -v --cov=src/opc_browser/generate_cert.py --cov-report=term-missing

# Exporter context
pytest tests/test_exporter.py -v --cov=src/opc_browser/exporter.py --cov-report=term-missing
```

### Integration Tests

Integration tests verify functionality against a **real OPC UA server** running on `opc.tcp://localhost:4840`.

#### Setup for Integration Tests

1. **Start OPC UA server** on default port 4840
2. **Verify server is running:**
   ```bash
   # Test server connectivity
   python -c "import asyncio; from asyncua import Client; asyncio.run(Client('opc.tcp://localhost:4840').connect())"
   ```
3. **Run integration tests:**
   ```bash
   pytest -m integration -v
   ```

#### Available Integration Tests

```bash
# Run ALL integration tests with coverage
pytest -m integration -v --cov=src/opc_browser --cov-report=term-missing

# Test basic browse operation
pytest tests/test_integration.py::test_real_browse_basic -v

# Test browse with value reading
pytest tests/test_integration.py::test_real_browse_with_values -v

# Test custom starting node
pytest tests/test_integration.py::test_real_browse_custom_node -v

# Test namespace filtering
pytest tests/test_integration.py::test_real_namespaces_only_filter -v

# Test deep browsing (max_depth=5)
pytest tests/test_integration.py::test_real_deep_browse -v

# Test full attribute export
pytest tests/test_integration.py::test_real_full_export_attributes -v

# Test connection lifecycle
pytest tests/test_integration.py::test_real_client_connection_lifecycle -v

# Test error handling
pytest tests/test_integration.py::test_real_invalid_node_id -v

# Run all integration tests in parallel (faster)
pytest -m integration -n auto -v
```

#### Integration Test Output Example

```bash
$ pytest -m integration -v --cov-report=term-missing

========================= test session starts ==========================
platform linux -- Python 3.10.12, pytest-7.4.3, pluggy-1.3.0
cachedir: .pytest_cache
rootdir: /home/user/opc_ua_exporter
configfile: pyproject.toml
plugins: asyncio-0.21.1, cov-4.1.0
collected 8 items / 199 deselected / 8 selected

tests/test_integration.py::test_real_browse_basic PASSED           [12%]
tests/test_integration.py::test_real_browse_with_values PASSED     [25%]
tests/test_integration.py::test_real_browse_custom_node PASSED     [37%]
tests/test_integration.py::test_real_namespaces_only_filter PASSED [50%]
tests/test_integration.py::test_real_deep_browse PASSED            [62%]
tests/test_integration.py::test_real_full_export_attributes PASSED [75%]
tests/test_integration.py::test_real_client_connection_lifecycle PASSED [87%]
tests/test_integration.py::test_real_invalid_node_id PASSED        [100%]

========================== 8 passed in 12.34s ==========================
```

#### No Server Available?

If no OPC UA server is running, integration tests are **automatically skipped**:

```bash
$ pytest -m integration -v

tests/test_integration.py::test_real_browse_basic SKIPPED          [12%]
reason: OPC UA server not available on localhost:4840

========================== 8 skipped in 0.12s ==========================
```

**This is expected behavior** - integration tests never fail due to missing server.

### Code Quality Tools

#### Linting with Ruff

```bash
# Check all code quality issues
ruff check src/ tests/

# Check and auto-fix safe issues
ruff check --fix src/ tests/

# Check and auto-fix including unsafe fixes
ruff check --unsafe-fixes --fix src/ tests/

# Check specific file
ruff check src/opc_browser/browser.py

# Show all violations with full details
ruff check --output-format=full src/ tests/

# Check only specific rules (e.g., imports)
ruff check --select I src/

# Complete quality check with auto-fix and verbose output
ruff check src/ tests/ --unsafe-fixes --fix --output-format=full
```

#### Formatting with Black

```bash
# Check if code needs formatting
black --check src/ tests/

# Apply formatting to all files
black src/ tests/

# Format specific file
black src/opc_browser/browser.py

# Show diff without applying changes
black --diff src/

# Format with verbose output
black -v src/ tests/

# Complete format check and application
black --check src/ tests/
black src/ tests/
```

#### Type Checking with MyPy

```bash
# Run type checking on source code
mypy src/

# Type check specific module
mypy src/opc_browser/browser.py

# Strict mode type checking
mypy --strict src/

# Type check with error summary
mypy src/ --error-summary

# Generate HTML type coverage report
mypy src/ --html-report mypy_report/

# Check without errors on missing imports
mypy src/ --ignore-missing-imports

# Complete type check with all reports
mypy src/ --ignore-missing-imports --html-report mypy_report/ --any-exprs-report mypy_coverage/
```

### Complete Quality Check Pipeline

Run all quality checks in one command (CI/CD simulation):

```bash
# Full quality check pipeline
pytest -v --cov=src/opc_browser --cov-report=term-missing --cov-report=html --cov-branch && \
ruff check src/ tests/ --output-format=full && \
black --check src/ tests/ && \
mypy src/ --ignore-missing-imports

# OR with auto-fix for linting and formatting
pytest -v --cov=src/opc_browser --cov-report=html && \
ruff check --fix src/ tests/ && \
black src/ tests/ && \
mypy src/
```

### Continuous Integration (CI/CD)

The project uses **GitHub Actions** for automated testing on every push and pull request.

#### CI Workflow Coverage

| Workflow | Python Versions | Operating Systems | What It Tests |
|----------|----------------|-------------------|---------------|
| **Tests** | 3.10, 3.11, 3.12 | Ubuntu, Windows, macOS | Unit tests, coverage, branch coverage |
| **Code Quality** | 3.10 | Ubuntu | Ruff linting, Black formatting |
| **Type Check** | 3.10, 3.11, 3.12 | Ubuntu | MyPy type checking (normal + strict) |

#### Viewing CI Results

1. **Go to GitHub repository**
2. **Click "Actions" tab**
3. **View workflow runs:**
   - ✅ Green checkmark = All tests passed
   - ❌ Red X = Tests failed (click for details)
   - 🟡 Yellow dot = In progress

#### Running CI Tests Locally

Simulate GitHub Actions environment:

```bash
# Run tests as CI would (Python 3.10, Ubuntu)
pytest -v --cov=src/opc_browser --cov-report=xml --cov-branch -m "not integration"

# Check Python version matches CI (3.10)
python --version

# Install exact dependencies from requirements.txt
pip install -r requirements.txt --force-reinstall
```

### Writing New Tests

#### Example: Testing a New Feature

```python
# filepath: tests/test_my_feature.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from opc_browser.browser import OpcUaBrowser


@pytest.mark.asyncio
async def test_my_new_feature(mock_client):
    """Test description with expected behavior."""
    # Arrange - Set up test data and mocks
    browser = OpcUaBrowser(client=mock_client)
    mock_client.get_namespace_array = AsyncMock(return_value=["http://opcfoundation.org/UA/"])
    
    # Act - Execute the feature being tested
    result = await browser.my_new_method()
    
    # Assert - Verify expected outcomes
    assert result.success is True
    assert result.total_nodes > 0
    mock_client.get_namespace_array.assert_called_once()
```

#### Using Fixtures

```python
# Reuse existing fixtures from conftest.py
def test_with_multiple_fixtures(mock_client, mock_node, mock_variable_node, sample_result):
    """Tests can combine multiple fixtures."""
    browser = OpcUaBrowser(client=mock_client)
    # Test implementation with pre-configured mocks
```

#### Async Test Best Practices

```python
@pytest.mark.asyncio
async def test_async_operation(mock_client):
    """Always mark async tests with @pytest.mark.asyncio."""
    # Create async mocks for async methods
    mock_node = AsyncMock()
    mock_node.read_browse_name = AsyncMock(return_value=browse_name)
    
    # Await all async calls
    result = await browser.browse(start_node_id="i=84")
    
    # Await mock verification
    await mock_node.read_browse_name()
    
    # Assertions
    assert result.success is True
```

### Troubleshooting Tests

#### Common Issues and Solutions

**Issue: AsyncIO warnings about unawaited coroutines**
```python
# ❌ Problem
mock_node.get_children()  # Missing await

# ✅ Solution
await mock_node.get_children()
mock_node.get_children = AsyncMock(return_value=[])
await mock_node.get_children()
```

**Issue: Loguru output not captured in tests**
```python
# ✅ Solution: Reconfigure loguru for tests (in conftest.py)
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, format="{message}", level="INFO", colorize=False)
```

**Issue: Coverage not showing 100% despite all tests passing**
```bash
# Check which lines are missing
pytest --cov-report=term-missing

# View detailed HTML report
pytest --cov-report=html
open htmlcov/index.html

# Check branch coverage
pytest --cov-branch --cov-report=term-missing
```

**Issue: Tests passing locally but failing in CI**
```bash
# Run tests exactly as CI does
pytest -v --cov=src/opc_browser --cov-report=xml --cov-branch -m "not integration"

# Check Python version matches CI (3.10)
python --version

# Install exact dependencies from requirements.txt
pip install -r requirements.txt --force-reinstall
```

**Issue: Integration tests failing**
```bash
# Verify OPC UA server is running
python -c "import asyncio; from asyncua import Client; asyncio.run(Client('opc.tcp://localhost:4840').connect())"

# Check server logs for connection errors
# Ensure server allows anonymous or test user connections
# Verify firewall isn't blocking port 4840
```

### Performance Testing

```bash
# Show 10 slowest tests
pytest --durations=10

# Show all test durations
pytest --durations=0

# Run only fast tests (skip slow ones)
pytest -m "not slow"

# Profile test execution
pytest --profile

# Benchmark specific test
pytest tests/test_browser.py::test_browse_deep -v --benchmark
```

### Test Reports

#### Generate Test Reports for Documentation

```bash
# JUnit XML report (for CI/CD integration)
pytest --junitxml=test-results.xml

# HTML test report (human-readable)
pytest --html=test-report.html --self-contained-html

# Combined coverage + test report
pytest --cov=src_opc_browser --cov-report=html --html=test-report.html
```

---

