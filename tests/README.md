# Tests for AquaSentinel Backend

## Running Tests

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_dashboard_service.py
pytest tests/test_routes.py
```

### Run with Coverage Report
```bash
pytest --cov=services --cov=routes --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`

## Test Structure

- `test_dashboard_service.py` - Unit tests for DashboardService
- `test_routes.py` - Integration tests for API endpoints

## What's Tested

### DashboardService Tests
- ✅ KPI structure and values
- ✅ Revenue summary calculations
- ✅ AR aging structure
- ✅ Debt metrics structure
- ✅ Revenue trends with different periods
- ✅ Budget variance retrieval
- ✅ Efficiency alerts
- ✅ Scenario planning
- ✅ Caching functionality

### Route Tests
- ✅ All endpoint responses
- ✅ Response structure validation
- ✅ Request ID headers
- ✅ Error handling

## Test Coverage

Run coverage report to see which parts of the code are tested:
```bash
pytest --cov=services --cov=routes --cov-report=term-missing
```


